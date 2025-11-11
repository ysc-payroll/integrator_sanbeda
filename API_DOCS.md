# San Beda Integration Tool - API Documentation

This document describes the expected API formats for integrating with San Beda's on-premise system and The Abba's cloud payroll system.

## Overview

The integration tool acts as a bridge between two systems:

1. **Pull API**: Fetches data from San Beda's on-premise timekeeping system
2. **Push API**: Sends data to The Abba's cloud payroll system

## Pull API (San Beda On-Premise)

### Endpoint Configuration

The pull endpoint URL should be configured in the application's Configuration view.

### Authentication

Supported authentication methods:

- **Bearer Token**: Authorization header with JWT token
- **API Key**: Custom header (X-API-Key) or query parameter
- **Basic Auth**: Base64-encoded username:password

### Request Format

**Method**: `GET`

**Headers**:
```
Authorization: Bearer <token>
# or
X-API-Key: <api-key>
# or
Authorization: Basic <base64-credentials>
```

**Query Parameters** (optional):
```
?from_date=2025-11-08T00:00:00&limit=1000
```

### Expected Response Format

```json
{
  "data": [
    {
      "sync_id": "1001_2734_20251108152755",
      "employee_id": 2734,
      "log_type": "in",
      "date": "2025-11-08",
      "time": "15:27",
      "photo_path": "/path/to/photo.jpg"
    },
    {
      "sync_id": "1001_2734_20251108170530",
      "employee_id": 2734,
      "log_type": "out",
      "date": "2025-11-08",
      "time": "17:05",
      "photo_path": null
    }
  ],
  "employees": [
    {
      "id": 2734,
      "name": "John Doe",
      "employee_code": "EMP001",
      "employee_number": 8104
    }
  ]
}
```

### Field Descriptions

#### Timesheet Data (`data` array)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sync_id` | string | Yes | Unique identifier for this timesheet entry. Format: `{company_id}_{employee_id}_{timestamp}` |
| `employee_id` | integer | Yes | Employee ID (matches `employees.id`) |
| `log_type` | string | Yes | Either "in" or "out" |
| `date` | string | Yes | Date in YYYY-MM-DD format |
| `time` | string | Yes | Time in HH:MM format (24-hour) |
| `photo_path` | string | No | Path to photo file (optional) |

#### Employee Data (`employees` array)

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | integer | Yes | Unique employee ID |
| `name` | string | Yes | Employee full name |
| `employee_code` | string | No | Employee code/identifier |
| `employee_number` | integer | No | Employee number for identification |

### Success Response

**Status Code**: `200 OK`

### Error Responses

**401 Unauthorized**: Invalid credentials
```json
{
  "error": "Invalid authentication credentials"
}
```

**500 Internal Server Error**: Server error
```json
{
  "error": "Internal server error",
  "message": "Database connection failed"
}
```

### Implementation Example

```python
# In backend/services/pull_service.py

def process_timesheet(self, ts_data):
    """Process timesheet data from API response"""
    employee = self.database.get_employee_by_backend_id(ts_data['employee_id'])
    if not employee:
        logger.warning(f"Employee {ts_data['employee_id']} not found")
        return False

    result = self.database.add_timesheet_entry(
        sync_id=ts_data['sync_id'],
        employee_id=employee['id'],
        log_type=ts_data['log_type'],
        date=ts_data['date'],
        time=ts_data['time'],
        photo_path=ts_data.get('photo_path')
    )
    return result is not None
```

## Push API (Cloud Payroll)

### Endpoint Configuration

The push endpoint URL should be configured in the application's Configuration view.

### Authentication

Same authentication methods as Pull API:

- Bearer Token
- API Key
- Basic Auth

### Request Format

**Method**: `POST`

**Headers**:
```
Content-Type: application/json
Authorization: Bearer <token>
```

**Request Body**:
```json
{
  "sync_id": "1001_2734_20251108152755",
  "employee_id": 2734,
  "employee_name": "John Doe",
  "log_type": "in",
  "date": "2025-11-08",
  "time": "15:27",
  "photo_path": null,
  "created_at": "2025-11-08T15:27:55"
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sync_id` | string | Yes | Unique identifier from source system |
| `employee_id` | integer | Yes | Employee ID in backend system |
| `employee_name` | string | Yes | Employee full name |
| `log_type` | string | Yes | Either "in" or "out" |
| `date` | string | Yes | Date in YYYY-MM-DD format |
| `time` | string | Yes | Time in HH:MM format |
| `photo_path` | string | No | Path to photo (optional) |
| `created_at` | string | Yes | ISO 8601 timestamp of creation |

### Expected Response Format

#### Success Response

**Status Code**: `200 OK` or `201 Created`

```json
{
  "id": 128906,
  "message": "Timesheet entry created successfully",
  "sync_id": "1001_2734_20251108152755"
}
```

**Required Fields**:
- `id` or `timesheet_id`: Backend database ID for this record

#### Duplicate Entry Response

**Status Code**: `409 Conflict`

```json
{
  "error": "Duplicate entry",
  "message": "Timesheet entry already exists",
  "existing_id": 128906
}
```

