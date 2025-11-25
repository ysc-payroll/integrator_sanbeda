"""
Test San Beda Authentication with detailed logging
"""
import requests
import hashlib
import json

def test_auth_methods():
    """Test different authentication methods"""
    host = '192.168.9.125'
    username = 'system'
    password = 'admin1234567'
    auth_url = f"http://{host}/brms/api/v1.0/accounts/authorize"

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'San Beda Integration Tool/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json;charset=UTF-8'
    })

    # Step 1: Get challenge
    print("=" * 80)
    print("STEP 1: Getting challenge")
    print("=" * 80)

    payload1 = {
        "userName": username,
        "ipAddress": "",
        "clientType": "WINPC_V2"
    }

    print(f"Request URL: {auth_url}")
    print(f"Payload: {json.dumps(payload1, indent=2)}")

    response1 = session.post(auth_url, json=payload1, timeout=30)
    print(f"Response Status: {response1.status_code}")
    print(f"Response: {json.dumps(response1.json(), indent=2)}")

    if response1.status_code != 401:
        print("ERROR: Expected 401 challenge response")
        return

    challenge = response1.json()
    random_key = challenge.get('randomKey')
    realm = challenge.get('realm')

    print(f"\nChallenge received:")
    print(f"  randomKey: {random_key}")
    print(f"  realm: {realm}")

    # Try different encryption methods
    print("\n" + "=" * 80)
    print("STEP 2: Trying different encryption methods")
    print("=" * 80)

    methods = [
        {
            "name": "Method 1: MD5(MD5(password) + randomKey)",
            "encrypt": lambda: hashlib.md5((hashlib.md5(password.encode()).hexdigest() + random_key).encode()).hexdigest()
        },
        {
            "name": "Method 2: MD5(password + randomKey)",
            "encrypt": lambda: hashlib.md5((password + random_key).encode()).hexdigest()
        },
        {
            "name": "Method 3: MD5(randomKey + MD5(password))",
            "encrypt": lambda: hashlib.md5((random_key + hashlib.md5(password.encode()).hexdigest()).encode()).hexdigest()
        },
        {
            "name": "Method 4: MD5(randomKey + password)",
            "encrypt": lambda: hashlib.md5((random_key + password).encode()).hexdigest()
        }
    ]

    for i, method in enumerate(methods, 1):
        print(f"\n{'-' * 80}")
        print(f"Trying {method['name']}")
        print(f"{'-' * 80}")

        encrypted_password = method['encrypt']()
        print(f"Encrypted password: {encrypted_password}")

        payload2 = {
            "userName": username,
            "password": encrypted_password,
            "ipAddress": "",
            "clientType": "WINPC_V2",
            "randomKey": random_key,
            "realm": realm
        }

        print(f"Payload: {json.dumps(payload2, indent=2)}")

        response2 = session.post(auth_url, json=payload2, timeout=30)
        print(f"Response Status: {response2.status_code}")

        try:
            response_json = response2.json()
            print(f"Response: {json.dumps(response_json, indent=2)}")

            if response2.status_code == 200 and response_json.get('loginToken'):
                print(f"\n{'=' * 80}")
                print(f"✅ SUCCESS! {method['name']} worked!")
                print(f"{'=' * 80}")
                print(f"Login Token: {response_json.get('loginToken')}")
                return True
        except Exception as e:
            print(f"Response Text: {response2.text}")
            print(f"Error parsing JSON: {e}")

    print(f"\n{'=' * 80}")
    print("❌ All methods failed")
    print(f"{'=' * 80}")
    return False

if __name__ == '__main__':
    test_auth_methods()
