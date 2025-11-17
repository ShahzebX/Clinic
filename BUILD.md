# Building the Clinic Data Entry Application

This guide explains how to create a standalone Windows executable from the Clinic Data Entry application.

## Prerequisites

- Python 3.10 or higher installed
- All dependencies installed: `pip install -r requirements.txt`
- PyInstaller (will be auto-installed by build scripts)

## Build Methods

### Method 1: Using the Batch File (Easiest)

Simply double-click `build.bat` or run from PowerShell:

```powershell
.\build.bat
```

The script will:
1. Check for PyInstaller (install if needed)
2. Clean previous builds
3. Create the executable
4. Show results and file location

### Method 2: Using the Python Script

Run from command line:

```powershell
python build.py
```

This provides the same functionality with better cross-platform support.

### Method 3: Manual PyInstaller Command

```powershell
pyinstaller --onefile --windowed --name "Clinic Data Entry" --add-data "assets;assets" --hidden-import=tkcalendar --hidden-import=babel.numbers --hidden-import=openpyxl --hidden-import=reportlab --clean main.py
```

### Method 4: Using the Spec File

For advanced customization:

```powershell
pyinstaller "Clinic Data Entry.spec"
```

## Output

After successful build, you'll find:

```
dist/
└── Clinic Data Entry.exe    (Your standalone application)
```

**File size:** Approximately 25-35 MB (includes Python runtime and all dependencies)

## Distribution

### Single PC Installation

1. Copy `Clinic Data Entry.exe` to the target PC
2. Place it anywhere (Desktop, Program Files, USB drive, etc.)
3. Double-click to run - no installation needed!

### Multiple PCs

1. Copy `Clinic Data Entry.exe` to each PC
2. Each PC will have its own database in `database/clinic.db`
3. Excel files save to `Documents\OPD Data` on each PC

### Network Shared Installation

**Not recommended** - SQLite doesn't handle concurrent access well.
Instead, install separately on each PC and consolidate Excel files manually.

## First Run

When users first run the application:

1. The app will create `Documents\OPD Data` folder automatically
2. Database file `database/clinic.db` will be created in the app's directory
3. PDF reports will be saved in `reports/` folder in the app's directory

## Troubleshooting

### Build Fails

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (should be 3.10+)
- Try cleaning and rebuilding: delete `build/` and `dist/` folders

### EXE Won't Run

- Check Windows Defender/Antivirus (may block unsigned executables)
- Run as Administrator (first time only)
- Check if all required DLLs are included

### Missing Imports

If the built EXE crashes with import errors, add the module to hidden imports in the build script:

```powershell
--hidden-import=module_name
```

## Signing the Executable (Optional)

To avoid Windows security warnings:

1. Obtain a code signing certificate
2. Use `signtool.exe` to sign the executable:
   ```powershell
   signtool sign /f certificate.pfx /p password "dist\Clinic Data Entry.exe"
   ```

## Creating an Installer (Advanced)

If you prefer an installer instead of standalone EXE:

### Using Inno Setup (Free)

1. Download Inno Setup: https://jrsoftware.org/isinfo.php
2. Create an `.iss` script file
3. Include the EXE and set up Start Menu shortcuts

### Using NSIS (Free)

1. Download NSIS: https://nsis.sourceforge.io/
2. Create an `.nsi` script
3. Compile to create installer

## Updates

To update the application:

1. Rebuild the EXE with new code
2. Distribute the new EXE
3. Users replace the old EXE with the new one
4. Database and data files remain intact

## File Locations After Distribution

```
[User's PC]
├── [Anywhere]/Clinic Data Entry.exe    (The application)
├── [App Location]/database/clinic.db    (Patient database)
├── [App Location]/reports/              (PDF reports)
└── C:\Users\[Username]\Documents\OPD Data\  (Excel files)
```

## Build Optimization

To reduce EXE size:

1. Use `--exclude-module` for unused packages
2. Enable UPX compression (included by default)
3. Remove unused assets

Example:
```powershell
pyinstaller --onefile --windowed --exclude-module matplotlib --exclude-module numpy ...
```

## Support & Issues

If you encounter issues:
1. Check the console output during build
2. Review PyInstaller logs in `build/` folder
3. Test the app before distributing
4. Keep source code for rebuilding
