# San Beda Integration Tool - Build Guide

Complete guide for setting up the development environment and building the application.

## Prerequisites

### Required Software

- **Python 3.10** or higher
- **Node.js 18** or higher (with npm)
- **Git** for version control

### macOS Specific

- Xcode Command Line Tools: `xcode-select --install`
- Homebrew (recommended): https://brew.sh

### Windows Specific

- Visual C++ Build Tools (for Python packages)
- Windows SDK

## Development Setup

### 1. Clone Repository

```bash
git clone <repository-url>
cd sanbeda-integration
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install PyInstaller for building
pip install pyinstaller
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm run build
```

## Development Workflow

### Two-Terminal Development

The recommended development workflow uses two terminals for hot reload:

**Terminal 1 - Frontend Dev Server:**

```bash
cd frontend
npm run dev
```

This starts Vite dev server on http://localhost:5173 with hot module replacement.

**Terminal 2 - Python Application:**

```bash
cd backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
export DEV_MODE=true      # or set DEV_MODE=true on Windows
python main.py
```

The Python app will load the frontend from the Vite dev server.

### Quick Start Script

```bash
./run_dev.sh  # macOS/Linux
```

This script checks dependencies and provides instructions for running in dev mode.

## Building for Production

### macOS Build

**IMPORTANT**: Before building for production, disable DEV_MODE:

Edit `backend/main.py` and change:
```python
DEV_MODE = True  # Set to False for production builds
```
to:
```python
DEV_MODE = False  # Production mode
```

Then build:

```bash
# One-command build
./build_release.sh

# Or manual steps:
cd frontend
npm run build
cd ../backend
source venv/bin/activate
pyinstaller --clean --distpath ../dist --workpath build sanbeda-integration.spec
```

Output: `dist/San Beda Integration.app`

### Create macOS DMG Installer

```bash
cd backend
./create_dmg.sh
```

Output: `dist/SanBedaIntegration-v1.0.0.dmg`

### Windows Build

```batch
REM One-command build
build_release_windows.bat

REM Or manual steps:
cd frontend
npm run build
cd ..\backend
call venv\Scripts\activate
pyinstaller --clean --distpath ..\dist --workpath build sanbeda-integration-windows.spec
```

Output: `dist\SanBedaIntegration.exe`

## Project Structure

```
sanbeda-integration/
├── backend/                      # Python backend
│   ├── main.py                   # Application entry point
│   ├── database.py               # SQLite database manager
│   ├── bridge.py                 # Python-JS bridge
│   ├── requirements.txt          # Python dependencies
│   ├── sanbeda-integration.spec  # PyInstaller spec (macOS)
│   ├── sanbeda-integration-windows.spec  # PyInstaller spec (Windows)
│   ├── create_dmg.sh            # DMG creator script
│   └── services/
│       ├── pull_service.py       # Pull from San Beda
│       ├── push_service.py       # Push to cloud
│       └── scheduler.py          # Automated sync
│
├── frontend/                     # Vue.js frontend
│   ├── src/
│   │   ├── App.vue              # Main app component
│   │   ├── main.js              # Vue app entry
│   │   ├── style.css            # Global styles
│   │   ├── components/          # Vue components
│   │   │   ├── DashboardView.vue
│   │   │   ├── TimesheetView.vue
│   │   │   ├── ConfigView.vue
│   │   │   ├── LogsView.vue
│   │   │   └── ToastNotification.vue
│   │   ├── services/
│   │   │   └── bridge.js        # Bridge service
│   │   └── composables/
│   │       └── useToast.js      # Toast composable
│   ├── package.json             # NPM dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── tailwind.config.js       # TailwindCSS config
│   └── postcss.config.js        # PostCSS config
│
├── icons/                        # Application icons
│   ├── icon.icns                # macOS icon
│   └── icon.ico                 # Windows icon
│
├── dist/                         # Build output
├── run_dev.sh                    # Dev mode launcher
├── build_release.sh              # Build script (macOS)
├── build_release_windows.bat     # Build script (Windows)
├── README.md                     # User documentation
├── BUILD_GUIDE.md               # This file
└── API_DOCS.md                  # API integration docs
```

## Key Technologies

### Backend

- **PyQt6**: Desktop application framework
- **QWebEngineView**: Embedded Chromium browser
- **QWebChannel**: Python-JavaScript communication
- **SQLite**: Local database
- **requests**: HTTP client
- **schedule**: Task scheduling

