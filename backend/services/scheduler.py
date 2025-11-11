"""
San Beda Integration Tool - Sync Scheduler
Automated scheduling for pull and push sync operations
"""

import schedule
import threading
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SyncScheduler:
    """Scheduler for automated sync operations"""

    def __init__(self, pull_service, push_service, database):
        self.pull_service = pull_service
        self.push_service = push_service
        self.database = database
        self.running = False
        self.thread = None

    def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return

        logger.info("Starting sync scheduler")
        self.running = True

        # Set up schedules based on config
        self.update_schedules()

        # Start scheduler thread
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping sync scheduler")
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)

    def update_schedules(self):
        """Update schedules based on database config"""
        try:
            config = self.database.get_api_config()
            if not config:
                logger.warning("No API config found, using default intervals")
                pull_interval = 30
                push_interval = 15
            else:
                pull_interval = config.get('pull_interval_minutes', 30)
                push_interval = config.get('push_interval_minutes', 15)

            # Clear existing schedules
            schedule.clear()

            # Schedule pull sync
            if pull_interval > 0:
                schedule.every(pull_interval).minutes.do(self.run_pull_sync)
                logger.info(f"Pull sync scheduled every {pull_interval} minutes")

            # Schedule push sync
            if push_interval > 0:
                schedule.every(push_interval).minutes.do(self.run_push_sync)
                logger.info(f"Push sync scheduled every {push_interval} minutes")

        except Exception as e:
            logger.error(f"Error updating schedules: {e}")

    def _run_scheduler(self):
        """Run the scheduler loop"""
        logger.info("Scheduler loop started")

        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Scheduler loop error: {e}", exc_info=True)

        logger.info("Scheduler loop stopped")

    def run_pull_sync(self):
        """Execute pull sync"""
        logger.info("Scheduled pull sync starting")
        try:
            success, message, stats = self.pull_service.pull_data()
            if success:
                logger.info(f"Scheduled pull sync completed: {message}")
            else:
                logger.error(f"Scheduled pull sync failed: {message}")
        except Exception as e:
            logger.error(f"Scheduled pull sync error: {e}", exc_info=True)

    def run_push_sync(self):
        """Execute push sync"""
        logger.info("Scheduled push sync starting")
        try:
            success, message, stats = self.push_service.push_data()
            if success:
                logger.info(f"Scheduled push sync completed: {message}")
            else:
                logger.error(f"Scheduled push sync failed: {message}")
        except Exception as e:
            logger.error(f"Scheduled push sync error: {e}", exc_info=True)

    def trigger_pull_now(self):
        """Manually trigger pull sync immediately"""
        logger.info("Manual pull sync triggered")
        threading.Thread(target=self.run_pull_sync, daemon=True).start()

    def trigger_push_now(self):
        """Manually trigger push sync immediately"""
        logger.info("Manual push sync triggered")
        threading.Thread(target=self.run_push_sync, daemon=True).start()
