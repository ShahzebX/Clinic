@echo off
REM Build script for Clinic Data Entry Application
REM This creates a standalone executable using PyInstaller

echo ================================
echo Clinic Data Entry - Build Script
echo ================================
echo.

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist "Clinic Data Entry.spec" del "Clinic Data Entry.spec"
echo.

REM Build the executable
echo Building executable...
echo This may take a few minutes...
echo.

python -m PyInstaller --onefile ^
    --windowed ^
    --name "Clinic Data Entry" ^
    --add-data "assets;assets" ^
    --hidden-import=tkcalendar ^
    --hidden-import=babel.numbers ^
    --hidden-import=openpyxl ^
    --hidden-import=reportlab ^
    --clean ^
    main.py

if errorlevel 1 (
    echo.
    echo ================================
    echo Build FAILED!
    echo ================================
    pause
    exit /b 1
)

echo.
echo ================================
echo Build SUCCESSFUL!
echo ================================
echo.
echo Your executable is located at:
echo dist\Clinic Data Entry.exe
echo.
echo File size:
dir "dist\Clinic Data Entry.exe" | find "Clinic Data Entry.exe"
echo.
echo You can now:
echo 1. Copy "Clinic Data Entry.exe" to any Windows PC
echo 2. Run it without installation
echo 3. The app will create "Documents\OPD Data" folder automatically
echo.
echo ================================
pause
