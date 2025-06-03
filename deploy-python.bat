@echo off
setlocal enabledelayedexpansion

REM Single Python Deployment Script Launcher
REM Calls the comprehensive Python deployer

echo.
echo ==========================================
echo   Python Deployment Script Launcher
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [91m❌ Python not found. Please install Python 3.11+[0m
    echo.
    echo Download from: https://python.org
    pause
    exit /b 1
)

REM Check if deploy.py exists
if not exist "deploy.py" (
    echo [91m❌ deploy.py not found in current directory[0m
    pause
    exit /b 1
)

echo [96m🚀 Starting Python deployment...[0m
echo.

REM Run the Python deployment script
python deploy.py

REM Check exit code
if errorlevel 1 (
    echo.
    echo [93m⚠️ Deployment encountered issues.[0m
    echo [96m💡 Fallback options:[0m
    echo   - Try deploy-simple.bat for ultra-simple deployment
    echo   - Check DEPLOYMENT_GUIDE.md for troubleshooting
    echo.
    pause
    exit /b 1
)

echo.
echo [92m✅ Python deployment completed successfully![0m
pause

