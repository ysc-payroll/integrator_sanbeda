"""
San Beda Integration Tool - Python-JavaScript Bridge
Provides QWebChannel bridge for communication between PyQt6 and Vue.js
"""

from PyQt6.QtCore import QObject, pyqtSlot, pyqtSignal
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Bridge(QObject):
    """Bridge class for Python-JavaScript communication via QWebChannel"""

    # Signals for sending data to JavaScript
    syncStatusUpdated = pyqtSignal(str)  # Emits JSON string with sync status
    syncProgressUpdated = pyqtSignal(str)  # Emits JSON string with progress
    syncCompleted = pyqtSignal(str)  # Emits JSON string with results

    def __init__(self, database, pull_service, push_service):
        super().__init__()
        self.database = database
        self.pull_service = pull_service
        self.push_service = push_service
        logger.info("Bridge initialized")

    # ==================== TIMESHEET METHODS ====================

    @pyqtSlot(result=str)
    def getTimesheetStats(self):
        """Get timesheet statistics"""
        try:
            stats = self.database.get_timesheet_stats()
            return json.dumps({"success": True, "data": stats})
        except Exception as e:
            logger.error(f"Error getting timesheet stats: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @pyqtSlot(int, int, result=str)
    def getAllTimesheets(self, limit=1000, offset=0):
        """Get all timesheets with pagination"""
        try:
            timesheets = self.database.get_all_timesheets(limit, offset)
            return json.dumps({"success": True, "data": timesheets})
        except Exception as e:
            logger.error(f"Error getting timesheets: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @pyqtSlot(int, result=str)
    def getUnsyncedTimesheets(self, limit=100):
        """Get unsynced timesheets"""
        try:
            timesheets = self.database.get_unsynced_timesheets(limit)
            return json.dumps({"success": True, "data": timesheets})
        except Exception as e:
            logger.error(f"Error getting unsynced timesheets: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @pyqtSlot(int, result=str)
    def retryFailedTimesheet(self, timesheet_id):
        """Retry syncing a failed timesheet"""
        try:
            # Clear error message to retry
            conn = self.database.get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE timesheet
                SET sync_error_message = NULL
                WHERE id = ?
            """, (timesheet_id,))
            conn.commit()
            conn.close()
            return json.dumps({"success": True})
        except Exception as e:
            logger.error(f"Error retrying timesheet: {e}")
            return json.dumps({"success": False, "error": str(e)})

    # ==================== EMPLOYEE METHODS ====================

    @pyqtSlot(result=str)
    def getAllEmployees(self):
        """Get all active employees"""
        try:
            employees = self.database.get_all_employees()
            return json.dumps({"success": True, "data": employees})
        except Exception as e:
            logger.error(f"Error getting employees: {e}")
            return json.dumps({"success": False, "error": str(e)})

    # ==================== SYNC METHODS ====================

    @pyqtSlot(result=str)
    def startPullSync(self):
        """Manually trigger pull sync from San Beda"""
        try:
            logger.info("Manual pull sync triggered from UI")
            success, message, stats = self.pull_service.pull_data()

            result = {
                "success": success,
                "message": message,
                "stats": stats
            }

            # Emit signal to update UI
            self.syncCompleted.emit(json.dumps({
                "type": "pull",
                "result": result
            }))

            return json.dumps(result)
        except Exception as e:
            logger.error(f"Error in manual pull sync: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @pyqtSlot(result=str)
    def startPushSync(self):
        """Manually trigger push sync to cloud payroll"""
        try:
            logger.info("Manual push sync triggered from UI")
            success, message, stats = self.push_service.push_data()

            result = {
                "success": success,
                "message": message,
                "stats": stats
            }

            # Emit signal to update UI
            self.syncCompleted.emit(json.dumps({
                "type": "push",
                "result": result
            }))

            return json.dumps(result)
        except Exception as e:
            logger.error(f"Error in manual push sync: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @pyqtSlot(result=str)
    def getSyncLogs(self):
        """Get recent sync logs"""
        try:
            logs = self.database.get_recent_sync_logs(limit=100)
            return json.dumps({"success": True, "data": logs})
        except Exception as e:
            logger.error(f"Error getting sync logs: {e}")
            return json.dumps({"success": False, "error": str(e)})

    # ==================== CONFIG METHODS ====================

    @pyqtSlot(result=str)
    def getApiConfig(self):
        """Get API configuration"""
        try:
            config = self.database.get_api_config()
            # Don't send credentials to frontend for security
            if config:
                config['pull_credentials'] = '***' if config.get('pull_credentials') else None
                config['pull_password'] = '***' if config.get('pull_password') else None
                config['push_credentials'] = '***' if config.get('push_credentials') else None
                config['login_token'] = '***' if config.get('login_token') else None
            return json.dumps({"success": True, "data": config})
        except Exception as e:
            logger.error(f"Error getting API config: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @pyqtSlot(str, result=str)
    def updateApiConfig(self, config_json):
        """Update API configuration"""
        try:
            config = json.loads(config_json)

            # Only update provided fields
            update_fields = {}
            allowed_fields = [
                'pull_url', 'pull_auth_type', 'pull_credentials',
                'pull_host', 'pull_username', 'pull_password',
                'push_url', 'push_auth_type', 'push_credentials',
                'pull_interval_minutes', 'push_interval_minutes'
            ]

            for field in allowed_fields:
                if field in config:
                    # Skip if credentials/passwords are masked
                    if (field.endswith('_credentials') or field.endswith('_password')) and config[field] == '***':
                        continue
                    update_fields[field] = config[field]

            self.database.update_api_config(**update_fields)
            logger.info(f"API config updated: {list(update_fields.keys())}")

            return json.dumps({"success": True, "message": "Configuration updated successfully"})
        except Exception as e:
            logger.error(f"Error updating API config: {e}")
            return json.dumps({"success": False, "error": str(e)})

    @pyqtSlot(str, result=str)
    def testConnection(self, connection_type):
        """Test API connection (pull or push)"""
        try:
            if connection_type == 'pull':
                success, message = self.pull_service.test_connection()
            elif connection_type == 'push':
                success, message = self.push_service.test_connection()
            else:
                return json.dumps({"success": False, "error": "Invalid connection type"})

            return json.dumps({"success": success, "message": message})
        except Exception as e:
            logger.error(f"Error testing connection: {e}")
            return json.dumps({"success": False, "error": str(e)})

    # ==================== UTILITY METHODS ====================

    @pyqtSlot(result=str)
    def getAppInfo(self):
        """Get application information"""
        return json.dumps({
            "success": True,
            "data": {
                "name": "San Beda Integration Tool",
                "version": "1.0.0",
                "description": "Bridge between on-premise timekeeping and cloud payroll"
            }
        })

    @pyqtSlot(str)
    def logMessage(self, message):
        """Log message from JavaScript"""
        logger.info(f"[JS] {message}")

    def emit_sync_status(self, status_dict):
        """Emit sync status update to JavaScript"""
        self.syncStatusUpdated.emit(json.dumps(status_dict))

    def emit_sync_progress(self, progress_dict):
        """Emit sync progress update to JavaScript"""
        self.syncProgressUpdated.emit(json.dumps(progress_dict))
