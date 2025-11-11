#!/bin/bash
# San Beda Integration Tool - Release Build Script for macOS

set -e

echo "========================================="
echo "San Beda Integration Tool - Build Release"
echo "========================================="

# Check for required commands
command -v npm >/dev/null 2>&1 || { echo "Error: npm is not installed"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 is not installed"; exit 1; }

# Step 1: Build Frontend
echo ""
echo "Step 1/3: Building frontend..."
cd frontend
npm install
npm run build
cd ..

if [ ! -d "frontend/dist" ]; then
    echo "Error: Frontend build failed - dist directory not found"
    exit 1
fi

echo "Frontend build complete!"

# Step 2: Set up Python environment
echo ""
echo "Step 2/3: Setting up Python environment..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    # Use Python 3.10+ explicitly (required for PyQt6 6.6.1)
    if command -v python3.10 &> /dev/null; then
        python3.10 -m venv venv
    elif command -v python3.12 &> /dev/null; then
        python3.12 -m venv venv
    elif command -v python3.11 &> /dev/null; then
        python3.11 -m venv venv
    else
        echo "Error: Python 3.10+ is required. Please install Python 3.10 or higher."
        exit 1
    fi
fi

source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

# Step 3: Build macOS app
echo ""
echo "Step 3/3: Building macOS application..."
pyinstaller --clean --distpath ../dist --workpath build sanbeda-integration.spec

cd ..

if [ ! -d "dist/San Beda Integration.app" ]; then
    echo "Error: Build failed - app bundle not found"
    exit 1
fi

echo ""
echo "========================================="
echo "Build completed successfully!"
echo "========================================="
echo "App location: dist/San Beda Integration.app"
echo ""
echo "To create DMG installer, run:"
echo "  cd backend && ./create_dmg.sh"
echo "========================================="
