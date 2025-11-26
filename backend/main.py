"""
San Beda Integration Tool - Main Application
Desktop application for syncing timekeeping data between on-premise and cloud systems
"""

import sys
import os
import logging
import platform
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtWebChannel import QWebChannel

from database import Database
from bridge import Bridge
from services.pull_service import PullService
from services.push_service import PushService
from services.scheduler import SyncScheduler

# Determine if running as frozen executable (PyInstaller bundle)
IS_FROZEN = getattr(sys, 'frozen', False)

# Configure log file path
if IS_FROZEN and platform.system() == 'Darwin':
    # macOS: Use /tmp for debugging packaged app
    LOG_FILE = '/tmp/sanbeda_integration.log'
elif IS_FROZEN:
    # Windows/other: Use temp directory
    import tempfile
    LOG_FILE = os.path.join(tempfile.gettempdir(), 'sanbeda_integration.log')
else:
    # Development: Use current directory
    LOG_FILE = 'sanbeda_integration.log'

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if not IS_FROZEN else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Dev mode: True for development, False when frozen (packaged)
DEV_MODE = not IS_FROZEN
HTTP_PORT = 8765


class LocalHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Custom HTTP request handler for serving frontend files"""

    def __init__(self, *args, **kwargs):
        # Serve from frontend/dist directory
        frontend_dir = Path(__file__).parent.parent / 'frontend' / 'dist'
        super().__init__(*args, directory=str(frontend_dir), **kwargs)

    def log_message(self, format, *args):
        """Override to use logger instead of stdout"""
        logger.debug(f"HTTP: {format % args}")

    def end_headers(self):
        """Add CORS headers"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()


class IntegrationApp:
    """Main application class"""

    def __init__(self):
        logger.info("Initializing San Beda Integration Tool")

        # Initialize Qt Application
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("San Beda Integration Tool")
        self.app.setOrganizationName("The Abba")

        # Initialize database
        self.database = Database()

        # Initialize services
        self.pull_service = PullService(self.database)
        self.push_service = PushService(self.database)

        # Initialize bridge
        self.bridge = Bridge(self.database, self.pull_service, self.push_service)

        # Initialize scheduler
        self.scheduler = SyncScheduler(self.pull_service, self.push_service, self.database)

        # Start HTTP server if not in dev mode
        if not DEV_MODE:
            self.start_http_server()

        # Create web view
        self.create_web_view()

        logger.info("Application initialized successfully")

    def start_http_server(self):
        """Start local HTTP server for serving frontend files"""
        def run_server():
            try:
                server = HTTPServer(('localhost', HTTP_PORT), LocalHTTPRequestHandler)
                logger.info(f"HTTP server started on http://localhost:{HTTP_PORT}")
                server.serve_forever()
            except Exception as e:
                logger.error(f"HTTP server error: {e}")

        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

    def create_web_view(self):
        """Create and configure the web view"""
        self.view = QWebEngineView()

        # Configure web engine settings
        settings = self.view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)

        # Enable developer tools in dev mode
        if DEV_MODE:
            settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptCanOpenWindows, True)

        # Set up QWebChannel for Python-JS communication
        self.channel = QWebChannel()
        self.channel.registerObject('bridge', self.bridge)
        self.view.page().setWebChannel(self.channel)

        # Load the frontend
        if DEV_MODE:
            # In dev mode, load from Vite dev server
            url = "http://localhost:5173"
            logger.info(f"Loading from Vite dev server: {url}")
        else:
            # In production, load from local HTTP server
            url = f"http://localhost:{HTTP_PORT}"
            logger.info(f"Loading from local HTTP server: {url}")

        self.view.load(QUrl(url))

        # Window configuration
        self.view.setWindowTitle("San Beda Integration Tool")
        self.view.resize(1400, 900)

        # Show maximized
        self.view.showMaximized()

    def run(self):
        """Run the application"""
        logger.info("Starting application event loop")

        # Start scheduler
        self.scheduler.start()

        return self.app.exec()


def main():
    """Application entry point"""
    try:
        logger.info("=" * 80)
        logger.info("San Beda Integration Tool Starting")
        logger.info(f"Python Version: {sys.version}")
        logger.info(f"Platform: {platform.system()} {platform.release()}")
        logger.info(f"Frozen (packaged): {IS_FROZEN}")
        logger.info(f"Development Mode: {DEV_MODE}")
        logger.info(f"Log File: {LOG_FILE}")
        logger.info("=" * 80)

        app = IntegrationApp()
        sys.exit(app.run())

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
