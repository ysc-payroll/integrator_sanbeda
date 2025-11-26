"""
Test YAHSHUA Payroll Push Sync
"""
import sys
from database import Database
from services.push_service import PushService

def test_push_sync():
    """Test pushing data to YAHSHUA"""
    print("=" * 80)
    print("Testing YAHSHUA Payroll Push Sync")
    print("=" * 80)

    # Initialize database
    db = Database()

    # Configure YAHSHUA credentials
    print("\n1. Configuring YAHSHUA credentials...")
    db.update_api_config(
        push_username='timekeeping@sanbeda.com',
        push_password='722436Aa!'
    )
    print("   ✓ Credentials configured")

    # Initialize push service
    print("\n2. Initializing push service...")
    push_service = PushService(db)
    print("   ✓ Push service initialized")

    # Check unsynced records
    print("\n3. Checking unsynced records...")
    unsynced = db.get_unsynced_timesheets(limit=10)
    print(f"   Found {len(unsynced)} unsynced records")

    if len(unsynced) == 0:
        print("\n   No records to push. Pull some data first!")
        return True

    # Show sample records
    print("\n   Sample records to push:")
    for i, record in enumerate(unsynced[:3]):
        print(f"   [{i+1}] Employee: {record.get('employee_code')} | "
              f"Date: {record.get('date')} | "
              f"Time: {record.get('time')} | "
              f"Type: {record.get('log_type')}")

    # Push data
    print("\n4. Pushing data to YAHSHUA...")
    print("   This may take a moment...\n")

    success, message, stats = push_service.push_data()

    print("=" * 80)
    if success:
        print("✅ PUSH SYNC COMPLETED!")
        print(f"\n   {message}")
        print(f"\n   Statistics:")
        print(f"   - Records processed: {stats['processed']}")
        print(f"   - Successfully synced: {stats['success']}")
        print(f"   - Failed: {stats['failed']}")
        print(f"   - Skipped: {stats.get('skipped', 0)}")
    else:
        print("❌ PUSH SYNC FAILED!")
        print(f"   {message}")
    print("=" * 80)

    return success

if __name__ == '__main__':
    try:
        success = test_push_sync()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
