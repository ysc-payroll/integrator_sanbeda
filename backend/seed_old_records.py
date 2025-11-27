"""
Seed script to populate old timesheet records for testing cleanup
"""
import sqlite3
import os
from datetime import datetime, timedelta
import random

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'sanbeda_integration.db')

def seed_old_records(num_records=50, days_ago_start=90, days_ago_end=60):
    """
    Create test timesheet records with dates in the past

    Args:
        num_records: Number of records to create
        days_ago_start: Oldest records (e.g., 90 = 90 days ago)
        days_ago_end: Newest old records (e.g., 60 = 60 days ago)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"Seeding {num_records} old timesheet records...")
    print(f"Date range: {days_ago_start} to {days_ago_end} days ago")

    employees = [f"EMP{i:03d}" for i in range(1, 11)]

    for i in range(num_records):
        # Random date between days_ago_start and days_ago_end
        days_offset = random.randint(days_ago_end, days_ago_start)
        record_date = (datetime.now() - timedelta(days=days_offset)).strftime("%Y-%m-%d")

        # Random employee
        emp_code = random.choice(employees)

        # Random time
        hour = random.randint(7, 18)
        minute = random.randint(0, 59)
        record_time = f"{hour:02d}:{minute:02d}:00"

        # Log type (in/out)
        log_type = random.choice(['in', 'out'])

        # Generate sync_id
        sync_id = f"TEST-{record_date}-{emp_code}-{log_type}-{i}"

        try:
            cursor.execute("""
                INSERT INTO timesheet (sync_id, employee_id, log_type, date, time, status, backend_timesheet_id)
                VALUES (?, ?, ?, ?, ?, 'success', ?)
            """, (sync_id, emp_code, log_type, record_date, record_time, f"SYNC-{i}"))
            print(f"  Created: {sync_id} ({record_date})")
        except sqlite3.IntegrityError:
            print(f"  Skipped (duplicate): {sync_id}")

    conn.commit()

    # Show summary
    cursor.execute("SELECT COUNT(*) FROM timesheet WHERE date < date('now', '-60 days')")
    old_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM timesheet")
    total_count = cursor.fetchone()[0]

    print(f"\nDone!")
    print(f"Total records: {total_count}")
    print(f"Records older than 60 days: {old_count}")

    conn.close()

if __name__ == '__main__':
    seed_old_records(num_records=50, days_ago_start=90, days_ago_end=65)
