@echo off
setlocal enabledelayedexpansion

REM Advanced Workflow-Use Suite Deployment Script
REM Enhanced version with Docker support, health checks, and advanced configuration

echo.
echo =============================================
echo   Advanced Workflow-Use Suite Deployment
echo =============================================
echo.

REM Color definitions (for Windows 10+)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "MAGENTA=[95m"
set "BOLD=[1m"
set "RESET=[0m"

REM Configuration variables
set "PROJECT_NAME=workflow-use-suite"
set "BACKEND_PORT=8000"
set "WEBUI_PORT=7788"
set "UI_PORT=5173"
set "DOCKER_COMPOSE_FILE=docker-compose.yml"

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

:check_port
netstat -an | findstr ":%~1 " >nul 2>&1
if errorlevel 1 (
    exit /b 0
) else (
    exit /b 1
)

:wait_for_service
set "url=%~1"
set "timeout=%~2"
if "%timeout%"=="" set "timeout=30"

for /l %%i in (1,1,%timeout%) do (
    curl -s "%url%" >nul 2>&1
    if not errorlevel 1 (
        call :print_success "Service at %url% is ready"
        exit /b 0
    )
    timeout /t 1 /nobreak >nul
)
call :print_warning "Service at %url% did not respond within %timeout% seconds"
exit /b 1

:main

REM Check if we're in the right directory
if not exist "pyproject.toml" (
    if not exist "workflows" (
        call :print_error "Neither pyproject.toml nor workflows directory found."
        call :print_error "Please run this script from the workflow-use project root."
        pause
        exit /b 1
    )
)

call :print_header "Advanced Workflow-Use Suite Deployment"
echo.

REM Enhanced prerequisite checking
call :print_info "Performing comprehensive system check..."

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    call :print_error "Python not found. Please install Python 3.11+ from https://python.org"
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
call :print_success "Python %PYTHON_VERSION% ✓"

REM Check uv with auto-installation
uv --version >nul 2>&1
if errorlevel 1 (
    call :print_warning "uv not found. Installing uv..."
    python -m pip install uv
    if errorlevel 1 (
        call :print_error "Failed to install uv. Please install manually: https://docs.astral.sh/uv/"
        pause
        exit /b 1
    )
    uv --version >nul 2>&1
    if errorlevel 1 (
        call :print_error "uv installation failed. Please install manually."
        pause
        exit /b 1
    )
)
for /f "tokens=*" %%i in ('uv --version 2^>^&1') do set UV_VERSION=%%i
call :print_success "%UV_VERSION% ✓"

REM Check Git
git --version >nul 2>&1
if errorlevel 1 (
    call :print_warning "Git not found. Some features may not work."
    set "GIT_AVAILABLE=false"
) else (
    for /f "tokens=*" %%i in ('git --version 2^>^&1') do set GIT_VERSION=%%i
    call :print_success "%GIT_VERSION% ✓"
    set "GIT_AVAILABLE=true"
)

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    call :print_warning "Node.js not found. UI development server will not be available."
    set "NODE_AVAILABLE=false"
) else (
    for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VERSION=%%i
    call :print_success "Node.js %NODE_VERSION% ✓"
    set "NODE_AVAILABLE=true"
)

REM Check Docker
docker --version >nul 2>&1
if errorlevel 1 (
    call :print_warning "Docker not found. Docker deployment will not be available."
    set "DOCKER_AVAILABLE=false"
) else (
    for /f "tokens=*" %%i in ('docker --version 2^>^&1') do set DOCKER_VERSION=%%i
    call :print_success "%DOCKER_VERSION% ✓"
    set "DOCKER_AVAILABLE=true"
)

REM Check curl for health checks
curl --version >nul 2>&1
if errorlevel 1 (
    call :print_warning "curl not found. Health checks will be limited."
    set "CURL_AVAILABLE=false"
) else (
    call :print_success "curl available ✓"
    set "CURL_AVAILABLE=true"
)

echo.
call :print_info "System check complete. Proceeding with deployment options..."
echo.

REM Port availability check
call :print_info "Checking port availability..."
call :check_port %BACKEND_PORT%
if errorlevel 1 (
    call :print_warning "Port %BACKEND_PORT% is already in use"
    set "BACKEND_PORT_AVAILABLE=false"
) else (
    call :print_success "Port %BACKEND_PORT% available"
    set "BACKEND_PORT_AVAILABLE=true"
)

