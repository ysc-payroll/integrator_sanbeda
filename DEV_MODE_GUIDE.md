# DEV_MODE Guide

## What is DEV_MODE?

DEV_MODE controls where the PyQt6 app loads the frontend from:

- **DEV_MODE = True** (Development): Loads from Vite dev server (localhost:5173)
  - ✅ Hot reload enabled
  - ✅ Fast development
  - ✅ Source maps available
  - ❌ Requires Vite server running

- **DEV_MODE = False** (Production): Loads from bundled files (frontend/dist)
  - ✅ Standalone app
  - ✅ No external dependencies
  - ✅ Optimized and minified
  - ❌ No hot reload

## Current Setting

**DEV_MODE is now TRUE by default** for easier development.

You can check the current mode in `backend/main.py`:
```python
# Always run in development mode for easier development
DEV_MODE = True  # Set to False for production builds
```

## How to Run in Development Mode

Since DEV_MODE is true by default, just run:

**Terminal 1** (Frontend):
```bash
cd frontend
npm run dev
```

**Terminal 2** (Backend):
```bash
cd backend
source venv/bin/activate
python main.py
```

No need to set environment variables!

## How to Toggle DEV_MODE

### Option 1: Use the Toggle Script (Easiest)

```bash
./toggle_dev_mode.sh
```

This script automatically switches between DEV_MODE = True/False.

### Option 2: Manual Edit

Edit `backend/main.py` line 37:

**For Development**:
```python
DEV_MODE = True  # Set to False for production builds
```

**For Production**:
```python
DEV_MODE = False  # Production mode
```

## When to Use Each Mode

### Use DEV_MODE = True (Current Default)

Use this when:
- ✅ Actively developing the app
- ✅ Making changes to Vue components
- ✅ Testing new features
- ✅ Debugging frontend issues

### Use DEV_MODE = False

Use this when:
- ✅ Building production app
- ✅ Creating DMG/EXE installer
- ✅ Testing final build
- ✅ Deploying to client

## Production Build Checklist

Before building for production:

1. **Switch to Production Mode**:
   ```bash
   ./toggle_dev_mode.sh
   # Verify it shows "PRODUCTION mode"
   ```

2. **Build Frontend**:
   ```bash
   cd frontend
   npm run build
   ```

3. **Build App**:
   ```bash
   ./build_release.sh  # macOS
   # or
   build_release_windows.bat  # Windows
   ```

4. **Test the Built App**:
   ```bash
   open "dist/San Beda Integration.app"  # macOS
   ```

5. **Create Installer** (macOS):
   ```bash
   cd backend
   ./create_dmg.sh
   ```

6. **Switch Back to Development** (optional):
   ```bash
   ./toggle_dev_mode.sh
   ```

## Troubleshooting

### App shows blank screen

**In DEV_MODE = True**:
- Check if Vite dev server is running (Terminal 1)
- Verify localhost:5173 is accessible
- Check browser console (right-click → Inspect)

**In DEV_MODE = False**:
- Verify `frontend/dist` folder exists
- Rebuild frontend: `cd frontend && npm run build`
- Check `sanbeda_integration.log` for errors

### Hot reload not working

- DEV_MODE must be True
- Vite dev server must be running
- Try restarting both terminals

### Production build shows dev server error

- Switch to production mode: `./toggle_dev_mode.sh`
- Rebuild app: `./build_release.sh`

## Quick Reference

```bash
# Check current mode
grep "DEV_MODE = " backend/main.py

# Toggle mode
./toggle_dev_mode.sh

# Development workflow (DEV_MODE = True)
cd frontend && npm run dev                      # Terminal 1
cd backend && source venv/bin/activate && python main.py  # Terminal 2

# Production build (DEV_MODE = False)
./toggle_dev_mode.sh  # Switch to production
./build_release.sh    # Build app
./toggle_dev_mode.sh  # Switch back to dev
```

## Summary

- ✅ **Default**: DEV_MODE = True (easier development)
- ✅ **No environment variables needed**: Just run `python main.py`
- ✅ **Toggle script**: Easy switching with `./toggle_dev_mode.sh`
- ✅ **Production**: Remember to set DEV_MODE = False before building

Happy developing! 🚀
