"""
Test YAHSHUA Payroll Authentication - Multiple Methods
"""
import requests
import json

def test_yahshua():
    """Test YAHSHUA authentication with different methods"""
    print("=" * 80)
    print("YAHSHUA Payroll Authentication - Testing Multiple Methods")
    print("=" * 80)

    url_with_slash = "https://www.yahshuapayroll.com/api/login/"
    url_without_slash = "https://www.yahshuapayroll.com/api/login"

    credentials = {
        "username": "timekeeping@sanbeda.com",
        "password": "722436Aa!"
    }

    print(f"\nCredentials:")
    print(f"  Username: {credentials['username']}")
    print(f"  Password: {credentials['password']}")

    # Method 1: JSON body with trailing slash
    print("\n" + "-" * 60)
    print("Method 1: JSON body to /api/login/")
    print("-" * 60)
    try:
        response = requests.post(
            url_with_slash,
            json=credentials,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✅ SUCCESS!")
            return True
    except Exception as e:
        print(f"Error: {e}")

    # Method 2: Form data
    print("\n" + "-" * 60)
    print("Method 2: Form data to /api/login/")
    print("-" * 60)
    try:
        response = requests.post(
            url_with_slash,
            data=credentials,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✅ SUCCESS!")
            return True
    except Exception as e:
        print(f"Error: {e}")

    # Method 3: JSON without trailing slash
    print("\n" + "-" * 60)
    print("Method 3: JSON body to /api/login (no slash)")
    print("-" * 60)
    try:
        response = requests.post(
            url_without_slash,
            json=credentials,
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✅ SUCCESS!")
            return True
    except Exception as e:
        print(f"Error: {e}")

    # Method 4: With explicit Content-Type header
    print("\n" + "-" * 60)
    print("Method 4: JSON with explicit headers")
    print("-" * 60)
    try:
        response = requests.post(
            url_with_slash,
            data=json.dumps(credentials),
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        if response.status_code == 200:
            print("✅ SUCCESS!")
            return True
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "=" * 80)
    print("❌ All methods failed")
    print("=" * 80)
    return False

if __name__ == '__main__':
    test_yahshua()
