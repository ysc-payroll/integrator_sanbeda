"""
San Beda Integration Tool - Push Service
Service for pushing timesheet data to cloud payroll system
"""

import requests
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class PushService:
    """Service for pushing data to cloud payroll system"""

    def __init__(self, database):
        self.database = database
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'San Beda Integration Tool/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })

    def get_config(self):
        """Get push configuration from database"""
        config = self.database.get_api_config()
        if not config:
            raise Exception("API configuration not found")

        if not config.get('push_url'):
            raise Exception("Push URL not configured")

        return config

    def build_auth_headers(self, config):
        """Build authentication headers based on config"""
        headers = {}

        auth_type = config.get('push_auth_type', '').lower()
        credentials = config.get('push_credentials')

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
        """Test connection to cloud payroll API"""
        try:
            config = self.get_config()
            headers = self.build_auth_headers(config)

            # Try to ping the endpoint (might need adjustment based on API)
            response = self.session.get(
                config['push_url'],
                headers=headers,
                timeout=10
            )

            if response.status_code in [200, 201, 204]:
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

    def push_data(self):
        """
        Push unsynced timesheet data to cloud payroll system

        Returns:
            tuple: (success: bool, message: str, stats: dict)
        """
        log_id = self.database.create_sync_log('push')
        stats = {
            'processed': 0,
            'success': 0,
            'failed': 0
        }

        try:
            logger.info("Starting push sync to cloud payroll")

            # Get configuration
            config = self.get_config()
            headers = self.build_auth_headers(config)

            # Get unsynced timesheets
            unsynced = self.database.get_unsynced_timesheets(limit=500)
            logger.info(f"Found {len(unsynced)} unsynced timesheet records")

            if len(unsynced) == 0:
                message = "No records to sync"
                logger.info(message)
                self.database.update_sync_log(
                    log_id, status='success', records_processed=0
                )
                return True, message, stats

            # Process each timesheet
            for timesheet in unsynced:
                stats['processed'] += 1
                try:
                    if self.push_timesheet(timesheet, config, headers):
                        stats['success'] += 1
                    else:
                        stats['failed'] += 1
                except Exception as e:
                    logger.error(f"Error pushing timesheet {timesheet['id']}: {e}")
                    stats['failed'] += 1
                    self.database.mark_timesheet_sync_failed(
                        timesheet['id'],
                        f"Push error: {str(e)}"
                    )

            # Update last push time
            self.database.update_last_sync_time('push')

            # Update sync log
            self.database.update_sync_log(
                log_id,
                status='success' if stats['failed'] == 0 else 'error',
                records_processed=stats['processed'],
                records_success=stats['success'],
                records_failed=stats['failed']
            )

            if stats['failed'] > 0:
                message = f"Push completed with errors: {stats['success']} success, {stats['failed']} failed"
            else:
                message = f"Push completed: {stats['success']} records synced"

            logger.info(message)
            return True, message, stats

        except Exception as e:
            error_msg = f"Push sync error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.database.update_sync_log(
                log_id, 'error', error_message=error_msg
            )
            return False, error_msg, stats

    def push_timesheet(self, timesheet, config, headers):
        """
        Push a single timesheet entry to cloud payroll

        TODO: Adjust payload format based on actual API requirements

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Build payload
            # TODO: Customize this based on cloud payroll API requirements
            payload = {
                'sync_id': timesheet['sync_id'],
                'employee_id': timesheet['employee_backend_id'],
                'employee_name': timesheet['employee_name'],
                'log_type': timesheet['log_type'],
                'date': timesheet['date'],
                'time': timesheet['time'],
                'photo_path': timesheet.get('photo_path'),
                'created_at': timesheet['created_at']
            }

            # Make API request
            response = self.session.post(
                config['push_url'],
                headers=headers,
                json=payload,
                timeout=30
            )

            if response.status_code in [200, 201]:
                # Parse response to get backend ID
                response_data = response.json()

                # TODO: Adjust this based on actual API response structure
                # Expected: {"id": 123, "message": "Success"}
                backend_id = response_data.get('id') or response_data.get('timesheet_id')

                if backend_id:
                    # Mark as synced
                    self.database.mark_timesheet_synced(
                        timesheet['id'],
                        backend_id
                    )
                    logger.info(f"Timesheet {timesheet['id']} synced successfully (backend ID: {backend_id})")
                    return True
                else:
                    # Success but no ID returned
                    logger.warning(f"Timesheet {timesheet['id']} pushed but no backend ID returned")
                    self.database.mark_timesheet_sync_failed(
                        timesheet['id'],
                        "Success but no backend ID in response"
                    )
                    return False

            elif response.status_code == 409:
                # Conflict - record already exists
                logger.warning(f"Timesheet {timesheet['id']} already exists in backend")
                # Try to extract existing ID from response
                try:
                    response_data = response.json()
                    existing_id = response_data.get('existing_id')
                    if existing_id:
                        self.database.mark_timesheet_synced(timesheet['id'], existing_id)
                        return True
                except:
                    pass

                self.database.mark_timesheet_sync_failed(
                    timesheet['id'],
                    "Duplicate record in backend"
                )
                return False

            else:
                # Other error
                error_msg = f"HTTP {response.status_code}: {response.text[:200]}"
                logger.error(f"Failed to push timesheet {timesheet['id']}: {error_msg}")
                self.database.mark_timesheet_sync_failed(
                    timesheet['id'],
                    error_msg
                )
                return False

        except requests.exceptions.Timeout:
            error_msg = "Request timeout"
            logger.error(f"Timeout pushing timesheet {timesheet['id']}")
            self.database.mark_timesheet_sync_failed(timesheet['id'], error_msg)
            return False

        except requests.exceptions.ConnectionError:
            error_msg = "Connection error"
            logger.error(f"Connection error pushing timesheet {timesheet['id']}")
            self.database.mark_timesheet_sync_failed(timesheet['id'], error_msg)
            return False

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(f"Error pushing timesheet {timesheet['id']}: {e}", exc_info=True)
            self.database.mark_timesheet_sync_failed(timesheet['id'], error_msg)
            return False