call :check_port %WEBUI_PORT%
if errorlevel 1 (
    call :print_warning "Port %WEBUI_PORT% is already in use"
    set "WEBUI_PORT_AVAILABLE=false"
) else (
    call :print_success "Port %WEBUI_PORT% available"
    set "WEBUI_PORT_AVAILABLE=true"
)

call :check_port %UI_PORT%
if errorlevel 1 (
    call :print_warning "Port %UI_PORT% is already in use"
    set "UI_PORT_AVAILABLE=false"
) else (
    call :print_success "Port %UI_PORT% available"
    set "UI_PORT_AVAILABLE=true"
)

echo.
call :print_info "Choose deployment mode:"
echo 1. Quick Setup (Backend + Web-UI)
echo 2. Development Suite (All components)
echo 3. Backend Only (API server)
echo 4. Web-UI Only (Browser automation)
echo 5. Docker Deployment (Containerized)
echo 6. Custom Configuration
echo 7. Health Check (Check running services)
echo 8. Clean Installation (Remove and reinstall)
echo 9. Exit
echo.

set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto :quick_setup
if "%choice%"=="2" goto :dev_suite
if "%choice%"=="3" goto :backend_only
if "%choice%"=="4" goto :webui_only
if "%choice%"=="5" goto :docker_deploy
if "%choice%"=="6" goto :custom_config
if "%choice%"=="7" goto :health_check
if "%choice%"=="8" goto :clean_install
if "%choice%"=="9" goto :exit
goto :invalid_choice

:quick_setup
echo.
call :print_header "Quick Setup - Backend + Web-UI"
call :setup_environment
if errorlevel 1 exit /b 1
call :print_info "Starting backend and web-ui..."
start /B uv run python main.py backend
timeout /t 3 /nobreak >nul
start /B uv run python main.py webui
call :wait_for_service "http://127.0.0.1:%WEBUI_PORT%" 30
call :print_success "Quick setup complete!"
call :print_info "Web-UI: http://127.0.0.1:%WEBUI_PORT%"
call :print_info "Backend API: http://127.0.0.1:%BACKEND_PORT%"
goto :end

:dev_suite
echo.
call :print_header "Development Suite - All Components"
call :setup_environment
if errorlevel 1 exit /b 1
call :print_info "Starting complete development suite..."
uv run python main.py suite
goto :end

:backend_only
echo.
call :print_header "Backend Only - API Server"
call :setup_environment
if errorlevel 1 exit /b 1
call :print_info "Starting backend API server..."
uv run python main.py backend
goto :end

:webui_only
echo.
call :print_header "Web-UI Only - Browser Automation"
call :setup_environment
if errorlevel 1 exit /b 1
call :print_info "Starting browser-use web-ui..."
uv run python main.py webui
goto :end

:docker_deploy
echo.
call :print_header "Docker Deployment"
if "%DOCKER_AVAILABLE%"=="false" (
    call :print_error "Docker is not available. Please install Docker Desktop."
    pause
    goto :main
)
call :create_docker_compose
call :print_info "Starting Docker containers..."
docker compose up --build -d
if errorlevel 1 (
    call :print_error "Docker deployment failed"
    pause
    goto :main
)
call :print_success "Docker deployment complete!"
call :print_info "Services will be available shortly..."
goto :end

:custom_config
echo.
call :print_header "Custom Configuration"
echo.
set /p custom_backend_port="Backend port (default %BACKEND_PORT%): "
if not "%custom_backend_port%"=="" set "BACKEND_PORT=%custom_backend_port%"

set /p custom_webui_port="Web-UI port (default %WEBUI_PORT%): "
if not "%custom_webui_port%"=="" set "WEBUI_PORT=%custom_webui_port%"

set /p custom_ui_port="UI port (default %UI_PORT%): "
if not "%custom_ui_port%"=="" set "UI_PORT=%custom_ui_port%"

echo.
call :print_info "Custom configuration:"
call :print_info "Backend: %BACKEND_PORT%"
call :print_info "Web-UI: %WEBUI_PORT%"
call :print_info "UI: %UI_PORT%"
echo.
pause
goto :main

