# San Beda Integration Tool

A desktop application that bridges San Beda's on-premise timekeeping system with The Abba's cloud payroll system.

## Overview

The San Beda Integration Tool automates the process of synchronizing timesheet data between two systems:

- **Pull**: Fetches timesheet data from San Beda's on-premise database
- **Push**: Syncs timesheet data to The Abba's cloud payroll system

### Features

- **Offline-First Architecture**: Works without internet connection, syncs when online
- **Automated Sync**: Configurable intervals for automatic pull and push operations
- **Manual Control**: Trigger sync operations on-demand
- **Data Management**: View, filter, and manage timesheet records
- **Error Handling**: Retry failed syncs with detailed error messages
- **Audit Logs**: Complete history of all sync operations

### Technology Stack

- **Backend**: Python 3.10 + PyQt6
- **Frontend**: Vue.js 3 + Vite + TailwindCSS
- **Database**: SQLite (local storage)
- **Communication**: QWebChannel (Python ↔ JavaScript bridge)

## Installation

### macOS

1. Download `SanBedaIntegration-v1.0.0.dmg`
2. Open the DMG file
3. Drag "San Beda Integration" to Applications folder
4. Launch from Applications

### Windows

1. Download `SanBedaIntegration-v1.0.0.zip`
2. Extract to desired location
3. Run `SanBedaIntegration.exe`

## Configuration

On first launch, configure the application:

1. Navigate to **Configuration** tab
2. Set up **Pull Configuration** (San Beda on-premise):
   - API Endpoint URL
   - Authentication type (Bearer, API Key, or Basic)
   - Credentials
   - Sync interval
3. Set up **Push Configuration** (Cloud Payroll):
   - API Endpoint URL
   - Authentication type
   - Credentials
   - Sync interval
4. Click **Test Connection** to verify each endpoint
5. Click **Save Configuration**

## Usage

### Dashboard

- View sync statistics (total, synced, pending, errors)
- Manually trigger pull/push operations
- See recent sync activity

### Timesheets

- Browse all timesheet records
- Filter by status (synced, pending, errors)
- Search by employee name or ID
- Retry failed syncs

### Configuration

- Update API endpoints
- Change authentication credentials
- Adjust sync intervals
- Test connections

### Logs

- View complete sync history
- Filter by type (pull/push) and status
- See detailed error messages
- Monitor sync duration

## API Integration

### Pull API (San Beda On-Premise)

The tool expects the pull endpoint to return data in this format:

```json
{
  "data": [
    {
      "sync_id": "1001_2734_20251108152755",
      "employee_id": 2734,
      "log_type": "in",
      "date": "2025-11-08",
      "time": "15:27",
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

### Push API (Cloud Payroll)

The tool posts data to the push endpoint in this format:

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

Expected response:

```json
{
  "id": 128906,
  "message": "Success"
}
```

**Note**: Adjust the data formats in `backend/services/pull_service.py` and `backend/services/push_service.py` to match your actual API specifications.

## Database Schema

The application stores data locally in SQLite with these main tables:

- **timesheet**: Timesheet entries with sync status
- **employee**: Employee reference data
- **sync_logs**: History of sync operations
- **api_config**: API configuration

For detailed schema, see `backend/database.py`.

## Troubleshooting

### Connection Issues

- Verify API endpoints are accessible
- Check firewall settings
- Ensure credentials are correct
- Use "Test Connection" button to diagnose

### Sync Failures

- Check error message in Logs tab
- Verify data format matches API expectations
- Retry individual failed records from Timesheets tab

### Application Won't Start

- Check log file: `sanbeda_integration.log`
- Ensure PyQt6 dependencies are installed
- On macOS, check System Preferences → Security for blocked apps

## Development

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for development setup and build instructions.

## Support

For issues or questions, contact The Abba support team.

## License

Copyright © 2025 The Abba. All rights reserved.