### Frontend

- **Vue 3**: JavaScript framework (Composition API)
- **Vite**: Build tool and dev server
- **TailwindCSS**: Utility-first CSS framework
- **PostCSS**: CSS processing

## Architecture

### Communication Flow

```
┌─────────────────────────────────────┐
│ PyQt6 Application (Python)          │
│  ├─ HTTP Server (localhost:8765)    │
│  ├─ QWebEngineView (Chromium)       │
│  ├─ QWebChannel Bridge              │
│  └─ SQLite Database                 │
└──────────────┬──────────────────────┘
               │
               ↓
┌─────────────────────────────────────┐
│ Vue.js Frontend                      │
│  ├─ Bridge Service (QWebChannel)    │
│  ├─ Components (Dashboard, etc.)    │
│  └─ Composables (useToast)          │
└─────────────────────────────────────┘
```

### Why Local HTTP Server?

PyQt6's QWebEngineView with `file://` protocol doesn't consistently send the `Origin` header, causing CORS issues. The embedded HTTP server on `localhost:8765` solves this by serving files via `http://` protocol.

### Development vs Production

**Development Mode** (`DEV_MODE=true`):
- Loads frontend from Vite dev server (localhost:5173)
- Hot module replacement enabled
- Source maps available
- DevTools accessible with F12

**Production Mode**:
- Loads frontend from embedded HTTP server
- Minified and optimized code
- No dev server required
- Standalone executable

## Common Issues

### Backend Issues

**Virtual environment not activating:**
```bash
# macOS/Linux
source backend/venv/bin/activate

# Windows
backend\venv\Scripts\activate.bat
```

**PyQt6 import errors:**
```bash
pip install --upgrade PyQt6 PyQt6-WebEngine
```

**Database errors:**
- Delete `backend/database/sanbeda_integration.db` and restart

### Frontend Issues

**npm install fails:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**Vite dev server port conflict:**
- Change port in `frontend/vite.config.js` (default: 5173)

**Build errors:**
```bash
# Clear cache and rebuild
rm -rf frontend/dist frontend/node_modules
cd frontend && npm install && npm run build
```

### Build Issues

**PyInstaller errors:**
```bash
# Clean previous builds
rm -rf backend/build dist

# Rebuild
pyinstaller --clean sanbeda-integration.spec
```

**Missing frontend files in build:**
- Ensure `frontend/dist` exists before running PyInstaller
- Check `datas` section in `.spec` file

**Icon not showing:**
- Verify icon files exist in `icons/` folder
- Check icon path in `.spec` file

## Testing

### Manual Testing Checklist

Before releasing:

- [ ] All views load correctly
- [ ] Configuration saves and loads
- [ ] Test Connection works for both endpoints
- [ ] Manual pull sync works
- [ ] Manual push sync works
- [ ] Timesheet table displays data
- [ ] Logs show sync history
- [ ] Retry failed sync works
- [ ] App icon displays correctly
- [ ] DMG/installer works

### API Testing

Use mock endpoints during development:

```python
# In pull_service.py or push_service.py
if config['pull_url'] == 'http://localhost:3000/mock':
    # Return mock data
    return mock_data
```

## Versioning

Update version in these files:

1. `backend/sanbeda-integration.spec` - `info_plist['CFBundleVersion']`
2. `backend/sanbeda-integration-windows.spec` - (if applicable)
3. `backend/create_dmg.sh` - `VERSION` variable
4. `frontend/src/App.vue` - Version display

## Distribution

### macOS

1. Build DMG: `./build_release.sh && cd backend && ./create_dmg.sh`
2. Test on clean Mac
3. Upload to distribution server

### Windows

1. Build EXE: `build_release_windows.bat`
2. Create ZIP with executable and dependencies
3. Test on clean Windows machine
4. Upload to distribution server

## Customization

### Changing API Endpoints

Edit these files to match your API:

- `backend/services/pull_service.py` - Pull data format
- `backend/services/push_service.py` - Push data format

### Adding New Features

1. Backend: Add methods to `backend/bridge.py`
2. Frontend: Add methods to `frontend/src/services/bridge.js`
3. UI: Create components in `frontend/src/components/`

### Changing Branding

1. Update app name in specs and scripts
2. Replace icons in `icons/` folder
3. Update colors in `frontend/tailwind.config.js`
4. Modify header in `frontend/src/App.vue`

## Support

For development questions, contact the development team.
