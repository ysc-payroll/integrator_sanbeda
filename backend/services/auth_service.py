"""
San Beda Integration Tool - Authentication Service
Handles authentication with San Beda timekeeping system
"""

import requests
import logging
import hashlib
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authenticating with San Beda timekeeping system"""

    def __init__(self, database):
        self.database = database
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'San Beda Integration Tool/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json;charset=UTF-8'
        })

    def get_valid_token(self):
        """
        Get a valid login token, authenticating if necessary

        Returns:
            str: Valid login token
        """
        # Try to get existing token
        token = self.database.get_login_token()

        if token:
            # Check if token is still valid (tokens are typically valid for a long time)
            # For now, we'll assume token is valid unless auth fails
            logger.info("Using existing login token")
            return token

        # No token or expired, need to authenticate
        logger.info("No valid token found, authenticating...")
        return self.authenticate()

    def authenticate(self):
        """
        Authenticate with San Beda system using challenge-response flow

        Step 1: POST with username only → Get challenge (randomKey, realm, encryptType)
        Step 2: POST with username + encrypted password → Get token

        Returns:
            str: Login token
        """
        try:
            config = self.database.get_api_config()
            if not config:
                raise Exception("API configuration not found")

            host = config.get('pull_host')
            username = config.get('pull_username')
            password = config.get('pull_password')

            if not all([host, username, password]):
                raise Exception("San Beda host, username, and password required for authentication")

            # Build authentication URL
            auth_url = f"http://{host}/brms/api/v1.0/accounts/authorize"

            logger.info(f"Authenticating to San Beda at {auth_url}")
            logger.info(f"Username: {username}")

            # Step 1: Send initial authentication request (challenge request)
            payload_step1 = {
                "userName": username,
                "ipAddress": "",
                "clientType": "WINPC_V2"
            }

            logger.info("Step 1: Sending challenge request...")
            response1 = self.session.post(
                auth_url,
                json=payload_step1,
                timeout=30
            )

            # If we get 200, try to get loginToken directly (simple auth)
            if response1.status_code == 200:
                data = response1.json()
                login_token = data.get('loginToken')

                if login_token:
                    self.database.update_login_token(login_token)
                    logger.info(f"Authentication successful (simple), token: {login_token[:20]}...")
                    return login_token

            # If we get 401, we need to handle challenge-response
            if response1.status_code == 401:
                logger.info("Step 1: Challenge received, processing...")
                challenge_data = response1.json()

                random_key = challenge_data.get('randomKey')
                realm = challenge_data.get('realm')
                encrypt_type = challenge_data.get('encryptType')

                if not all([random_key, realm, encrypt_type]):
                    raise Exception(f"Invalid challenge response: {challenge_data}")

                logger.info(f"Challenge details: encryptType={encrypt_type}, randomKey={random_key}")

                # Step 2: Encrypt password and send authentication
                if encrypt_type == 'MD5':
                    # Encrypt password: MD5(MD5(password) + randomKey)
                    password_md5 = hashlib.md5(password.encode()).hexdigest()
                    encrypted_password = hashlib.md5((password_md5 + random_key).encode()).hexdigest()
                    logger.info(f"Password encrypted using MD5")
                else:
                    raise Exception(f"Unsupported encryption type: {encrypt_type}")

                # Send authentication with encrypted password
                payload_step2 = {
                    "userName": username,
                    "password": encrypted_password,
                    "ipAddress": "",
                    "clientType": "WINPC_V2",
                    "randomKey": random_key,
                    "realm": realm
                }

                logger.info("Step 2: Sending authentication with encrypted password...")
                response2 = self.session.post(
                    auth_url,
                    json=payload_step2,
                    timeout=30
                )

                if response2.status_code != 200:
                    error_msg = f"Authentication failed: HTTP {response2.status_code}"
                    logger.error(error_msg)
                    logger.error(f"Response: {response2.text}")
                    raise Exception(error_msg)

                # Parse successful response
                data = response2.json()
                login_token = data.get('loginToken')

                if not login_token:
                    raise Exception(f"No loginToken in response: {data}")

                # Store token in database
                self.database.update_login_token(login_token)
                logger.info(f"Authentication successful (challenge-response), token: {login_token[:20]}...")

                return login_token

            # Unexpected status code
            error_msg = f"Authentication failed: HTTP {response1.status_code}"
            logger.error(error_msg)
            logger.error(f"Response: {response1.text}")
            raise Exception(error_msg)

        except requests.exceptions.Timeout:
            error_msg = "Authentication timeout: Server not responding"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.ConnectionError as e:
            error_msg = f"Connection error: Cannot reach San Beda server - {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            logger.error(f"Authentication error: {e}", exc_info=True)
            raise

    def test_connection(self):
        """
        Test authentication to San Beda system

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            token = self.authenticate()
            return True, f"Authentication successful. Token: {token[:20]}..."
        except Exception as e:
            return False, f"Authentication failed: {str(e)}"

    def invalidate_token(self):
        """Invalidate the current token (force re-authentication on next request)"""
        self.database.update_login_token(None)
        logger.info("Login token invalidated")
