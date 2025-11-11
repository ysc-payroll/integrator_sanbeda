#!/bin/bash
# San Beda Integration Tool - Development Mode Launcher
# Run this script to start the app in development mode with hot reload

set -e

echo "========================================="
echo "San Beda Integration Tool - Dev Mode"
echo "========================================="

# Check if venv exists
if [ ! -d "backend/venv" ]; then
    echo "Virtual environment not found. Creating..."
    cd backend
    # Use Python 3.10 explicitly (required for PyQt6 6.6.1)
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
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install pyinstaller  # For building later
    cd ..
else
    echo "Virtual environment found."
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "Frontend dependencies not found. Installing..."
    cd frontend
    npm install
    cd ..
else
    echo "Frontend dependencies found."
fi

echo ""
echo "========================================="
echo "IMPORTANT: Run in TWO terminals"
echo "========================================="
echo "Terminal 1: Start frontend dev server"
echo "  cd frontend && npm run dev"
echo ""
echo "Terminal 2: Start Python app"
echo "  cd backend && source venv/bin/activate && python main.py"
echo ""
echo "Note: DEV_MODE is enabled by default in main.py"
echo "========================================="
