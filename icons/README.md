# Application Icons

This directory should contain the application icons for different platforms.

## Required Files

### macOS
- `icon.icns` - macOS application icon (512x512@2x recommended)

### Windows
- `icon.ico` - Windows application icon (256x256 recommended)

## Creating Icons

### From PNG to ICNS (macOS)

1. Create a 1024x1024 PNG file named `icon.png`
2. Create iconset directory:
   ```bash
   mkdir icon.iconset
   ```
3. Generate all sizes:
   ```bash
   sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
   sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
   sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
   sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
   sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
   sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
   sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
   sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
   sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
   sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
   ```
4. Convert to ICNS:
   ```bash
   iconutil -c icns icon.iconset
   ```

### From PNG to ICO (Windows)

Use online tools or ImageMagick:

```bash
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
```

## Placeholder Icons

If you don't have custom icons yet, you can:

1. Use the default system icon (app will work without custom icons)
2. Generate placeholder icons from text or shapes
3. Find free icon templates online

## Icon Design Guidelines

- Use simple, recognizable shapes
- Ensure visibility at small sizes (16x16, 32x32)
- Use consistent brand colors
- Test on both light and dark backgrounds
- Follow platform-specific design guidelines:
  - macOS: Rounded square with subtle gradient
  - Windows: Can be any shape, often includes transparency

## Current Status

Icons are not included in this template. Please add your custom icons before building the final release.
