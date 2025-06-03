@echo off
setlocal enabledelayedexpansion

REM Enhanced Development Deployment for Workflow-Use Suite
REM One-time setup with comprehensive environment validation and sequential launchers

echo.
echo ==========================================
echo   Workflow-Use Suite v2.0 - Dev Setup
echo ==========================================
echo.

REM Color definitions
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "MAGENTA=[95m"
set "BOLD=[1m"
set "RESET=[0m"

REM Function definitions
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

:print_header
echo %MAGENTA%🚀 %~1%RESET%
goto :eof

:main

REM Check if we're in the right directory
if not exist "pyproject.toml" (
    call :print_error "pyproject.toml not found. Please run from project root."
    pause
    exit /b 1
)

call :print_header "Enhanced Development Environment Setup"
echo.

REM Comprehensive prerequisite checking
call :print_info "Performing comprehensive system validation..."

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python not found. Please install Python 3.11+"
    call :print_info "Download from: https://python.org"
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
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
call :print_success "Python %PYTHON_VERSION% validated"

REM Check/install uv with enhanced error handling
uv --version >nul 2>&1
if errorlevel 1 (
    call :print_warning "uv not found. Installing latest version..."
    python -m pip install --upgrade uv
    if errorlevel 1 (
        call :print_error "Failed to install uv. Trying alternative method..."
        curl -LsSf https://astral.sh/uv/install.ps1 | powershell -c -
        if errorlevel 1 (
            call :print_error "Failed to install uv. Please install manually."
            pause
            exit /b 1
        )
    )
    
    REM Verify installation
    uv --version >nul 2>&1
    if errorlevel 1 (
        call :print_error "uv installation verification failed"
        pause
        exit /b 1
    )
)

for /f "tokens=*" %%i in ('uv --version 2^>^&1') do set UV_VERSION=%%i
call :print_success "%UV_VERSION% validated"

REM Check Git (optional but recommended)
git --version >nul 2>&1
if errorlevel 1 (
    call :print_warning "Git not found. Some features may be limited."
    set "GIT_AVAILABLE=false"
) else (
    for /f "tokens=*" %%i in ('git --version 2^>^&1') do set GIT_VERSION=%%i
    call :print_success "%GIT_VERSION% available"
    set "GIT_AVAILABLE=true"
)

REM Check Node.js (for UI development)
node --version >nul 2>&1
if errorlevel 1 (
    call :print_warning "Node.js not found. UI development will be limited."
    set "NODE_AVAILABLE=false"
) else (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    call :print_success "Node.js %NODE_VERSION% available"
    set "NODE_AVAILABLE=true"
)

echo.
call :print_header "Setting up development environment..."

REM Create and setup virtual environment
if not exist ".venv" (
    call :print_info "Creating virtual environment..."
    uv venv --python %MAJOR%.%MINOR%
    if errorlevel 1 (
        call :print_error "Failed to create virtual environment"
        pause
        exit /b 1
    )
    call :print_success "Virtual environment created"
) else (
    call :print_success "Virtual environment exists"
)

REM Install dependencies with progress indication
call :print_info "Installing dependencies (this may take a few minutes)..."
uv sync --all-extras
if errorlevel 1 (
    call :print_error "Failed to install dependencies"
    call :print_info "Trying basic installation..."
    uv sync
    if errorlevel 1 (
        call :print_error "Basic installation also failed"
        pause
        exit /b 1
    )
    call :print_warning "Basic dependencies installed (some features may be limited)"
) else (
    call :print_success "All dependencies installed successfully"
)

REM Install Playwright browsers
call :print_info "Installing browser automation components..."
uv run playwright install --with-deps chromium >nul 2>&1
if errorlevel 1 (
    call :print_warning "Playwright installation had issues, but continuing..."
    call :print_info "You may need to run 'uv run playwright install' manually later"
) else (
    call :print_success "Browser automation ready"
)

REM Create necessary directories
call :print_info "Creating project directories..."
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "temp" mkdir temp
if not exist "workflows" mkdir workflows
call :print_success "Project structure created"

REM Setup environment files
call :print_info "Setting up configuration files..."

REM Create .env file if it doesn't exist
if not exist ".env" (
    (
    echo # Workflow-Use Suite Configuration
    echo # Generated by deploy-dev.bat
    echo.
    echo # Environment
    echo ENVIRONMENT=development
    echo DEBUG=true
    echo.
    echo # API Configuration
    echo API_HOST=127.0.0.1
    echo API_PORT=8000
    echo.
    echo # Web UI Configuration
    echo WEBUI_HOST=127.0.0.1
    echo WEBUI_PORT=7788
    echo.
    echo # Browser Settings
    echo BROWSER_HEADLESS=false
    echo BROWSER_DISABLE_SECURITY=true
    echo.
    echo # AI Provider API Keys ^(add your keys here^)
    echo # OPENAI_API_KEY=your_openai_api_key_here
    echo # ANTHROPIC_API_KEY=your_anthropic_api_key_here
    echo # GOOGLE_API_KEY=your_google_api_key_here
    echo.
    echo # Logging
    echo LOG_LEVEL=INFO
    echo LOG_FILE_PATH=logs/workflow-use.log
    ) > .env
    call :print_success "Configuration file created (.env)"
    call :print_warning "Please edit .env to add your AI provider API keys"
) else (
    call :print_success "Configuration file exists"
)

