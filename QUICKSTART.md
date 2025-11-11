# San Beda Integration Tool - Quick Start Guide

## For Developers

### First Time Setup

```bash
# 1. Install dependencies
./run_dev.sh

# 2. Terminal 1 - Start frontend dev server
cd frontend
npm run dev

# 3. Terminal 2 - Start Python app (in another terminal)
cd backend
source venv/bin/activate
export DEV_MODE=true
python main.py
```

The app will open with hot reload enabled. Changes to Vue files will reflect immediately.

### Building for Release

```bash
# macOS
./build_release.sh
cd backend && ./create_dmg.sh

# Windows
build_release_windows.bat
```

## For End Users

### Installation

**macOS**:
1. Download and open `SanBedaIntegration-v1.0.0.dmg`
2. Drag app to Applications folder
3. Launch from Applications

**Windows**:
1. Download and extract `SanBedaIntegration-v1.0.0.zip`
2. Run `SanBedaIntegration.exe`

### Initial Configuration

1. Open the app
2. Go to **Configuration** tab
3. Configure **Pull** settings:
   - Enter San Beda API URL
   - Select authentication type
   - Enter credentials
   - Set sync interval (e.g., 30 minutes)
   - Click "Test Connection"
4. Configure **Push** settings:
   - Enter cloud payroll API URL
   - Select authentication type
   - Enter credentials
   - Set sync interval (e.g., 15 minutes)
   - Click "Test Connection"
5. Click "Save Configuration"

### Daily Usage

**Dashboard** - Overview and manual sync controls
- View total/synced/pending/error counts
- Click "Pull Data Now" to fetch from San Beda
- Click "Push Data Now" to sync to cloud payroll

**Timesheets** - Browse and manage records
- View all timesheet entries
- Filter by status (synced/pending/errors)
- Search by employee name
- Retry failed syncs

**Configuration** - Update settings
- Change API endpoints
- Update credentials
- Adjust sync intervals

**Logs** - Monitor sync activity
- View sync history
- Check error messages
- Monitor performance

## Next Steps

### For Developers

1. Review [BUILD_GUIDE.md](BUILD_GUIDE.md) for detailed development workflow
2. Read [API_DOCS.md](API_DOCS.md) to customize API integration
3. Modify services in `backend/services/` to match your API formats

### For Customization

**Change Pull API Format**:
Edit `backend/services/pull_service.py`:
```python
def process_timesheet(self, ts_data):
    # Customize field mapping here
```

**Change Push API Format**:
Edit `backend/services/push_service.py`:
```python
def push_timesheet(self, timesheet, config, headers):
    # Customize payload here
```

**Change UI/Branding**:
- Update colors in `frontend/tailwind.config.js`
- Modify header in `frontend/src/App.vue`
- Replace icons in `icons/` folder

## Troubleshooting

**App won't start in dev mode**:
```bash
# Check Python virtual environment
cd backend
source venv/bin/activate
python main.py

# Check frontend dev server
cd frontend
npm run dev
```

**Build fails**:
```bash
# Clean and rebuild
rm -rf frontend/dist backend/build dist
./build_release.sh
```

**Connection errors**:
- Check Configuration tab
- Click "Test Connection" for each endpoint
- Verify credentials and URLs
- Check firewall settings

**Sync errors**:
- View Logs tab for details
- Retry failed records from Timesheets tab
- Check API_DOCS.md for format requirements

## Key Files

| File | Purpose |
|------|---------|
| `backend/main.py` | Application entry point |
| `backend/database.py` | Database operations |
| `backend/services/pull_service.py` | Pull from San Beda |
| `backend/services/push_service.py` | Push to cloud payroll |
| `frontend/src/App.vue` | Main UI component |
| `frontend/src/components/` | Vue components |

## Support

- Documentation: See README.md, BUILD_GUIDE.md, API_DOCS.md
- Issues: Check `sanbeda_integration.log` for errors
- Contact: The Abba development team
