#!/usr/bin/env python3
"""
Quick build script for Clinic Data Entry Application
Alternative to build.bat for those who prefer Python scripts
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_pyinstaller():
    """Check if PyInstaller is installed, install if not."""
    try:
        import PyInstaller
        print("✓ PyInstaller found")
        return True
    except ImportError:
        print("⚠ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✓ PyInstaller installed")
        return True


def clean_build():
    """Remove previous build artifacts."""
    print("\n🧹 Cleaning previous builds...")
    folders = ["build", "dist", "__pycache__"]
    files = ["Clinic Data Entry.spec"]
    
    for folder in folders:
        if Path(folder).exists():
            shutil.rmtree(folder)
            print(f"  Removed {folder}/")
    
    for file in files:
        if Path(file).exists():
            os.remove(file)
            print(f"  Removed {file}")


def build_exe():
    """Build the executable using PyInstaller."""
    print("\n🔨 Building executable...")
    print("This may take a few minutes...\n")
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "Clinic Data Entry",
        "--add-data", "assets;assets",
        "--hidden-import=tkcalendar",
        "--hidden-import=babel.numbers",
        "--hidden-import=openpyxl",
        "--hidden-import=reportlab",
        "--clean",
        "main.py"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def show_results():
    """Display build results and file information."""
    exe_path = Path("dist/Clinic Data Entry.exe")
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        
        print("\n" + "=" * 50)
        print("✅ BUILD SUCCESSFUL!")
        print("=" * 50)
        print(f"\n📦 Executable location:")
        print(f"   {exe_path.absolute()}")
        print(f"\n📊 File size: {size_mb:.2f} MB")
        print(f"\n📝 Instructions:")
        print("   1. Copy 'Clinic Data Entry.exe' to any Windows PC")
        print("   2. Run it without installation")
        print("   3. Data saves to Documents\\OPD Data automatically")
        print("\n" + "=" * 50)
        return True
    else:
        print("\n" + "=" * 50)
        print("❌ BUILD FAILED!")
        print("=" * 50)
        print("Check the error messages above.")
        return False


def main():
    """Main build process."""
    print("=" * 50)
    print("Clinic Data Entry - Build Script")
    print("=" * 50)
    
    # Change to script directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Build steps
    if not check_pyinstaller():
        return 1
    
    clean_build()
    
    if not build_exe():
        return 1
    
    if not show_results():
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