The integration tool will use `existing_id` to mark the record as synced.

### Error Responses

**400 Bad Request**: Invalid data
```json
{
  "error": "Validation error",
  "message": "Invalid log_type value"
}
```

**401 Unauthorized**: Invalid credentials
```json
{
  "error": "Authentication failed"
}
```

**500 Internal Server Error**: Server error
```json
{
  "error": "Internal server error"
}
```

### Implementation Example

```python
# In backend/services/push_service.py

def push_timesheet(self, timesheet, config, headers):
    """Push a single timesheet entry to cloud payroll"""
    payload = {
        'sync_id': timesheet['sync_id'],
        'employee_id': timesheet['employee_backend_id'],
        'employee_name': timesheet['employee_name'],
        'log_type': timesheet['log_type'],
        'date': timesheet['date'],
        'time': timesheet['time'],
        'photo_path': timesheet.get('photo_path'),
        'created_at': timesheet['created_at']
    }

    response = self.session.post(
        config['push_url'],
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code in [200, 201]:
        response_data = response.json()
        backend_id = response_data.get('id') or response_data.get('timesheet_id')

        if backend_id:
            self.database.mark_timesheet_synced(timesheet['id'], backend_id)
            return True

    elif response.status_code == 409:
        # Duplicate - try to get existing ID
        response_data = response.json()
        existing_id = response_data.get('existing_id')
        if existing_id:
            self.database.mark_timesheet_synced(timesheet['id'], existing_id)
            return True

    return False
```

## Customization Guide

### Adapting to Different API Formats

If your API uses a different format, modify these files:

#### Pull Service (`backend/services/pull_service.py`)

**Change request parameters**:
```python
def pull_data(self):
    # Customize query parameters
    params = {
        'start_date': config.get('last_pull_at'),
        'end_date': datetime.now().isoformat(),
        'page_size': 1000
    }

    response = self.session.get(
        config['pull_url'],
        headers=headers,
        params=params,
        timeout=30
    )
```

**Change response parsing**:
```python
def process_timesheet(self, ts_data):
    # Map API fields to database fields
    return self.database.add_timesheet_entry(
        sync_id=ts_data['id'],  # Different field name
        employee_id=employee['id'],
        log_type=ts_data['type'].lower(),  # Convert format
        date=ts_data['log_date'],  # Different field name
        time=ts_data['log_time'],
        photo_path=ts_data.get('image_url')
    )
```

#### Push Service (`backend/services/push_service.py`)

**Change request payload**:
```python
def push_timesheet(self, timesheet, config, headers):
    # Customize payload format
    payload = {
        'id': timesheet['sync_id'],
        'emp_id': timesheet['employee_backend_id'],
        'type': timesheet['log_type'].upper(),
        'timestamp': f"{timesheet['date']}T{timesheet['time']}:00"
    }

    response = self.session.post(
        config['push_url'],
        headers=headers,
        json=payload,
        timeout=30
    )
```

**Change response parsing**:
```python
if response.status_code == 200:
    response_data = response.json()
    # Extract ID from different response structure
    backend_id = response_data['data']['timesheet']['id']
    self.database.mark_timesheet_synced(timesheet['id'], backend_id)
```

### Adding Custom Headers

```python
# In pull_service.py or push_service.py
def build_auth_headers(self, config):
    headers = {}

    # Standard authentication
    auth_type = config.get('pull_auth_type', '').lower()
    credentials = config.get('pull_credentials')

    if auth_type == 'bearer':
        headers['Authorization'] = f'Bearer {credentials}'

    # Custom headers
    headers['X-Client-Version'] = '1.0.0'
    headers['X-Client-ID'] = 'sanbeda-integration'

    return headers
```

### Adding Request Retry Logic

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def __init__(self, database):
    self.database = database
    self.session = requests.Session()

    # Configure retry strategy
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    self.session.mount('http://', adapter)
    self.session.mount('https://', adapter)
```

## Testing

### Mock Endpoints

For testing without actual APIs, you can use mock endpoints:

```python
# In pull_service.py
def pull_data(self):
    if config['pull_url'] == 'http://localhost:3000/mock':
        # Return mock data
        return True, "Mock pull successful", {
            'processed': 10,
            'success': 10,
            'failed': 0
        }
    # ... normal logic
```

### Testing Tools

- **Postman**: Test API endpoints manually
- **httpbin.org**: Test HTTP requests
- **mockapi.io**: Create mock REST APIs
- **json-server**: Local mock API server

## Troubleshooting

### Common Issues

**Connection Refused**:
- Verify endpoint URL is correct
- Check firewall settings
- Ensure service is running

**Authentication Failed**:
- Verify credentials are correct
- Check token expiration
- Ensure proper header format

**Data Format Errors**:
- Check field names match expected format
- Verify data types (string vs integer)
- Validate date/time formats

**Timeout Errors**:
- Increase timeout value
- Check network connectivity
- Verify API performance

### Debug Logging

Enable detailed logging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

View logs in `sanbeda_integration.log`.

## Support

For API integration questions, contact The Abba development team.
