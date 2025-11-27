# San Beda Integration Tool

A desktop application that bridges San Beda's on-premise timekeeping system with YAHSHUA cloud payroll.

## Features

- **Pull** - Fetch attendance data from San Beda on-premise server
- **Push** - Sync timesheet data to YAHSHUA cloud payroll
- **Auto Sync** - Configurable automatic sync intervals
- **Offline-First** - Works without internet, syncs when online
- **Activity Logs** - Complete history of all sync operations

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.10+ / PyQt6 |
| Frontend | Vue.js 3 / Vite / TailwindCSS |
| Database | SQLite |
| Packaging | PyInstaller |
| CI/CD | GitHub Actions |

## Installation

### macOS
1. Download `SanBedaIntegration-vX.X.X.dmg` from Releases
2. Open DMG and drag to Applications
3. First launch takes 1-2 minutes (one-time initialization)

### Windows
1. Download `SanBedaIntegration-vX.X.X-Windows.zip` from Releases
2. Extract and run `SanBedaIntegration.exe`

## Documentation

See **[CLAUDE.md](CLAUDE.md)** for comprehensive developer documentation including:
- Architecture overview
- Authentication flows (San Beda MD5 + YAHSHUA Bearer)
- Database schema
- Build instructions
- Troubleshooting guide

## Release

```bash
git tag vX.X.X
git push origin vX.X.X
```

GitHub Actions will automatically build and create a release with macOS DMG and Windows ZIP.

## License

Copyright © 2025 The Abba. All rights reserved.
