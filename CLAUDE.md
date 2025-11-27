# San Beda Integration Tool - Developer Documentation

> **For AI Assistants (Claude):** This document provides comprehensive context for understanding and working with this codebase. Read this first before making changes.

## Project Overview

**San Beda Integration Tool** is a desktop application that bridges two systems:
1. **San Beda On-Premise Timekeeping** - Source of employee attendance/timesheet data
2. **YAHSHUA Cloud Payroll** - Destination for syncing timesheet data

The app runs on the client's local machine, pulls data from their on-premise server, and pushes it to the cloud payroll system.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+ with PyQt6 |
| Frontend | Vue.js 3 + Vite + TailwindCSS |
| Database | SQLite (local) |
| Communication | QWebChannel (Python ↔ JavaScript bridge) |
| Packaging | PyInstaller (creates standalone executables) |
| CI/CD | GitHub Actions |

## Project Structure

```
sanbeda-integration/
├── backend/                      # Python backend
│   ├── main.py                   # Application entry point
│   ├── bridge.py                 # QWebChannel bridge (exposes Python methods to JS)
│   ├── database.py               # SQLite database manager
│   ├── services/
│   │   ├── auth_service.py       # San Beda authentication (MD5 challenge-response)
│   │   ├── pull_service.py       # Fetch data from San Beda API
│   │   ├── push_service.py       # Push data to YAHSHUA API
│   │   └── scheduler.py          # Background sync scheduler
│   ├── sanbeda-integration.spec  # PyInstaller config (macOS)
│   ├── sanbeda-integration-windows.spec  # PyInstaller config (Windows)
│   ├── create_dmg.sh             # macOS DMG creation script
│   └── requirements.txt          # Python dependencies
│
├── frontend/                     # Vue.js frontend
│   ├── src/
│   │   ├── App.vue               # Main app with sidebar navigation
│   │   ├── components/
│   │   │   ├── DashboardView.vue    # Stats + manual sync buttons
│   │   │   ├── TimesheetView.vue    # Timesheet data table
│   │   │   ├── ConfigView.vue       # API configuration
│   │   │   ├── LogsView.vue         # Sync activity logs
│   │   │   ├── SyncProgressModal.vue # Push sync progress indicator
│   │   │   └── ToastNotification.vue # Toast messages
│   │   ├── services/
│   │   │   └── bridge.js            # QWebChannel client wrapper
│   │   └── composables/
│   │       └── useToast.js          # Toast notification composable
│   ├── package.json
│   └── vite.config.js
│
├── icons/                        # App icons
│   ├── icon.icns                 # macOS icon
│   ├── icon_1024x1024.png        # Source PNG
│   └── create_ico.py             # Generates Windows ICO
│
├── .github/workflows/
│   └── build-release.yml         # GitHub Actions build workflow
│
└── docs/                         # Documentation (you are here)
```

---

## Architecture

### How the App Works

```
┌─────────────────────────────────────────────────────────────┐
│                     Desktop Application                      │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                    PyQt6 Window                         ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │              QWebEngineView (Chromium)              │││
│  │  │  ┌───────────────────────────────────────────────┐  │││
│  │  │  │            Vue.js Frontend (HTML/JS/CSS)      │  │││
│  │  │  └───────────────────────────────────────────────┘  │││
│  │  │                        ↕ QWebChannel                │││
│  │  └─────────────────────────────────────────────────────┘││
│  │                           ↕                              ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │              Python Backend (Bridge)                │││
│  │  │    Database │ AuthService │ PullService │ PushService│││
│  │  └─────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
          ↓                                        ↓
┌──────────────────────┐              ┌──────────────────────┐
│  San Beda On-Premise │              │   YAHSHUA Cloud      │
│  Timekeeping Server  │              │   Payroll API        │
│  (HTTP, MD5 Auth)    │              │   (HTTPS, Bearer)    │
└──────────────────────┘              └──────────────────────┘
```

### Communication Flow

1. **Frontend → Backend:** Vue.js calls methods on `window.bridge` object
2. **Backend → Frontend:** Python emits signals that trigger JavaScript events
3. **Bridge (bridge.py):** Exposes Python methods as `@pyqtSlot` decorators

---

## Authentication Systems

### 1. San Beda Authentication (Pull)

**Location:** `backend/services/auth_service.py`

San Beda uses a **challenge-response authentication** with 5-round MD5 hashing:

```
Step 1: Client sends username
        → Server returns: randomKey, realm, encryptType

Step 2: Client calculates signature:
        temp1 = MD5(password)
        temp2 = MD5(userName + temp1)
        temp3 = MD5(temp2)
        temp4 = MD5(userName + ":" + realm + ":" + temp3)
        signature = MD5(temp4 + ":" + randomKey)

Step 3: Client sends signature + RSA public key
        → Server returns: loginToken
```

