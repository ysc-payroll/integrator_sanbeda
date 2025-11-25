"""
San Beda Integration Tool - Seed Data Script
Populates the database with dummy data for demo purposes
"""

from database import Database
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed the database with dummy data"""
    print("=" * 60)
    print("San Beda Integration Tool - Seeding Database")
    print("=" * 60)

    db = Database()

    # Sample employees
    employees = [
        {"backend_id": 2734, "name": "John Doe", "employee_code": "EMP001", "employee_number": 8104},
        {"backend_id": 2735, "name": "Jane Smith", "employee_code": "EMP002", "employee_number": 8105},
        {"backend_id": 2736, "name": "Michael Johnson", "employee_code": "EMP003", "employee_number": 8106},
        {"backend_id": 2737, "name": "Sarah Williams", "employee_code": "EMP004", "employee_number": 8107},
        {"backend_id": 2738, "name": "Robert Brown", "employee_code": "EMP005", "employee_number": 8108},
        {"backend_id": 2739, "name": "Emily Davis", "employee_code": "EMP006", "employee_number": 8109},
        {"backend_id": 2740, "name": "David Miller", "employee_code": "EMP007", "employee_number": 8110},
        {"backend_id": 2741, "name": "Jessica Wilson", "employee_code": "EMP008", "employee_number": 8111},
        {"backend_id": 2742, "name": "Christopher Moore", "employee_code": "EMP009", "employee_number": 8112},
        {"backend_id": 2743, "name": "Amanda Taylor", "employee_code": "EMP010", "employee_number": 8113},
    ]

    print("\n1. Adding employees...")
    employee_map = {}
    for emp in employees:
        emp_id = db.add_or_update_employee(
            backend_id=emp["backend_id"],
            name=emp["name"],
            employee_code=emp["employee_code"],
            employee_number=emp["employee_number"]
        )
        employee_map[emp["backend_id"]] = emp_id
        print(f"   ✓ Added: {emp['name']} (ID: {emp['backend_id']})")

    print(f"\n✓ Added {len(employees)} employees")

    # Generate timesheet entries for the last 7 days
    print("\n2. Adding timesheet entries...")

    today = datetime.now()
    timesheet_count = 0
    synced_count = 0

    for day_offset in range(7, 0, -1):  # Last 7 days
        current_date = today - timedelta(days=day_offset)
        date_str = current_date.strftime("%Y-%m-%d")

        print(f"\n   Date: {date_str}")

        # Each employee has 80% chance of having entries on any given day
        for backend_id, emp_id in employee_map.items():
            if random.random() < 0.8:  # 80% chance
                # Morning clock in (8:00 AM - 9:00 AM)
                in_hour = random.randint(8, 9)
                in_minute = random.randint(0, 59)
                in_time = f"{in_hour:02d}:{in_minute:02d}"

                # Evening clock out (5:00 PM - 6:00 PM)
                out_hour = random.randint(17, 18)
                out_minute = random.randint(0, 59)
                out_time = f"{out_hour:02d}:{out_minute:02d}"

                # Create IN entry
                timestamp_in = current_date.replace(hour=in_hour, minute=in_minute, second=0)
                sync_id_in = f"1001_{backend_id}_{timestamp_in.strftime('%Y%m%d%H%M%S')}"

                db.add_timesheet_entry(
                    sync_id=sync_id_in,
                    employee_id=emp_id,
                    log_type="in",
                    date=date_str,
                    time=in_time,
                    photo_path=None
                )
                timesheet_count += 1

                # Create OUT entry
                timestamp_out = current_date.replace(hour=out_hour, minute=out_minute, second=0)
                sync_id_out = f"1001_{backend_id}_{timestamp_out.strftime('%Y%m%d%H%M%S')}"

                out_entry_id = db.add_timesheet_entry(
                    sync_id=sync_id_out,
                    employee_id=emp_id,
                    log_type="out",
                    date=date_str,
                    time=out_time,
                    photo_path=None
                )
                timesheet_count += 1

                # 70% of entries are synced, 30% are pending
                if random.random() < 0.7:
                    # Mark as synced with a fake backend ID
                    fake_backend_id = 128900 + timesheet_count
                    db.mark_timesheet_synced(out_entry_id - 1, fake_backend_id)  # IN entry
                    db.mark_timesheet_synced(out_entry_id, fake_backend_id + 1)  # OUT entry
                    synced_count += 2

                # 5% of pending entries have errors
                elif random.random() < 0.05:
                    error_messages = [
                        "Connection timeout",
                        "Invalid employee ID",
                        "Duplicate entry detected",
                        "Server returned 500 error",
                        "Authentication failed"
                    ]
                    db.mark_timesheet_sync_failed(out_entry_id - 1, random.choice(error_messages))
                    db.mark_timesheet_sync_failed(out_entry_id, random.choice(error_messages))

        print(f"   ✓ Added entries for {date_str}")

    print(f"\n✓ Added {timesheet_count} timesheet entries")
    print(f"  - Synced: {synced_count}")
    print(f"  - Pending: {timesheet_count - synced_count}")

    # Create some sync logs
    print("\n3. Adding sync logs...")

    # Pull sync logs
    for i in range(5):
        log_date = today - timedelta(days=i * 2)
        log_id = db.create_sync_log('pull')

        success = random.randint(10, 30)
        failed = random.randint(0, 3)

        db.update_sync_log(
            log_id,
            status='success' if failed == 0 else 'error',
            records_processed=success + failed,
            records_success=success,
            records_failed=failed,
            error_message="Network timeout" if failed > 0 else None
        )

    # Push sync logs
    for i in range(5):
        log_date = today - timedelta(days=i * 2 + 1)
        log_id = db.create_sync_log('push')

        success = random.randint(15, 40)
        failed = random.randint(0, 5)

        db.update_sync_log(
            log_id,
            status='success' if failed == 0 else 'error',
            records_processed=success + failed,
            records_success=success,
            records_failed=failed,
            error_message="API rate limit exceeded" if failed > 0 else None
        )

    print("✓ Added 10 sync logs")

    # Get statistics
    print("\n" + "=" * 60)
    print("DATABASE SEEDED SUCCESSFULLY!")
    print("=" * 60)

    stats = db.get_timesheet_stats()
    print(f"\nDatabase Statistics:")
    print(f"  Total Employees: {len(employees)}")
    print(f"  Total Timesheet Entries: {stats['total']}")
    print(f"  Synced: {stats['synced']}")
    print(f"  Pending: {stats['pending']}")
    print(f"  Errors: {stats['errors']}")
    print(f"  Sync Logs: 10")

    print("\n" + "=" * 60)
    print("You can now start the application and see the demo data!")
    print("=" * 60)
    print("\nTo start the app:")
    print("  Terminal 1: cd frontend && npm run dev")
    print("  Terminal 2: cd backend && source venv/bin/activate && python main.py")
    print()

if __name__ == "__main__":
    seed_database()