:health_check
echo.
call :print_header "Health Check - Service Status"
echo.

if "%CURL_AVAILABLE%"=="true" (
    call :print_info "Checking backend health..."
    curl -s "http://127.0.0.1:%BACKEND_PORT%/health" >nul 2>&1
    if not errorlevel 1 (
        call :print_success "Backend is healthy"
    ) else (
        call :print_warning "Backend is not responding"
    )

    call :print_info "Checking web-ui health..."
    curl -s "http://127.0.0.1:%WEBUI_PORT%" >nul 2>&1
    if not errorlevel 1 (
        call :print_success "Web-UI is healthy"
    ) else (
        call :print_warning "Web-UI is not responding"
    )
) else (
    call :print_warning "curl not available, checking processes..."
    tasklist | findstr python >nul 2>&1
    if not errorlevel 1 (
        call :print_info "Python processes are running"
    ) else (
        call :print_warning "No Python processes found"
    )
)

echo.
pause
goto :main

:clean_install
echo.
call :print_header "Clean Installation"
call :print_warning "This will remove the virtual environment and reinstall everything."
set /p confirm="Are you sure? (y/N): "
if /i not "%confirm%"=="y" goto :main

call :print_info "Removing virtual environment..."
if exist ".venv" rmdir /s /q ".venv"
if exist "browser-use-web-ui" rmdir /s /q "browser-use-web-ui"

call :print_info "Starting fresh installation..."
call :setup_environment
if errorlevel 1 exit /b 1
call :print_success "Clean installation complete!"
pause
goto :main

:setup_environment
call :print_info "Setting up Python environment..."

REM Create virtual environment in project root
if not exist ".venv" (
    call :print_info "Creating virtual environment..."
    uv venv
    if errorlevel 1 (
        call :print_error "Failed to create virtual environment"
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

exit /b 0

:create_docker_compose
call :print_info "Creating Docker Compose configuration..."
(
echo version: '3.8'
echo services:
echo   workflow-backend:
echo     build:
echo       context: ./workflows
echo       dockerfile: Dockerfile
echo     ports:
echo       - "%BACKEND_PORT%:%BACKEND_PORT%"
echo     environment:
echo       - PORT=%BACKEND_PORT%
echo     volumes:
echo       - ./workflows/.env:/app/.env
echo.
echo   browser-use-webui:
echo     build:
echo       context: ./browser-use-web-ui
echo       dockerfile: Dockerfile
echo     ports:
echo       - "%WEBUI_PORT%:%WEBUI_PORT%"
echo     environment:
echo       - PORT=%WEBUI_PORT%
echo     volumes:
echo       - ./browser-use-web-ui/.env:/app/.env
echo.
echo   workflow-ui:
echo     build:
echo       context: ./ui
echo       dockerfile: Dockerfile
echo     ports:
echo       - "%UI_PORT%:%UI_PORT%"
echo     depends_on:
echo       - workflow-backend
) > %DOCKER_COMPOSE_FILE%
call :print_success "Docker Compose configuration created"
goto :eof

:invalid_choice
call :print_error "Invalid choice. Please select 1-9."
pause
goto :main

:exit
echo.
call :print_info "Exiting advanced deployment script..."
goto :end

:end
echo.
call :print_success "Advanced deployment script completed!"
echo.
echo %CYAN%📖 Service URLs:%RESET%
echo   - Backend API: http://127.0.0.1:%BACKEND_PORT%
echo   - API Documentation: http://127.0.0.1:%BACKEND_PORT%/docs
echo   - Browser-Use Web-UI: http://127.0.0.1:%WEBUI_PORT%
echo   - Workflow UI: http://127.0.0.1:%UI_PORT%
echo.
echo %YELLOW%💡 Advanced Commands:%RESET%
echo   - Health check: deploy-advanced.bat (option 7)
echo   - Clean install: deploy-advanced.bat (option 8)
echo   - Custom ports: deploy-advanced.bat (option 6)
echo   - Docker deploy: deploy-advanced.bat (option 5)
echo.
echo %MAGENTA%🔧 Manual Commands:%RESET%
echo   - Backend: uv run python main.py backend
echo   - Web-UI: uv run python main.py webui
echo   - Suite: uv run python main.py suite
echo.
pause