**Token Storage:** Stored in `api_config.login_token` in SQLite database.

### 2. YAHSHUA Authentication (Push)

**Location:** `backend/services/push_service.py`

YAHSHUA uses **standard Bearer token** authentication:

```
POST /api/auth/login
Body: { "email": "user@example.com", "password": "..." }
Response: { "token": "eyJ...", "user_logged": "John Doe", ... }
```

**Token Storage:** Stored in `api_config.push_token` in SQLite database.

---

## Data Flow

### Pull Flow (San Beda → Local Database)

**Location:** `backend/services/pull_service.py`

```
1. Authenticate with San Beda (get/refresh token)
2. GET /brms/api/v1.0/att/attLogs?beginTime=...&endTime=...
3. Parse response (employee attendance logs)
4. Upsert into local SQLite `timesheet` table
5. Mark records as synced_at = NULL (pending push)
```

**Key Fields Pulled:**
- `employee_code` - Employee ID
- `punch_time` - Timestamp of clock in/out
- `device_name` - Which device recorded the punch
- `verify_mode` - Fingerprint, face, card, etc.

### Push Flow (Local Database → YAHSHUA)

**Location:** `backend/services/push_service.py`

```
1. Authenticate with YAHSHUA (get/refresh token)
2. Query local DB for unsynced records (synced_at IS NULL, no error)
3. Batch records (50 per batch) to avoid API limits
4. For each batch:
   POST /api/external/bulk
   Body: [{ "employee_code": "...", "time_in": "...", "time_out": "..." }, ...]
5. Update local records:
   - Success: Set synced_at = NOW
   - Failure: Set sync_error_message = error
6. Emit progress updates to frontend
```

**Batching:** Records are pushed in groups of 50 to prevent timeouts and allow progress tracking.

---

## Database Schema

**Location:** `backend/database.py`

### Tables

#### `api_config` (singleton - always 1 row)
```sql
- pull_host          -- San Beda server IP (e.g., "192.168.9.125")
- pull_username      -- San Beda username
- pull_password      -- San Beda password
- login_token        -- San Beda auth token
- push_url           -- YAHSHUA API URL
- push_username      -- YAHSHUA email
- push_password      -- YAHSHUA password
- push_token         -- YAHSHUA Bearer token
- push_user_logged   -- YAHSHUA user display name
- pull_interval_minutes  -- Auto-pull interval (0 = disabled)
- push_interval_minutes  -- Auto-push interval (0 = disabled)
```

#### `timesheet`
```sql
- id                 -- Primary key
- employee_code      -- Employee ID from San Beda
- punch_time         -- Original punch timestamp
- device_name        -- Source device
- verify_mode        -- Verification method
- pulled_at          -- When pulled from San Beda
- synced_at          -- When pushed to YAHSHUA (NULL = pending)
- sync_error_message -- Error if push failed (NULL = no error)
```

#### `sync_logs`
```sql
- id
- sync_type          -- 'pull', 'push', or 'config'
- status             -- 'started', 'success', 'error'
- records_processed  -- Total records attempted
- records_success    -- Successfully processed
- records_failed     -- Failed records
- started_at
- completed_at
- error_message
```

---

## Bridge API Reference

**Location:** `backend/bridge.py`

The Bridge class exposes these methods to the frontend via QWebChannel:

### Timesheet Methods
| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `getTimesheetStats()` | - | JSON | Get counts (total, synced, pending, failed) |
| `getAllTimesheets(limit, offset)` | int, int | JSON | Paginated timesheet list |
| `getUnsyncedTimesheets(limit)` | int | JSON | Get pending timesheets |
| `retryFailedTimesheet(id)` | int | JSON | Clear error to retry sync |

### Sync Methods
| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `startPullSync()` | - | JSON | Trigger manual pull (synchronous) |
| `startPushSync()` | - | JSON | Trigger manual push (async, emits progress) |
| `getSyncLogs()` | - | JSON | Get sync activity logs |

### Config Methods
| Method | Parameters | Returns | Description |
|--------|------------|---------|-------------|
| `getApiConfig()` | - | JSON | Get config (credentials masked) |
| `updateApiConfig(json)` | string | JSON | Update configuration |
| `testConnection(type)` | 'pull'/'push' | JSON | Test API connectivity |
| `loginPush(user, pass)` | string, string | JSON | Login to YAHSHUA |
| `logoutPush()` | - | JSON | Logout from YAHSHUA |

