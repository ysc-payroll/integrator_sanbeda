"""
Test YAHSHUA Payroll Push - Debug Version
"""
import requests
import json
from database import Database
from services.push_service import PushService

def test_push_debug():
    """Test push with detailed debugging"""
    print("=" * 80)
    print("YAHSHUA Push - Debug Test")
    print("=" * 80)

    db = Database()

    # Configure credentials
    db.update_api_config(
        push_username='timekeeping@sanbeda.com',
        push_password='722436Aa!'
    )

    push_service = PushService(db)

    # Get token first
    print("\n1. Authenticating...")
    token = push_service.authenticate()
    print(f"   Token: {token[:30]}...")

    # Get a small batch of unsynced records
    print("\n2. Getting unsynced records...")
    unsynced = db.get_unsynced_timesheets(limit=3)
    print(f"   Found {len(unsynced)} records")

    if len(unsynced) == 0:
        print("   No records to test!")
        return

    # Build log_list
    log_list = []
    for ts in unsynced:
        log_entry = {
            "id": ts['id'],
            "employee": ts.get('employee_code', ''),
            "log_time": ts['time'],
            "log_type": ts['log_type'].upper(),
            "sync_id": ts['sync_id'],
            "date": ts['date']
        }
        log_list.append(log_entry)
        print(f"   Entry: {log_entry}")

    # Make direct API call
    print("\n3. Sending to YAHSHUA...")

    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

    # YAHSHUA API requires:
    # - from_biometrics: true to extract log_list from wrapper
    # - from_new_biometrics: true to lookup by employee code (not PK)
    payload = {
        "from_biometrics": True,
        "from_new_biometrics": True,
        "log_list": log_list
    }

    print(f"\n   URL: https://yahshuapayroll.com/api/sync-time-in-out/")
    print(f"   Payload: {json.dumps(payload, indent=2)}")

    response = requests.post(
        "https://yahshuapayroll.com/api/sync-time-in-out/",
        headers=headers,
        json=payload,
        timeout=60
    )

    print(f"\n4. Response:")
    print(f"   Status: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    print(f"   Body: {response.text}")

    try:
        data = response.json()
        print(f"\n   Parsed JSON:")
        print(f"   Type: {type(data)}")
        print(f"   Content: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"   JSON parse error: {e}")

if __name__ == '__main__':
    test_push_debug()
