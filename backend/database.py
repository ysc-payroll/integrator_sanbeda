"""
San Beda Integration Tool - Database Manager
SQLite database for storing timesheet data and sync status
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path="database/sanbeda_integration.db"):
        """Initialize database connection and create tables if needed"""
        self.db_path = Path(__file__).parent / db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def get_connection(self):
        """Get database connection with row factory"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Create all tables and indexes"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            # Company table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backend_id INTEGER UNIQUE,
                    name TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_company_backend_id ON company(backend_id)")

            # Employee table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employee (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backend_id INTEGER UNIQUE,
                    name TEXT NOT NULL,
                    employee_code TEXT,
                    employee_number INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    deleted_at DATETIME
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_employee_backend_id ON employee(backend_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_employee_code ON employee(employee_code)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_employee_deleted_at ON employee(deleted_at)")

            # Timesheet table (primary sync table)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS timesheet (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sync_id TEXT UNIQUE NOT NULL,
                    employee_id INTEGER NOT NULL,
                    log_type TEXT NOT NULL CHECK(log_type IN ('in', 'out')),
                    date TEXT NOT NULL,
                    time TEXT NOT NULL,
                    photo_path TEXT,
                    is_synced BOOLEAN DEFAULT 0,
                    status TEXT DEFAULT 'success',
                    error_message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    backend_timesheet_id INTEGER,
                    synced_at DATETIME,
                    sync_error_message TEXT,
                    FOREIGN KEY (employee_id) REFERENCES employee(id)
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timesheet_sync_id ON timesheet(sync_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timesheet_employee_id ON timesheet(employee_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timesheet_date ON timesheet(date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timesheet_is_synced ON timesheet(is_synced)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timesheet_backend_id ON timesheet(backend_timesheet_id)")

            # Users table (admin access)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    email TEXT NOT NULL,
                    name TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    last_login DATETIME,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Sync logs table (track pull/push operations)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sync_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sync_type TEXT NOT NULL CHECK(sync_type IN ('pull', 'push')),
                    status TEXT NOT NULL CHECK(status IN ('started', 'success', 'error')),
                    records_processed INTEGER DEFAULT 0,
                    records_success INTEGER DEFAULT 0,
                    records_failed INTEGER DEFAULT 0,
                    error_message TEXT,
                    started_at DATETIME NOT NULL,
                    completed_at DATETIME,
                    metadata TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sync_logs_type ON sync_logs(sync_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sync_logs_status ON sync_logs(status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sync_logs_started ON sync_logs(started_at)")

            # API configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_config (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    pull_url TEXT,
                    pull_auth_type TEXT,
                    pull_credentials TEXT,
                    pull_host TEXT,
                    pull_username TEXT,
                    pull_password TEXT,
                    login_token TEXT,
                    token_created_at DATETIME,
                    push_url TEXT,
                    push_auth_type TEXT,
                    push_credentials TEXT,
                    push_username TEXT,
                    push_password TEXT,
                    push_token TEXT,
                    push_token_created_at DATETIME,
                    pull_interval_minutes INTEGER DEFAULT 30,
                    push_interval_minutes INTEGER DEFAULT 15,
                    last_pull_at DATETIME,
                    last_push_at DATETIME,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Add new columns to existing table if they don't exist (for migration)
            try:
                cursor.execute("ALTER TABLE api_config ADD COLUMN pull_host TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE api_config ADD COLUMN pull_username TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE api_config ADD COLUMN pull_password TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE api_config ADD COLUMN login_token TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE api_config ADD COLUMN token_created_at DATETIME")
            except:
                pass
            # YAHSHUA push credential fields
            try:
                cursor.execute("ALTER TABLE api_config ADD COLUMN push_username TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE api_config ADD COLUMN push_password TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE api_config ADD COLUMN push_token TEXT")
            except:
                pass
            try:
                cursor.execute("ALTER TABLE api_config ADD COLUMN push_token_created_at DATETIME")
            except:
                pass
            # YAHSHUA user info from login response
            try:
                cursor.execute("ALTER TABLE api_config ADD COLUMN push_user_logged TEXT")
            except:
                pass

            # Insert default config if not exists
            cursor.execute("SELECT COUNT(*) as count FROM api_config WHERE id = 1")
            if cursor.fetchone()['count'] == 0:
                cursor.execute("""
                    INSERT INTO api_config (id, pull_interval_minutes, push_interval_minutes)
                    VALUES (1, 30, 15)
                """)

            conn.commit()
            logger.info("Database initialized successfully")
        except Exception as e:
            conn.rollback()
            logger.error(f"Database initialization error: {e}")
            raise
        finally:
            conn.close()

    # ==================== TIMESHEET METHODS ====================

    def add_timesheet_entry(self, sync_id, employee_id, log_type, date, time, photo_path=None):
        """Add a new timesheet entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO timesheet (sync_id, employee_id, log_type, date, time, photo_path, status)
                VALUES (?, ?, ?, ?, ?, ?, 'success')
            """, (sync_id, employee_id, log_type, date, time, photo_path))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logger.warning(f"Duplicate timesheet entry: {sync_id}")
            return None
        except Exception as e:
            conn.rollback()
            logger.error(f"Error adding timesheet entry: {e}")
            raise
        finally:
            conn.close()

    def get_unsynced_timesheets(self, limit=100):
        """Get timesheet entries that need to be pushed to backend"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT t.*, e.backend_id as employee_backend_id, e.name as employee_name,
                       e.employee_code as employee_code
                FROM timesheet t
                JOIN employee e ON t.employee_id = e.id
                WHERE t.backend_timesheet_id IS NULL
                AND t.status = 'success'
                ORDER BY t.created_at ASC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def mark_timesheet_synced(self, timesheet_id, backend_timesheet_id):
        """Mark a timesheet entry as successfully synced"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE timesheet
                SET backend_timesheet_id = ?,
                    synced_at = ?,
                    sync_error_message = NULL
                WHERE id = ?
            """, (backend_timesheet_id, datetime.now(), timesheet_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error marking timesheet as synced: {e}")
            raise
        finally:
            conn.close()

    def mark_timesheet_sync_failed(self, timesheet_id, error_message):
        """Mark a timesheet sync as failed"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE timesheet
                SET sync_error_message = ?
                WHERE id = ?
            """, (error_message, timesheet_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error marking sync failed: {e}")
            raise
        finally:
            conn.close()

    def get_timesheet_stats(self):
        """Get statistics about timesheet entries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN backend_timesheet_id IS NOT NULL THEN 1 ELSE 0 END) as synced,
                    SUM(CASE WHEN backend_timesheet_id IS NULL THEN 1 ELSE 0 END) as pending,
                    SUM(CASE WHEN sync_error_message IS NOT NULL THEN 1 ELSE 0 END) as errors
                FROM timesheet
            """)
            return dict(cursor.fetchone())
        finally:
            conn.close()

    def get_all_timesheets(self, limit=1000, offset=0):
        """Get all timesheet entries with pagination"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT t.*, e.name as employee_name, e.employee_code
                FROM timesheet t
                JOIN employee e ON t.employee_id = e.id
                ORDER BY t.created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # ==================== EMPLOYEE METHODS ====================

    def add_or_update_employee(self, backend_id, name, employee_code=None, employee_number=None):
        """Add or update employee record"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO employee (backend_id, name, employee_code, employee_number)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(backend_id) DO UPDATE SET
                    name = excluded.name,
                    employee_code = excluded.employee_code,
                    employee_number = excluded.employee_number
            """, (backend_id, name, employee_code, employee_number))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            logger.error(f"Error adding/updating employee: {e}")
            raise
        finally:
            conn.close()

    def get_employee_by_backend_id(self, backend_id):
        """Get employee by backend ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM employee WHERE backend_id = ?", (backend_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_employee_by_code(self, employee_code):
        """Get employee by employee code (supports alphanumeric codes)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM employee WHERE employee_code = ?", (employee_code,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_all_employees(self):
        """Get all active employees"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM employee WHERE deleted_at IS NULL ORDER BY name")
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # ==================== SYNC LOG METHODS ====================

    def create_sync_log(self, sync_type):
        """Create a new sync log entry"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO sync_logs (sync_type, status, started_at)
                VALUES (?, 'started', ?)
            """, (sync_type, datetime.now()))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            logger.error(f"Error creating sync log: {e}")
            raise
        finally:
            conn.close()

    def update_sync_log(self, log_id, status, records_processed=0, records_success=0,
                       records_failed=0, error_message=None, metadata=None):
        """Update sync log with results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            metadata_json = json.dumps(metadata) if metadata else None
            cursor.execute("""
                UPDATE sync_logs
                SET status = ?,
                    records_processed = ?,
                    records_success = ?,
                    records_failed = ?,
                    error_message = ?,
                    completed_at = ?,
                    metadata = ?
                WHERE id = ?
            """, (status, records_processed, records_success, records_failed,
                  error_message, datetime.now(), metadata_json, log_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating sync log: {e}")
            raise
        finally:
            conn.close()

    def get_recent_sync_logs(self, sync_type=None, limit=50):
        """Get recent sync logs"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if sync_type:
                cursor.execute("""
                    SELECT * FROM sync_logs
                    WHERE sync_type = ?
                    ORDER BY started_at DESC
                    LIMIT ?
                """, (sync_type, limit))
            else:
                cursor.execute("""
                    SELECT * FROM sync_logs
                    ORDER BY started_at DESC
                    LIMIT ?
                """, (limit,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    # ==================== API CONFIG METHODS ====================

    def get_api_config(self):
        """Get API configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM api_config WHERE id = 1")
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def update_api_config(self, **kwargs):
        """Update API configuration"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            # Build dynamic update query
            set_clauses = [f"{key} = ?" for key in kwargs.keys()]
            values = list(kwargs.values())
            values.append(datetime.now())  # for updated_at
            values.append(1)  # for WHERE id = 1

            query = f"""
                UPDATE api_config
                SET {', '.join(set_clauses)}, updated_at = ?
                WHERE id = ?
            """
            cursor.execute(query, values)
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating API config: {e}")
            raise
        finally:
            conn.close()

    def update_last_sync_time(self, sync_type):
        """Update last pull/push time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            field = f"last_{sync_type}_at"
            cursor.execute(f"""
                UPDATE api_config
                SET {field} = ?, updated_at = ?
                WHERE id = 1
            """, (datetime.now(), datetime.now()))
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating last sync time: {e}")
            raise
        finally:
            conn.close()

    def update_login_token(self, token):
        """Update San Beda login token"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE api_config
                SET login_token = ?, token_created_at = ?, updated_at = ?
                WHERE id = 1
            """, (token, datetime.now(), datetime.now()))
            conn.commit()
            logger.info("Login token updated successfully")
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating login token: {e}")
            raise
        finally:
            conn.close()

    def get_login_token(self):
        """Get current login token"""
        config = self.get_api_config()
        return config.get('login_token') if config else None

    def update_push_token(self, token, user_logged=None):
        """Update YAHSHUA push token and user info"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            if token is None:
                # Logout - clear token and user info
                cursor.execute("""
                    UPDATE api_config
                    SET push_token = NULL, push_token_created_at = NULL,
                        push_user_logged = NULL, updated_at = ?
                    WHERE id = 1
                """, (datetime.now(),))
            else:
                # Login - store token and user info
                cursor.execute("""
                    UPDATE api_config
                    SET push_token = ?, push_token_created_at = ?,
                        push_user_logged = ?, updated_at = ?
                    WHERE id = 1
                """, (token, datetime.now(), user_logged, datetime.now()))
            conn.commit()
            logger.info("Push token updated successfully")
        except Exception as e:
            conn.rollback()
            logger.error(f"Error updating push token: {e}")
            raise
        finally:
            conn.close()

    def get_push_token(self):
        """Get current YAHSHUA push token"""
        config = self.get_api_config()
        return config.get('push_token') if config else None