### Signals (Backend → Frontend)
| Signal | Payload | Description |
|--------|---------|-------------|
| `syncProgressUpdated` | JSON | Push progress (batch X of Y) |
| `syncCompleted` | JSON | Sync finished (success/error) |

---

## Development Setup

### Prerequisites
- Python 3.10+
- Node.js 20+
- macOS or Windows

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend Setup
```bash
cd frontend
npm install
```

### Running in Development

**Terminal 1 - Frontend (Vite dev server):**
```bash
cd frontend
npm run dev
# Runs on http://localhost:5173
```

**Terminal 2 - Backend:**
```bash
cd backend
source venv/bin/activate
python main.py
# Opens PyQt window pointing to Vite dev server
```

The app detects `IS_FROZEN` (PyInstaller) to determine dev vs production mode:
- **Dev mode:** Loads frontend from `http://localhost:5173`
- **Production:** Loads frontend from bundled files via local HTTP server

---

## Building for Production

### Automated (GitHub Actions)

Push a version tag to trigger automatic builds:

```bash
git tag v1.0.7
git push origin v1.0.7
```

This creates a GitHub Release with:
- `SanBedaIntegration-v1.0.7.dmg` (macOS)
- `SanBedaIntegration-v1.0.7-Windows.zip` (Windows)

### Manual Build

**macOS:**
```bash
cd frontend && npm run build && cd ..
cd backend
source venv/bin/activate
pip install pyinstaller
pyinstaller --clean --distpath ../dist sanbeda-integration.spec
./create_dmg.sh 1.0.7
```

**Windows:**
```bash
cd frontend && npm run build && cd ..
cd icons && python create_ico.py && cd ..
cd backend
pip install pyinstaller
pyinstaller --clean --distpath ../dist sanbeda-integration-windows.spec
```

---

## Version Management

**Update version in these files before releasing:**

| File | Location |
|------|----------|
| `backend/bridge.py` | Line ~311: `"version": "X.X.X"` |
| `backend/main.py` | Line ~112: Tkinter splash `"Version X.X.X"` |
| `backend/main.py` | Line ~251: Qt splash `"Version X.X.X"` |
| `frontend/src/App.vue` | Line ~58: `ref('X.X.X')` |

---

## Troubleshooting

### Logs

**macOS (packaged):** `/tmp/sanbeda_integration.log`
**Windows (packaged):** `%TEMP%\sanbeda_integration.log`
**Development:** `./sanbeda_integration.log`

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| App bounces in dock, doesn't open | First launch, QtWebEngine initializing | Wait 1-2 minutes, splash should appear |
| "Module not found: Crypto" | Missing pycryptodome | Add to requirements.txt and spec hiddenimports |
| 404 on frontend load | Wrong frontend path | Check `sys._MEIPASS` path in packaged app |
| Push fails silently | Token expired | Re-login in Configuration |

### Debug Mode

To enable verbose logging, check `IS_FROZEN` in main.py - dev mode uses DEBUG level.

---

## Key Implementation Notes

### Threading
- **Push sync runs in a background thread** to avoid blocking the UI
- Progress updates are emitted via Qt signals which are thread-safe
- The scheduler runs in a daemon thread

### Startup Optimization
- **Tkinter splash** shows immediately (before PyQt6 loads)
- **Qt splash** replaces it after imports complete
- First launch is slow (1-2 min) due to QtWebEngine cache creation

### Error Handling
- Failed push records are marked with `sync_error_message`
- Retry clears the error message, allowing re-sync
- All sync operations are logged to `sync_logs` table

---

## API Endpoints Reference

### San Beda API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/brms/api/v1.0/accounts/authorize` | POST | Authentication |
| `/brms/api/v1.0/att/attLogs` | GET | Get attendance logs |

### YAHSHUA API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/login` | POST | Authentication |
| `/api/external/bulk` | POST | Bulk timesheet upload |

---

## Future Improvements

Potential enhancements for future development:
1. **Retry queue** - Automatic retry of failed records
2. **Conflict resolution** - Handle duplicate punches
3. **Offline indicator** - Show network status
4. **Export to CSV** - Manual data export
5. **Multi-company support** - Support multiple YAHSHUA companies


## Credentials

## Pull Config
1. Ask the IT from San Beda about their credentials in DSS
2. Make sure that this account has an access to read the attendance in DSS
3. If they change the password of that credential, we need to do Reconnect to get a new token


## Push Config
1. The HR should provide the credential for Timekeeping account.
2. The HR should create a new user under User module and then add a "Timekeeper Access" under "View Rights" module


## Setup

1. Install the Integration App (wait for 1-2 minutes for first initialization)
2. Go to Config
3. Setup Pull and Push config
4. You can click the "Pull" button in Dashboard right away or just wait for the auto download and auto upload.
