"""
San Beda Integration Tool - Pull Service
Service for pulling timesheet data from San Beda's timekeeping system
"""

import requests
import logging
from datetime import datetime, timedelta
import json
from urllib.parse import urlencode
from .auth_service import AuthService

logger = logging.getLogger(__name__)


class PullService:
    """Service for pulling data from San Beda timekeeping system"""

    def __init__(self, database):
        self.database = database
        self.auth_service = AuthService(database)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'San Beda Integration Tool/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=UTF-8'
        })

    def get_config(self):
        """Get pull configuration from database"""
        config = self.database.get_api_config()
        if not config:
            raise Exception("API configuration not found")

        if not config.get('pull_host'):
            raise Exception("San Beda host not configured")

        return config

    def test_connection(self):
        """Test connection to San Beda API"""
        try:
            # Test authentication
            return self.auth_service.test_connection()
        except Exception as e:
            logger.error(f"Connection test error: {e}")
            return False, f"Error: {str(e)}"

    def pull_data(self):
        """
        Pull timesheet data from San Beda timekeeping system

        Returns:
            tuple: (success: bool, message: str, stats: dict)
        """
        log_id = self.database.create_sync_log('pull')
        stats = {
            'processed': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

        try:
            logger.info("Starting pull sync from San Beda")

            # Get configuration
            config = self.get_config()
            host = config['pull_host']

            # Get authentication token
            login_token = self.auth_service.get_valid_token()

            # Set token in headers
            self.session.headers['X-Subject-Token'] = login_token

            # Calculate date range (last 7 days if no last_pull_at)
            last_pull = config.get('last_pull_at')
            if last_pull:
                start_time = datetime.fromisoformat(last_pull)
            else:
                start_time = datetime.now() - timedelta(days=7)

            end_time = datetime.now()

            # Format dates for San Beda API (yyyy-MM-dd HH:mm:ss)
            start_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")
            end_time_str = end_time.strftime("%Y-%m-%d %H:%M:%S")

            logger.info(f"Pulling data from {start_time_str} to {end_time_str}")

            # Pull data with pagination
            page = 1
            page_size = 100  # Adjust based on performance
            total_records = 0

            while True:
                logger.info(f"Fetching page {page}...")

                # Build request parameters
                params = {
                    'startTime': start_time_str,
                    'endTime': end_time_str,
                    'personName': '',
                    'personId': '',
                    'deptId': '',
                    'page': page,
                    'pageSize': page_size
                }

                # Build URL
                url = f"http://{host}/brms/api/v1.0/attendance/record-info-report/page?{urlencode(params)}"

                # Make API request
                response = self.session.get(url, timeout=30)

                if response.status_code == 401:
                    # Token expired, re-authenticate
                    logger.warning("Token expired, re-authenticating...")
                    self.auth_service.invalidate_token()
                    login_token = self.auth_service.authenticate()
                    self.session.headers['X-Subject-Token'] = login_token

                    # Retry request
                    response = self.session.get(url, timeout=30)

                if response.status_code != 200:
                    error_msg = f"Pull failed: HTTP {response.status_code} - {response.text}"
                    logger.error(error_msg)
                    self.database.update_sync_log(
                        log_id, 'error', error_message=error_msg
                    )
                    return False, error_msg, stats

                # Parse response
                data = response.json()

                # Check API-level success
                if data.get('code') != 1000:
                    error_msg = f"API Error: {data.get('desc', 'Unknown error')}"
                    logger.error(error_msg)
                    self.database.update_sync_log(
                        log_id, 'error', error_message=error_msg
                    )
                    return False, error_msg, stats

                # Get page data
                page_data = data.get('data', {}).get('pageData', [])

                if not page_data:
                    logger.info(f"No more data on page {page}, stopping pagination")
                    break

                logger.info(f"Processing {len(page_data)} attendance records from page {page}")

                # Process each attendance record
                for attendance in page_data:
                    stats['processed'] += 1
                    try:
                        result = self.process_attendance(attendance)
                        if result == 'success':
                            stats['success'] += 2  # 2 entries per attendance (IN + OUT)
                        elif result == 'skipped':
                            stats['skipped'] += 2
                        else:
                            stats['failed'] += 1
                    except Exception as e:
                        logger.error(f"Error processing attendance {attendance}: {e}")
                        stats['failed'] += 1

                total_records += len(page_data)

                # Check if we should continue pagination
                # San Beda API doesn't provide clear pagination info, so we stop when page is not full
                if len(page_data) < page_size:
                    logger.info("Last page reached")
                    break

                page += 1

            # Update last pull time
            self.database.update_last_sync_time('pull')

            # Update sync log
            self.database.update_sync_log(
                log_id,
                status='success',
                records_processed=stats['processed'],
                records_success=stats['success'],
                records_failed=stats['failed'],
                metadata={'skipped': stats['skipped'], 'total_records': total_records}
            )

            message = f"Pull completed: {stats['success']} records imported ({stats['processed']} attendance records processed)"
            logger.info(message)
            return True, message, stats

        except Exception as e:
            error_msg = f"Pull sync error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.database.update_sync_log(
                log_id, 'error', error_message=error_msg
            )
            return False, error_msg, stats

    def process_attendance(self, attendance_data):
        """
        Process single attendance record from San Beda API
        Creates 2 timesheet entries: one for signInTime, one for signOutTime

        Returns:
            str: 'success', 'skipped', or 'failed'
        """
        try:
            # Extract employee data
            employee_id = attendance_data.get('code')  # Person ID
            employee_name = attendance_data.get('name')
            attendance_date = attendance_data.get('attendanceDate')
            sign_in_time = attendance_data.get('signInTime')
            sign_out_time = attendance_data.get('signOutTime')

            if not all([employee_id, employee_name, attendance_date]):
                logger.warning(f"Missing required fields in attendance data: {attendance_data}")
                return 'failed'

            # First, ensure employee exists
            employee = self.database.get_employee_by_backend_id(int(employee_id))
            if not employee:
                # Create employee
                emp_id = self.database.add_or_update_employee(
                    backend_id=int(employee_id),
                    name=employee_name,
                    employee_code=employee_id,
                    employee_number=None
                )
                employee = {'id': emp_id, 'backend_id': int(employee_id)}
                logger.info(f"Created employee: {employee_name} (ID: {employee_id})")

            # Create IN entry if signInTime exists
            if sign_in_time:
                timestamp_in = datetime.strptime(f"{attendance_date} {sign_in_time}", "%Y-%m-%d %H:%M")
                sync_id_in = f"{employee_id}_{timestamp_in.strftime('%Y%m%d%H%M%S')}_IN"

                result_in = self.database.add_timesheet_entry(
                    sync_id=sync_id_in,
                    employee_id=employee['id'],
                    log_type='in',
                    date=attendance_date,
                    time=sign_in_time,
                    photo_path=None
                )

                if result_in is None:
                    logger.debug(f"IN entry already exists: {sync_id_in}")

            # Create OUT entry if signOutTime exists
            if sign_out_time:
                timestamp_out = datetime.strptime(f"{attendance_date} {sign_out_time}", "%Y-%m-%d %H:%M")
                sync_id_out = f"{employee_id}_{timestamp_out.strftime('%Y%m%d%H%M%S')}_OUT"

                result_out = self.database.add_timesheet_entry(
                    sync_id=sync_id_out,
                    employee_id=employee['id'],
                    log_type='out',
                    date=attendance_date,
                    time=sign_out_time,
                    photo_path=None
                )

                if result_out is None:
                    logger.debug(f"OUT entry already exists: {sync_id_out}")

            return 'success'

        except Exception as e:
            logger.error(f"Error processing attendance: {e}", exc_info=True)
            return 'failed'
