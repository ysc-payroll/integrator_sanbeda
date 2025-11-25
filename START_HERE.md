# 🚀 San Beda Integration Tool - Start Here

## ✅ Setup Complete!

Your development environment is now ready. All dependencies have been installed:
- ✅ Python 3.10 virtual environment (backend/venv)
- ✅ PyQt6 6.6.1 installed
- ✅ Node.js dependencies installed
- ✅ All services and components created
- ✅ **Demo database seeded** with sample data!

## 🎯 Quick Start - Development Mode

To run the app in development mode with hot reload, you need **TWO terminals**:

### Terminal 1 - Frontend Dev Server

```bash
cd frontend
npm run dev
```

This starts Vite on http://localhost:5173 with hot module replacement.

### Terminal 2 - Python Application

```bash
cd backend
source venv/bin/activate
python main.py
```

The PyQt6 app will open and load the frontend from the Vite dev server.

**Note**: DEV_MODE is now always enabled by default in `main.py`.

**Hot Reload**: Any changes to `.vue` files will automatically refresh in the app!

## 🔧 What You Need to Customize

### 1. API Endpoints (REQUIRED)

The app is ready to run, but you need to configure it for your actual APIs:

**Pull Service** (San Beda → Local):
Edit: `backend/services/pull_service.py`
- Update `process_timesheet()` method to match San Beda's API response format
- Update `process_employee()` method if needed
- See `API_DOCS.md` for examples

**Push Service** (Local → Cloud Payroll):
Edit: `backend/services/push_service.py`
- Update `push_timesheet()` method to match your cloud API format
- Adjust payload structure in the `payload = {...}` section
- See `API_DOCS.md` for examples

### 2. Application Icons (Optional but Recommended)

Create app icons before building for production:
- macOS: `icons/icon.icns`
- Windows: `icons/icon.ico`

See `icons/README.md` for instructions.

## 📋 Daily Development Workflow

1. **Start development servers** (see Quick Start above)
2. **Make changes** to Vue files in `frontend/src/components/`
3. **See changes instantly** (hot reload)
4. **Test backend changes**: Restart Terminal 2 after Python file changes

## 🏗️ Building for Production

### macOS App

```bash
./build_release.sh
```

Output: `dist/San Beda Integration.app`

### macOS DMG Installer

```bash
cd backend
./create_dmg.sh
```

Output: `dist/SanBedaIntegration-v1.0.0.dmg`

### Windows Executable

```bash
build_release_windows.bat
```

Output: `dist/SanBedaIntegration.exe`

## 🎬 Demo Database

The database has been seeded with sample data:
- **10 employees** (John Doe, Jane Smith, etc.)
- **112 timesheet entries** from the last 7 days
- **78 synced** records
- **34 pending** records
- **10 sync logs** (pull and push history)

### Database Management

**Add more demo data**:
```bash
cd backend
source venv/bin/activate
python seed_data.py
```

**Reset database** (start fresh):
```bash
cd backend
source venv/bin/activate
python reset_database.py
```

## 🧪 Testing the App

### Explore the Demo Data

When you first run the app:

1. Go to **Configuration** tab
2. Enter test endpoints:
   - Pull URL: Your San Beda API endpoint
   - Push URL: Your cloud payroll API endpoint
3. Select authentication type
4. Enter credentials
5. Click "Test Connection" for each
6. Set sync intervals (e.g., 30 min for pull, 15 min for push)
7. Click "Save Configuration"

### Testing Sync

1. Go to **Dashboard**
2. Click "Pull Data Now" (will fetch from San Beda)
3. Go to **Timesheets** to see imported records
4. Click "Push Data Now" (will sync to cloud)
5. Check **Logs** tab for sync history

## 📚 Documentation

- **README.md** - User guide and features overview
- **BUILD_GUIDE.md** - Complete development guide
- **API_DOCS.md** - API integration with code examples
- **QUICKSTART.md** - Quick reference commands
- **PROJECT_SUMMARY.md** - Complete project overview

## 🐛 Troubleshooting

### Python version error

If you see "No matching distribution for PyQt6==6.6.1":
```bash
# Check Python version
python3 --version  # Must be 3.8+

# Use Python 3.10+
python3.10 --version

# Recreate venv
cd backend
rm -rf venv
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start

```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### Backend won't start

```bash
cd backend
source venv/bin/activate
python main.py  # Check error message
```

Check `sanbeda_integration.log` for detailed errors.

### App window is blank

Make sure:
1. Frontend dev server is running (Terminal 1)
2. DEV_MODE=true is set (Terminal 2)
3. No firewall blocking localhost:5173

## ⚡ Common Commands

```bash
# Development
cd frontend && npm run dev                    # Terminal 1
cd backend && source venv/bin/activate && python main.py  # Terminal 2

# Build frontend only
cd frontend && npm run build

# Build complete macOS app
./build_release.sh

# Create DMG installer
cd backend && ./create_dmg.sh

# Clean build
rm -rf frontend/dist backend/build dist
```

## 📝 Next Steps

1. ✅ **Test the app** - Run in dev mode to see it working
2. ✅ **Customize APIs** - Update pull_service.py and push_service.py
3. ✅ **Add icons** - Create app icons for professional look
4. ✅ **Test with real data** - Connect to actual San Beda API
5. ✅ **Build production version** - Create distributable app
6. ✅ **Deploy to client** - Install on target machine

## 🎉 You're Ready!

Everything is set up and working. Just:
1. Start both terminals (see Quick Start above)
2. App will open automatically
3. Configure your API endpoints
4. Start syncing!

Need help? Check the documentation files or the inline comments in the code.

---

**Built with**: PyQt6 + Vue.js 3 + SQLite
**Version**: 1.0.0
**Python**: 3.10+ required
