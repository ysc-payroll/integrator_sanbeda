@echo off
REM San Beda Integration Tool - Release Build Script for Windows

echo =========================================
echo San Beda Integration Tool - Build Release
echo =========================================

REM Check for npm
where npm >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: npm is not installed
    exit /b 1
)

REM Check for python
where python >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: python is not installed
    exit /b 1
)

REM Step 1: Build Frontend
echo.
echo Step 1/3: Building frontend...
cd frontend
call npm install
call npm run build
cd ..

if not exist "frontend\dist" (
    echo Error: Frontend build failed - dist directory not found
    exit /b 1
)

echo Frontend build complete!

REM Step 2: Set up Python environment
echo.
echo Step 2/3: Setting up Python environment...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

REM Step 3: Build Windows executable
echo.
echo Step 3/3: Building Windows executable...
pyinstaller --clean --distpath ..\dist --workpath build sanbeda-integration-windows.spec

cd ..

if not exist "dist\SanBedaIntegration.exe" (
    echo Error: Build failed - executable not found
    exit /b 1
)

echo.
echo =========================================
echo Build completed successfully!
echo =========================================
echo Executable location: dist\SanBedaIntegration.exe
echo.
echo To distribute, create a ZIP file with:
echo - dist\SanBedaIntegration.exe
echo - Any required DLL files
echo =========================================

pause
