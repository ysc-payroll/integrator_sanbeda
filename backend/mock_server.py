"""
Mock San Beda Server for Testing
Simulates the on-premise timekeeping API responses
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import hashlib

# Simulated latency in seconds (adjust as needed)
LATENCY_MIN = 1.0  # Minimum delay
LATENCY_MAX = 3.0  # Maximum delay

# Mock data - Generate 100 employees for more realistic testing
MOCK_EMPLOYEES = [
    {"code": f"EMP{i:03d}", "name": f"Employee {i:03d}"}
    for i in range(1, 101)
]

# Store token for auth simulation
VALID_TOKEN = None


class MockSanBedaHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[MockServer] {format % args}")

    def simulate_latency(self):
        """Add random delay to simulate network latency"""
        delay = random.uniform(LATENCY_MIN, LATENCY_MAX)
        print(f"[MockServer] Simulating {delay:.1f}s latency...")
        time.sleep(delay)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Subject-Token')
        self.end_headers()

    def do_GET(self):
        self.simulate_latency()

        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # Check auth token
        token = self.headers.get('X-Subject-Token')
        if path != '/brms/api/v1.0/accounts/authorize' and token != VALID_TOKEN:
            self.send_json({"code": 401, "desc": "Unauthorized"}, 401)
            return

        # Attendance records endpoint
        if '/attendance/record-info-report/page' in path:
            self.handle_attendance(params)
        else:
            self.send_json({"code": 404, "desc": "Not found"}, 404)

    def do_POST(self):
        self.simulate_latency()

        global VALID_TOKEN
        parsed = urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length > 0 else ''

        # Auth endpoint
        if '/accounts/authorize' in path:
            self.handle_auth(body)
            return

        self.send_json({"code": 404, "desc": "Not found"}, 404)

    def handle_auth(self, body):
        """Handle San Beda authentication flow"""
        global VALID_TOKEN

        try:
            data = json.loads(body) if body else {}
        except:
            data = {}

        print(f"[MockServer] Auth request: {data}")

        # Check if this is Step 1 (no signature) or Step 2 (has signature)
        if 'signature' not in data:
            # Step 1: Return challenge with 401
            random_key = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:16]
            print(f"[MockServer] Step 1: Sending challenge with randomKey={random_key}")

            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                "randomKey": random_key,
                "realm": "BRMS",
                "encryptType": "MD5"
            }).encode())
        else:
            # Step 2: Validate signature and return token
            VALID_TOKEN = hashlib.md5(str(datetime.now()).encode()).hexdigest()
            print(f"[MockServer] Step 2: Auth successful, token={VALID_TOKEN[:16]}...")

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('X-Subject-Token', VALID_TOKEN)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Expose-Headers', 'X-Subject-Token')
            self.end_headers()
            self.wfile.write(json.dumps({
                "token": VALID_TOKEN
            }).encode())

    def handle_attendance(self, params):
        """Generate mock attendance records"""
        start_time = params.get('startTime', [''])[0]
        end_time = params.get('endTime', [''])[0]
        page = int(params.get('page', ['1'])[0])
        page_size = int(params.get('pageSize', ['100'])[0])

        print(f"[MockServer] Attendance request: {start_time} to {end_time}, page {page}")

        # Parse dates
        try:
            start_date = datetime.strptime(start_time.split()[0], "%Y-%m-%d")
            end_date = datetime.strptime(end_time.split()[0], "%Y-%m-%d")
        except:
            start_date = datetime.now() - timedelta(days=1)
            end_date = datetime.now()

        # Generate mock records
        records = []
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")

            for emp in MOCK_EMPLOYEES:
                # Random IN time between 7:30 and 9:00
                in_hour = random.randint(7, 8)
                in_min = random.randint(0, 59)

                # Random OUT time between 17:00 and 19:00
                out_hour = random.randint(17, 19)
                out_min = random.randint(0, 59)

                records.append({
                    "code": emp["code"],
                    "name": emp["name"],
                    "attendanceDate": date_str,
                    "signInTime": f"{in_hour:02d}:{in_min:02d}",
                    "signOutTime": f"{out_hour:02d}:{out_min:02d}"
                })

            current_date += timedelta(days=1)

        # Paginate
        total = len(records)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_data = records[start_idx:end_idx]

        print(f"[MockServer] Returning {len(page_data)} records (total: {total})")

        self.send_json({
            "code": 1000,
            "desc": "success",
            "data": {
                "pageData": page_data,
                "total": total,
                "page": page,
                "pageSize": page_size
            }
        })


def run_mock_server(port=8080):
    server = HTTPServer(('localhost', port), MockSanBedaHandler)
    print(f"=" * 50)
    print(f"Mock San Beda Server running on http://localhost:{port}")
    print(f"=" * 50)
    print(f"\nConfigure the app with:")
    print(f"  Host: localhost:{port}")
    print(f"  Username: system")
    print(f"  Password: test123")
    print(f"\nPress Ctrl+C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down mock server...")
        server.shutdown()


if __name__ == '__main__':
    run_mock_server()
