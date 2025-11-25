"""
Test San Beda Authentication
"""
import sys
from database import Database
from services.auth_service import AuthService

def test_authentication():
    """Test San Beda authentication with provided credentials"""
    print("=" * 80)
    print("Testing San Beda Authentication")
    print("=" * 80)

    # Initialize database
    db = Database()

    # Configure San Beda credentials
    print("\n1. Configuring San Beda credentials...")
    db.update_api_config(
        pull_host='192.168.9.125',
        pull_username='system',
        pull_password='admin1234567'
    )
    print("   ✓ Credentials configured")

    # Initialize auth service
    print("\n2. Initializing authentication service...")
    auth_service = AuthService(db)
    print("   ✓ Auth service initialized")

    # Test connection
    print("\n3. Testing connection to San Beda server...")
    print("   Host: 192.168.9.125")
    print("   Username: system")
    print("   Attempting authentication...\n")

    success, message = auth_service.test_connection()

    print("=" * 80)
    if success:
        print("✅ SUCCESS!")
        print(f"   {message}")
    else:
        print("❌ FAILED!")
        print(f"   {message}")
    print("=" * 80)

    return success

if __name__ == '__main__':
    try:
        success = test_authentication()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
