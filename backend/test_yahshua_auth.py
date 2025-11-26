"""
Test YAHSHUA Payroll Authentication
"""
import sys
from database import Database
from services.push_service import PushService

def test_authentication():
    """Test YAHSHUA authentication with provided credentials"""
    print("=" * 80)
    print("Testing YAHSHUA Payroll Authentication")
    print("=" * 80)

    # Initialize database
    db = Database()

    # Configure YAHSHUA credentials
    print("\n1. Configuring YAHSHUA credentials...")
    db.update_api_config(
        push_username='timekeeping@sanbeda.com',
        push_password='722436Aa!'
    )
    print("   Username: timekeeping@sanbeda.com")
    print("   Password: ****")
    print("   ✓ Credentials configured")

    # Initialize push service
    print("\n2. Initializing push service...")
    push_service = PushService(db)
    print("   ✓ Push service initialized")

    # Test connection
    print("\n3. Testing connection to YAHSHUA Payroll...")
    print("   Endpoint: https://www.yahshuapayroll.com/api/login/")
    print("   Attempting authentication...\n")

    success, message = push_service.test_connection()

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
