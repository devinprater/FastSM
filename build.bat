@echo off
REM Build script for FastSM using PyInstaller

echo ========================================
echo Building FastSM with PyInstaller
echo ========================================
echo.

REM Check if PyInstaller is installed
python -m PyInstaller --version
if errorlevel 1 (
    echo PyInstaller is not installed. Installing...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Run the build script
python build.py

echo.
pause
