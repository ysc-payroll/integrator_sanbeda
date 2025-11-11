#!/bin/bash
# Toggle DEV_MODE between development and production

MAIN_PY="backend/main.py"

# Check current mode
if grep -q "DEV_MODE = True" "$MAIN_PY"; then
    echo "Current mode: DEVELOPMENT"
    echo "Switching to PRODUCTION mode..."
    sed -i.bak 's/DEV_MODE = True/DEV_MODE = False/' "$MAIN_PY"
    echo "✅ Switched to PRODUCTION mode"
    echo "   App will load from bundled frontend/dist"
else
    echo "Current mode: PRODUCTION"
    echo "Switching to DEVELOPMENT mode..."
    sed -i.bak 's/DEV_MODE = False/DEV_MODE = True/' "$MAIN_PY"
    echo "✅ Switched to DEVELOPMENT mode"
    echo "   App will load from Vite dev server (localhost:5173)"
fi

rm -f "${MAIN_PY}.bak"

echo ""
echo "Current setting in main.py:"
grep "DEV_MODE = " "$MAIN_PY"
