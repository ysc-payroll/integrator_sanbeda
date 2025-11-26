"""
Test San Beda Pull Sync
"""
import sys
from database import Database
from services.pull_service import PullService

def test_pull_sync():
    """Test pulling data from San Beda"""
    print("=" * 80)
    print("Testing San Beda Pull Sync")
    print("=" * 80)

    # Initialize database
    db = Database()

    # Configure San Beda credentials
    print("\n1. Configuring San Beda credentials...")
    db.update_api_config(
        pull_host='192.168.9.125',
        pull_username='system',
        pull_password='Admin@123'
    )
    print("   ✓ Credentials configured")

    # Initialize pull service
    print("\n2. Initializing pull service...")
    pull_service = PullService(db)
    print("   ✓ Pull service initialized")

    # Pull data
    print("\n3. Pulling attendance data from San Beda...")
    print("   This may take a moment...\n")

    success, message, stats = pull_service.pull_data()

    print("=" * 80)
    if success:
        print("✅ PULL SYNC SUCCESS!")
        print(f"\n   {message}")
        print(f"\n   Statistics:")
        print(f"   - Attendance records processed: {stats['processed']}")
        print(f"   - Timesheet entries created: {stats['success']}")
        print(f"   - Skipped (duplicates): {stats['skipped']}")
        print(f"   - Failed: {stats['failed']}")
    else:
        print("❌ PULL SYNC FAILED!")
        print(f"   {message}")
    print("=" * 80)

    return success

if __name__ == '__main__':
    try:
        success = test_pull_sync()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