REM Create workflows/.env if workflows directory exists
if exist "workflows" (
    if not exist "workflows\.env" (
        if exist "workflows\.env.example" (
            copy "workflows\.env.example" "workflows\.env" >nul
            call :print_success "Workflow configuration created"
        ) else (
            (
            echo # Workflow Backend Configuration
            echo OPENAI_API_KEY=your_openai_api_key_here
            echo ANTHROPIC_API_KEY=your_anthropic_api_key_here
            echo GOOGLE_API_KEY=your_google_api_key_here
            ) > workflows\.env
            call :print_success "Basic workflow configuration created"
        )
        call :print_warning "Please edit workflows\.env to add your API keys"
    )
)

echo.
call :print_header "Creating launch scripts..."

REM Create enhanced start.bat
(
echo @echo off
echo setlocal
echo.
echo REM Enhanced Quick Start Script for Workflow-Use Suite
echo REM Generated by deploy-dev.bat v2.0
echo.
echo echo.
echo echo ==========================================
echo echo   🚀 Starting Workflow-Use Suite v2.0
echo echo ==========================================
echo echo.
echo.
echo REM Validate environment
echo if not exist ".venv" ^(
echo     echo ❌ Virtual environment not found. Please run deploy-dev.bat first.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo if not exist "pyproject.toml" ^(
echo     echo ❌ Project configuration not found. Please run from project root.
echo     pause
echo     exit /b 1
echo ^)
echo.
echo REM Check for updates
echo echo 🔍 Checking for dependency updates...
echo uv sync --quiet
echo.
echo echo 🎯 Services will be available at:
echo echo   📡 Backend API: http://127.0.0.1:8000
echo echo   📚 API Documentation: http://127.0.0.1:8000/docs
echo echo   🌐 Browser Web-UI: http://127.0.0.1:7788
echo echo   ⚛️ Workflow UI: http://127.0.0.1:5173
echo echo.
echo echo 💡 Press Ctrl+C to stop all services
echo echo ⚡ Starting enhanced launcher...
echo echo.
echo.
echo REM Start the enhanced suite with monitoring
echo uv run python main.py suite
echo.
echo echo.
echo echo 🛑 All services stopped.
echo echo 👋 Thank you for using Workflow-Use Suite!
echo pause
) > start.bat

call :print_success "Enhanced start.bat created"

REM Create component-specific launchers
(
echo @echo off
echo echo 🔧 Starting Backend API Only...
echo echo 📡 API will be available at: http://127.0.0.1:8000
echo echo 📚 Documentation at: http://127.0.0.1:8000/docs
echo echo.
echo uv run python main.py backend
echo pause
) > start-backend.bat

(
echo @echo off
echo echo 🌐 Starting Browser Web-UI Only...
echo echo 🌐 Interface will be available at: http://127.0.0.1:7788
echo echo.
echo uv run python main.py webui
echo pause
) > start-webui.bat

(
echo @echo off
echo echo ⚛️ Starting Workflow UI Only...
echo echo ⚛️ Interface will be available at: http://127.0.0.1:5173
echo echo.
echo uv run python main.py ui
echo pause
) > start-ui.bat

(
echo @echo off
echo echo 📊 Checking Service Status...
echo echo.
echo uv run python main.py status
echo echo.
echo pause
) > status.bat

call :print_success "Component launchers created"

REM Create development utilities
(
echo @echo off
echo echo 🧹 Cleaning up temporary files and caches...
echo if exist "temp" rmdir /s /q temp
echo if exist "__pycache__" rmdir /s /q __pycache__
echo if exist ".pytest_cache" rmdir /s /q .pytest_cache
echo mkdir temp
echo echo ✅ Cleanup completed
echo pause
) > cleanup.bat

(
echo @echo off
echo echo 🔄 Updating Workflow-Use Suite...
echo echo.
echo echo Updating dependencies...
echo uv sync --upgrade
echo echo.
echo echo Updating browser components...
echo uv run playwright install --with-deps
echo echo.
echo echo ✅ Update completed
echo pause
) > update.bat

call :print_success "Development utilities created"

echo.
call :print_success "🎉 Enhanced development setup complete!"
echo.
echo %CYAN%📋 What was created:%RESET%
echo   - .venv/ (virtual environment with all dependencies)
echo   - .env (main configuration file)
echo   - start.bat (enhanced main launcher)
echo   - start-backend.bat (backend API only)
echo   - start-webui.bat (browser web-ui only)
echo   - start-ui.bat (workflow UI only)
echo   - status.bat (service status checker)
echo   - cleanup.bat (development cleanup utility)
echo   - update.bat (dependency update utility)
echo.
echo %YELLOW%💡 Next steps:%RESET%
echo   1. Edit .env to add your AI provider API keys
echo   2. Run start.bat to launch the complete suite
echo   3. Use component launchers for specific services
echo.
echo %GREEN%🚀 Quick launch commands:%RESET%
echo   - start.bat (complete suite with monitoring)
echo   - start-backend.bat (API server only)
echo   - start-webui.bat (browser automation UI)
echo   - start-ui.bat (workflow management UI)
echo   - status.bat (check service status)
echo.
echo %MAGENTA%🔧 Development utilities:%RESET%
echo   - cleanup.bat (clean temporary files)
echo   - update.bat (update dependencies)
echo.

REM Ask if user wants to start now
set /p launch_now="Would you like to start the complete suite now? (y/N): "
if /i "%launch_now%"=="y" (
    echo.
    call :print_header "Launching Workflow-Use Suite..."
    call start.bat
) else (
    echo.
    call :print_info "Setup complete! Run start.bat when ready to begin."
    echo.
    call :print_success "Happy automating! 🎉"
)

echo.
pause

