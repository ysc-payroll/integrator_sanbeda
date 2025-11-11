"""
San Beda Integration Tool - Pull Service
Service for pulling timesheet data from San Beda's on-premise system
"""

import requests
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class PullService:
    """Service for pulling data from San Beda on-premise timekeeping system"""

    def __init__(self, database):
        self.database = database
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'San Beda Integration Tool/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def get_config(self):
        """Get pull configuration from database"""
        config = self.database.get_api_config()
        if not config:
            raise Exception("API configuration not found")

        if not config.get('pull_url'):
            raise Exception("Pull URL not configured")

        return config

    def build_auth_headers(self, config):
        """Build authentication headers based on config"""
        headers = {}

        auth_type = config.get('pull_auth_type', '').lower()
        credentials = config.get('pull_credentials')

        if auth_type == 'bearer':
            # Bearer token authentication
            headers['Authorization'] = f'Bearer {credentials}'
        elif auth_type == 'api_key':
            # API key authentication
            headers['X-API-Key'] = credentials
        elif auth_type == 'basic':
            # Basic authentication (credentials should be base64 encoded)
            headers['Authorization'] = f'Basic {credentials}'

        return headers

    def test_connection(self):
        """Test connection to San Beda API"""
        try:
            config = self.get_config()
            headers = self.build_auth_headers(config)

            # Try to ping the endpoint
            response = self.session.get(
                config['pull_url'],
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                return True, "Connection successful"
            elif response.status_code == 401:
                return False, "Authentication failed: Invalid credentials"
            elif response.status_code == 404:
                return False, "Endpoint not found: Check URL"
            else:
                return False, f"Connection failed: HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            return False, "Connection timeout: Server not responding"
        except requests.exceptions.ConnectionError:
            return False, "Connection error: Cannot reach server"
        except Exception as e:
            logger.error(f"Connection test error: {e}")
            return False, f"Error: {str(e)}"

    def pull_data(self):
        """
        Pull timesheet data from San Beda on-premise system

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
            headers = self.build_auth_headers(config)

            # TODO: Customize this based on actual San Beda API
            # Example: You might need to pass date range parameters
            params = {
                'from_date': config.get('last_pull_at'),  # Pull only new data
                'limit': 1000
            }

            # Make API request
            response = self.session.get(
                config['pull_url'],
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code != 200:
                error_msg = f"Pull failed: HTTP {response.status_code}"
                logger.error(error_msg)
                self.database.update_sync_log(
                    log_id, 'error', error_message=error_msg
                )
                return False, error_msg, stats

            # Parse response
            data = response.json()

            # TODO: Adjust this based on actual API response structure
            # Expected structure: {"data": [...], "employees": [...]}
            timesheets = data.get('data', [])
            employees = data.get('employees', [])

            logger.info(f"Received {len(timesheets)} timesheet records")
            logger.info(f"Received {len(employees)} employee records")

            # Process employees first
            for emp_data in employees:
                try:
                    self.process_employee(emp_data)
                except Exception as e:
                    logger.error(f"Error processing employee {emp_data}: {e}")

            # Process timesheets
            for ts_data in timesheets:
                stats['processed'] += 1
                try:
                    if self.process_timesheet(ts_data):
                        stats['success'] += 1
                    else:
                        stats['skipped'] += 1
                except Exception as e:
                    logger.error(f"Error processing timesheet {ts_data}: {e}")
                    stats['failed'] += 1

            # Update last pull time
            self.database.update_last_sync_time('pull')

            # Update sync log
            self.database.update_sync_log(
                log_id,
                status='success',
                records_processed=stats['processed'],
                records_success=stats['success'],
                records_failed=stats['failed'],
                metadata={'skipped': stats['skipped']}
            )

            message = f"Pull completed: {stats['success']} records imported"
            logger.info(message)
            return True, message, stats

        except Exception as e:
            error_msg = f"Pull sync error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.database.update_sync_log(
                log_id, 'error', error_message=error_msg
            )
            return False, error_msg, stats

    def process_employee(self, emp_data):
        """
        Process employee data from API response

        TODO: Adjust field mapping based on actual API response
        Expected fields: id, name, employee_code, employee_number
        """
        self.database.add_or_update_employee(
            backend_id=emp_data['id'],
            name=emp_data['name'],
            employee_code=emp_data.get('employee_code'),
            employee_number=emp_data.get('employee_number')
        )

    def process_timesheet(self, ts_data):
        """
        Process timesheet data from API response

        TODO: Adjust field mapping based on actual API response
        Expected fields: sync_id, employee_id, log_type, date, time, photo_path

        Returns:
            bool: True if added, False if skipped (duplicate)
        """
        # Get or create employee
        employee = self.database.get_employee_by_backend_id(ts_data['employee_id'])
        if not employee:
            logger.warning(f"Employee {ts_data['employee_id']} not found, skipping timesheet")
            return False

        # Add timesheet entry
        result = self.database.add_timesheet_entry(
            sync_id=ts_data['sync_id'],
            employee_id=employee['id'],
            log_type=ts_data['log_type'],
            date=ts_data['date'],
            time=ts_data['time'],
            photo_path=ts_data.get('photo_path')
        )

        return result is not None  # None means duplicate, returns row ID if successful
