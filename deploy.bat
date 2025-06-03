@echo off
setlocal enabledelayedexpansion

REM Workflow-Use Suite Deployment Script
REM This script sets up and launches the complete workflow-use suite using uv

echo.
echo ========================================
echo   Workflow-Use Suite Deployment
echo ========================================
echo.

REM Color definitions (for Windows 10+)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "BOLD=[1m"
set "RESET=[0m"

REM Function to print colored text
goto :main

:print_success
echo %GREEN%✅ %~1%RESET%
goto :eof

:print_warning
echo %YELLOW%⚠️ %~1%RESET%
goto :eof

:print_error
echo %RED%❌ %~1%RESET%
goto :eof

:print_info
echo %CYAN%🔍 %~1%RESET%
goto :eof

:main

REM Check if we're in the right directory
if not exist "pyproject.toml" (
    call :print_error "pyproject.toml not found. Please run this script from the project root."
    pause
    exit /b 1
)

call :print_info "Checking prerequisites..."

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python not found. Please install Python 3.11+ from https://python.org"
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
call :print_success "Python found: %PYTHON_VERSION%"

REM Check if Python version is 3.11+
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)
if %MAJOR% LSS 3 (
    call :print_error "Python 3.11+ required. Found: %PYTHON_VERSION%"
    pause
    exit /b 1
)
if %MAJOR% EQU 3 if %MINOR% LSS 11 (
    call :print_error "Python 3.11+ required. Found: %PYTHON_VERSION%"
    pause
    exit /b 1
)

REM Check uv
uv --version >nul 2>&1
if errorlevel 1 (
    call :print_warning "uv not found. Installing uv..."
    
    REM Install uv using pip
    python -m pip install uv
    if errorlevel 1 (
        call :print_error "Failed to install uv. Please install manually: https://docs.astral.sh/uv/"
        pause
        exit /b 1
    )
    
    REM Verify uv installation
    uv --version >nul 2>&1
    if errorlevel 1 (
        call :print_error "uv installation failed. Please install manually."
        pause
        exit /b 1
    )
)

for /f "tokens=*" %%i in ('uv --version 2^>^&1') do set UV_VERSION=%%i
call :print_success "uv found: %UV_VERSION%"

REM Check Git
git --version >nul 2>&1
if errorlevel 1 (
    call :print_warning "Git not found. Some features may not work."
) else (
    call :print_success "Git found"
)

REM Check Node.js (optional)
node --version >nul 2>&1
if errorlevel 1 (
    call :print_warning "Node.js not found. UI development server will not be available."
) else (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    call :print_success "Node.js found: %NODE_VERSION%"
)

echo.
call :print_info "Setting up Python environment..."

REM Create virtual environment in project root
if not exist ".venv" (
    call :print_info "Creating virtual environment..."
    uv venv
    if errorlevel 1 (
        call :print_error "Failed to create virtual environment"
        pause
        exit /b 1
    )
    call :print_success "Virtual environment created"
) else (
    call :print_success "Virtual environment already exists"
)

REM Sync dependencies
call :print_info "Installing dependencies..."
uv sync
if errorlevel 1 (
    call :print_error "Failed to install dependencies"
    pause
    exit /b 1
)
call :print_success "Dependencies installed"

REM Install Playwright browsers
call :print_info "Installing Playwright browsers..."
uv run playwright install --with-deps
if errorlevel 1 (
    call :print_warning "Playwright installation had issues, but continuing..."
) else (
    call :print_success "Playwright browsers installed"
)

REM Setup environment files
call :print_info "Setting up environment configuration..."

if not exist "workflows\.env" (
    if exist "workflows\.env.example" (
        copy "workflows\.env.example" "workflows\.env" >nul
        call :print_success "Created workflows\.env from example"
        call :print_warning "Please edit workflows\.env to add your API keys"
    )
)

echo.
call :print_info "Choose deployment mode:"
echo 1. Backend only (API server)
echo 2. Web-UI only (Browser automation interface)
echo 3. Complete suite (Backend + Web-UI + Workflow UI)
echo 4. Exit
echo.

set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto :backend
if "%choice%"=="2" goto :webui
if "%choice%"=="3" goto :suite
if "%choice%"=="4" goto :exit
goto :invalid_choice

:backend
echo.
call :print_info "Starting workflow backend..."
uv run python main.py backend
goto :end

:webui
echo.
call :print_info "Starting browser-use web-ui..."
uv run python main.py webui
goto :end

:suite
echo.
call :print_info "Starting complete workflow-use suite..."
uv run python main.py suite
goto :end

:invalid_choice
call :print_error "Invalid choice. Please select 1-4."
pause
goto :main

:exit
echo.
call :print_info "Exiting..."
goto :end

:end
echo.
call :print_success "Deployment script completed!"
echo.
echo %CYAN%📖 For more information:%RESET%
echo   - Workflow Backend API: http://127.0.0.1:8000/docs
echo   - Browser-Use Web-UI: http://127.0.0.1:7788
echo   - Workflow UI: http://127.0.0.1:5173
echo.
echo %YELLOW%💡 Quick commands:%RESET%
echo   - Backend only: uv run python main.py backend
echo   - Web-UI only: uv run python main.py webui
echo   - Complete suite: uv run python main.py suite
echo.
pause

