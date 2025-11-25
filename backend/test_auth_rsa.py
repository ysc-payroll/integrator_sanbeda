"""
Test San Beda Authentication with RSA encryption
"""
import requests
import hashlib
import json
import base64
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5

def test_rsa_auth():
    """Test RSA-based authentication"""
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

    response1 = session.post(auth_url, json=payload1, timeout=30)
    print(f"Response Status: {response1.status_code}")

    if response1.status_code != 401:
        print("ERROR: Expected 401 challenge response")
        return

    challenge = response1.json()
    random_key = challenge.get('randomKey')
    realm = challenge.get('realm')
    public_key_str = challenge.get('publickey')

    print(f"\nChallenge received:")
    print(f"  randomKey: {random_key}")
    print(f"  realm: {realm}")
    print(f"  publickey: {public_key_str[:50]}...")

    # Step 2: RSA encrypt password
    print("\n" + "=" * 80)
    print("STEP 2: RSA Encryption Methods")
    print("=" * 80)

    try:
        # Parse the public key
        public_key_der = base64.b64decode(public_key_str)
        public_key = RSA.import_key(public_key_der)
        cipher = PKCS1_v1_5.new(public_key)

        # Try different combinations
        test_cases = [
            {
                "name": "RSA(password)",
                "data": password
            },
            {
                "name": "RSA(MD5(password))",
                "data": hashlib.md5(password.encode()).hexdigest()
            },
            {
                "name": "RSA(password + randomKey)",
                "data": password + random_key
            },
            {
                "name": "RSA(MD5(password) + randomKey)",
                "data": hashlib.md5(password.encode()).hexdigest() + random_key
            },
            {
                "name": "RSA(MD5(MD5(password) + randomKey))",
                "data": hashlib.md5((hashlib.md5(password.encode()).hexdigest() + random_key).encode()).hexdigest()
            }
        ]

        for test_case in test_cases:
            print(f"\n{'-' * 80}")
            print(f"Trying {test_case['name']}")
            print(f"{'-' * 80}")

            # RSA encrypt the data
            encrypted_data = cipher.encrypt(test_case['data'].encode())
            encrypted_password = base64.b64encode(encrypted_data).decode('utf-8')

            print(f"Plaintext: {test_case['data'][:30]}...")
            print(f"Encrypted (first 50 chars): {encrypted_password[:50]}...")

            payload2 = {
                "userName": username,
                "password": encrypted_password,
                "ipAddress": "",
                "clientType": "WINPC_V2",
                "randomKey": random_key,
                "realm": realm
            }

            response2 = session.post(auth_url, json=payload2, timeout=30)
            print(f"Response Status: {response2.status_code}")

            try:
                response_json = response2.json()

                if response2.status_code == 200 and response_json.get('loginToken'):
                    print(f"\n{'=' * 80}")
                    print(f"✅ SUCCESS! {test_case['name']} worked!")
                    print(f"{'=' * 80}")
                    print(f"Login Token: {response_json.get('loginToken')}")
                    return True
                else:
                    # Show first part of response
                    response_str = json.dumps(response_json, indent=2)
                    if len(response_str) > 200:
                        response_str = response_str[:200] + "..."
                    print(f"Response: {response_str}")
            except Exception as e:
                print(f"Response Text (first 200 chars): {response2.text[:200]}")
                print(f"Error parsing JSON: {e}")

    except Exception as e:
        print(f"ERROR with RSA encryption: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n{'=' * 80}")
    print("❌ All RSA methods failed")
    print(f"{'=' * 80}")
    return False

if __name__ == '__main__':
    test_rsa_auth()
