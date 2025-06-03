@echo off
setlocal enabledelayedexpansion

REM Browser-Use Complete Suite Launcher (Batch Version)
REM Simple launcher for Windows users who prefer batch files

echo.
echo ==========================================
echo   Browser-Use Complete Suite Launcher
echo ==========================================
echo.

REM Color definitions
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "RESET=[0m"

REM Check if PowerShell is available
powershell -Command "Get-Host" >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ PowerShell not found. This launcher requires PowerShell.%RESET%
    echo.
    echo Please install PowerShell or use the Python deployment instead:
    echo   python deploy.py
    pause
    exit /b 1
)

echo %GREEN%✅ PowerShell found%RESET%

REM Check if the PowerShell script exists
if not exist "launch-browser-use-complete.ps1" (
    echo %RED%❌ launch-browser-use-complete.ps1 not found%RESET%
    echo.
    echo Please ensure the PowerShell script is in the same directory.
    pause
    exit /b 1
)

echo %GREEN%✅ PowerShell script found%RESET%
echo.

REM Ask user for launch mode
echo %CYAN%🎯 Select launch mode:%RESET%
echo   1. Complete Suite (browser-use + web-ui + workflows)
echo   2. Web-UI Only (browser interface)
echo   3. Workflows Only (automation backend)
echo   4. Browser-Use Core Only
echo.
set /p choice="Enter your choice (1-4, default 1): "

if "%choice%"=="" set choice=1

REM Set launch mode based on choice
set "launchMode=all"
set "description=Complete Suite"

if "%choice%"=="1" (
    set "launchMode=all"
    set "description=Complete Suite"
)
if "%choice%"=="2" (
    set "launchMode=webui"
    set "description=Web-UI Only"
)
if "%choice%"=="3" (
    set "launchMode=workflows"
    set "description=Workflows Only"
)
if "%choice%"=="4" (
    set "launchMode=browser-only"
    set "description=Browser-Use Core Only"
)

echo.
echo %CYAN%🚀 Launching %description%...%RESET%
echo.

REM Ask for Docker mode
set /p useDocker="Use Docker containers? (y/N): "
set "dockerFlag="
if /i "%useDocker%"=="y" (
    set "dockerFlag=-UseDocker"
    echo %YELLOW%🐳 Docker mode enabled%RESET%
)

REM Ask for persistent browser
set /p persistentBrowser="Enable persistent browser sessions? (y/N): "
set "persistentFlag="
if /i "%persistentBrowser%"=="y" (
    set "persistentFlag=-PersistentBrowser"
    echo %YELLOW%💾 Persistent browser enabled%RESET%
)

REM Ask for custom ports
echo.
echo %CYAN%🌐 Port Configuration:%RESET%
set /p webUIPort="Web-UI port (default 7788): "
if "%webUIPort%"=="" set webUIPort=7788

set /p workflowPort="Workflow backend port (default 8000): "
if "%workflowPort%"=="" set workflowPort=8000

echo.
echo %CYAN%📋 Configuration Summary:%RESET%
echo   Launch Mode: %description%
echo   Web-UI Port: %webUIPort%
echo   Workflow Port: %workflowPort%
echo   Docker Mode: %useDocker%
echo   Persistent Browser: %persistentBrowser%
echo.

REM Confirm launch
set /p confirm="Proceed with launch? (Y/n): "
if /i "%confirm%"=="n" (
    echo %YELLOW%⚠️ Launch cancelled by user%RESET%
    pause
    exit /b 0
)

echo.
echo %GREEN%🚀 Starting Browser-Use Suite...%RESET%
echo.

REM Build PowerShell command
set "psCommand=.\launch-browser-use-complete.ps1 -LaunchMode %launchMode% -WebUIPort %webUIPort% -WorkflowPort %workflowPort%"

if not "%dockerFlag%"=="" (
    set "psCommand=!psCommand! %dockerFlag%"
)

if not "%persistentFlag%"=="" (
    set "psCommand=!psCommand! %persistentFlag%"
)

REM Execute PowerShell script
echo %CYAN%Executing: %psCommand%%RESET%
echo.

powershell -ExecutionPolicy Bypass -Command "& { %psCommand% }"

REM Check exit code
if errorlevel 1 (
    echo.
    echo %RED%❌ Launch failed with error code %errorlevel%%RESET%
    echo.
    echo %YELLOW%💡 Troubleshooting tips:%RESET%
    echo   - Check if all prerequisites are installed
    echo   - Try running as Administrator
    echo   - Check the PowerShell execution policy
    echo   - Review the error messages above
    echo.
    echo %CYAN%📚 For detailed help, see:%RESET%
    echo   - POWERSHELL_BROWSER_USE_GUIDE.md
    echo   - DEPLOYMENT_GUIDE_UPDATED.md
    echo.
    pause
    exit /b 1
)

echo.
echo %GREEN%✅ Browser-Use Suite launched successfully!%RESET%
echo.
echo %CYAN%🌐 Access your services at:%RESET%
if "%launchMode%"=="all" (
    echo   Web-UI: http://localhost:%webUIPort%
    echo   Workflow API: http://localhost:%workflowPort%
    echo   API Docs: http://localhost:%workflowPort%/docs
) else if "%launchMode%"=="webui" (
    echo   Web-UI: http://localhost:%webUIPort%
) else if "%launchMode%"=="workflows" (
    echo   Workflow API: http://localhost:%workflowPort%
    echo   API Docs: http://localhost:%workflowPort%/docs
) else (
    echo   Browser-Use Core is running
)

echo.
echo %YELLOW%💡 Press Ctrl+C in the PowerShell window to stop services%RESET%
echo.
pause

