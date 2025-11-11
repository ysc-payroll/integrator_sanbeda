#!/bin/bash
# San Beda Integration Tool - DMG Installer Creator for macOS

set -e

APP_NAME="San Beda Integration"
VERSION="1.0.0"
DMG_NAME="SanBedaIntegration-v${VERSION}.dmg"
APP_PATH="../dist/${APP_NAME}.app"
DMG_PATH="../dist/${DMG_NAME}"

echo "========================================="
echo "Creating DMG Installer"
echo "========================================="

# Check if app exists
if [ ! -d "$APP_PATH" ]; then
    echo "Error: Application not found at $APP_PATH"
    echo "Please run build_release.sh first"
    exit 1
fi

# Remove old DMG if exists
if [ -f "$DMG_PATH" ]; then
    echo "Removing old DMG..."
    rm "$DMG_PATH"
fi

# Create temporary directory
TEMP_DIR=$(mktemp -d)
echo "Creating temporary directory at $TEMP_DIR"

# Copy app to temp directory
echo "Copying application..."
cp -R "$APP_PATH" "$TEMP_DIR/"

# Create symlink to Applications folder
echo "Creating Applications symlink..."
ln -s /Applications "$TEMP_DIR/Applications"

# Create DMG
echo "Creating DMG..."
hdiutil create -volname "${APP_NAME}" \
    -srcfolder "$TEMP_DIR" \
    -ov -format UDZO \
    "$DMG_PATH"

# Clean up
echo "Cleaning up..."
rm -rf "$TEMP_DIR"

# Get DMG size
DMG_SIZE=$(du -h "$DMG_PATH" | cut -f1)

echo ""
echo "========================================="
echo "DMG created successfully!"
echo "========================================="
echo "Location: $DMG_PATH"
echo "Size: $DMG_SIZE"
echo ""
echo "To distribute:"
echo "1. Test the DMG by mounting and dragging to Applications"
echo "2. Upload to your distribution server"
echo "========================================="
