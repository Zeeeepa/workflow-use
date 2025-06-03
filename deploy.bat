@echo off
setlocal enabledelayedexpansion

REM Simple Single Deployment Script for Workflow-Use Suite
REM Creates START.bat for easy launching

echo.
echo ==========================================
echo   Workflow-Use Suite - Simple Deploy
echo ==========================================
echo.

REM Color definitions
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "RESET=[0m"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%❌ Python not found. Please install Python 3.11+%RESET%
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo %GREEN%✅ Python %PYTHON_VERSION% found%RESET%

REM Check/install uv
uv --version >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%⚠️ Installing uv...%RESET%
    python -m pip install uv
    if errorlevel 1 (
        echo %RED%❌ Failed to install uv%RESET%
        pause
        exit /b 1
    )
)

for /f "tokens=*" %%i in ('uv --version 2^>^&1') do set UV_VERSION=%%i
echo %GREEN%✅ %UV_VERSION% ready%RESET%

REM Create virtual environment
echo %CYAN%🔧 Setting up environment...%RESET%
if not exist ".venv" (
    uv venv
    if errorlevel 1 (
        echo %RED%❌ Failed to create virtual environment%RESET%
        pause
        exit /b 1
    )
    echo %GREEN%✅ Virtual environment created%RESET%
) else (
    echo %GREEN%✅ Virtual environment exists%RESET%
)

REM Install core dependencies only (no docker extras)
echo %CYAN%📦 Installing core dependencies...%RESET%
(
echo [project]
echo name = "workflow-use-suite"
echo version = "1.0.0"
echo description = "Workflow automation suite"
echo requires-python = ">=3.11"
echo dependencies = [
echo     "fastapi>=0.104.0",
echo     "uvicorn[standard]>=0.24.0",
echo     "pydantic>=2.5.0",
echo     "playwright>=1.40.0",
echo     "gradio>=4.0.0",
echo     "requests>=2.31.0",
echo     "python-dotenv>=1.0.0",
echo     "rich>=13.7.0",
echo     "psutil>=5.9.0",
echo     "click>=8.1.0",
echo ]
echo.
echo [build-system]
echo requires = ["hatchling"]
echo build-backend = "hatchling.build"
) > pyproject.toml

uv sync
if errorlevel 1 (
    echo %RED%❌ Failed to install dependencies%RESET%
    pause
    exit /b 1
)
echo %GREEN%✅ Dependencies installed%RESET%

REM Install browsers
echo %CYAN%🌐 Installing browsers...%RESET%
uv run playwright install chromium >nul 2>&1
if errorlevel 1 (
    echo %YELLOW%⚠️ Browser installation had issues%RESET%
) else (
    echo %GREEN%✅ Browsers ready%RESET%
)

REM Create directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "workflows" mkdir workflows

REM Create simple main.py
echo %CYAN%⚡ Creating launcher...%RESET%
(
echo import os
echo import sys
echo import time
echo import subprocess
echo import asyncio
echo from pathlib import Path
echo.
echo def start_backend^(^):
echo     """Start workflow backend"""
echo     print^("🔧 Starting backend..."^)
echo     workflows_dir = Path^("workflows"^)
echo     if workflows_dir.exists^(^):
echo         try:
echo             process = subprocess.Popen^([sys.executable, "-m", "backend.api"], cwd=workflows_dir^)
echo             print^("✅ Backend started at http://127.0.0.1:8000"^)
echo             return process
echo         except Exception as e:
echo             print^(f"❌ Backend failed: {e}"^)
echo     else:
echo         print^("⚠️ Workflows directory not found"^)
echo     return None
echo.
echo def start_webui^(^):
echo     """Start browser-use web-ui"""
echo     print^("🌐 Starting web-ui..."^)
echo     webui_dir = Path^("browser-use-web-ui"^)
echo     
echo     # Clone if needed
echo     if not webui_dir.exists^(^):
echo         print^("📥 Cloning web-ui..."^)
echo         try:
echo             subprocess.run^(["git", "clone", "https://github.com/browser-use/web-ui.git", "browser-use-web-ui"], check=True^)
echo             print^("✅ Web-UI cloned"^)
echo         except:
echo             print^("❌ Failed to clone web-ui"^)
echo             return None
echo     
echo     try:
echo         process = subprocess.Popen^([sys.executable, "app.py"], cwd=webui_dir^)
echo         print^("✅ Web-UI started at http://127.0.0.1:7788"^)
echo         return process
echo     except Exception as e:
echo         print^(f"❌ Web-UI failed: {e}"^)
echo     return None
echo.
echo def main^(^):
echo     """Main launcher"""
echo     if len^(sys.argv^) ^< 2:
echo         print^("Usage: python main.py [backend^|webui^|suite]"^)
echo         return
echo     
echo     command = sys.argv[1].lower^(^)
echo     processes = []
echo     
echo     try:
echo         if command == "backend":
echo             process = start_backend^(^)
echo             if process:
echo                 processes.append^(process^)
echo                 process.wait^(^)
echo         
echo         elif command == "webui":
echo             process = start_webui^(^)
echo             if process:
echo                 processes.append^(process^)
echo                 process.wait^(^)
echo         
echo         elif command == "suite":
echo             print^("🚀 Starting complete suite..."^)
echo             
echo             backend = start_backend^(^)
echo             if backend:
echo                 processes.append^(backend^)
echo                 time.sleep^(3^)
echo             
echo             webui = start_webui^(^)
echo             if webui:
echo                 processes.append^(webui^)
echo             
echo             if processes:
echo                 print^("\\n🎉 Suite is running!"^)
echo                 print^("📡 Backend: http://127.0.0.1:8000"^)
echo                 print^("🌐 Web-UI: http://127.0.0.1:7788"^)
echo                 print^("\\n💡 Press Ctrl+C to stop"^)
echo                 
echo                 try:
echo                     while any^(p.poll^(^) is None for p in processes^):
echo                         time.sleep^(1^)
echo                 except KeyboardInterrupt:
echo                     pass
echo         
echo         else:
echo             print^(f"❌ Unknown command: {command}"^)
echo     
echo     except KeyboardInterrupt:
echo         print^("\\n🛑 Stopping..."^)
echo     finally:
echo         for process in processes:
echo             if process and process.poll^(^) is None:
echo                 process.terminate^(^)
echo         print^("✅ Stopped"^)
echo.
echo if __name__ == "__main__":
echo     main^(^)
) > main.py

REM Create .env file
if not exist ".env" (
    (
    echo # Workflow-Use Suite Configuration
    echo ENVIRONMENT=development
    echo DEBUG=true
    echo.
    echo # API Keys ^(add your keys here^)
    echo # OPENAI_API_KEY=your_key_here
    echo # ANTHROPIC_API_KEY=your_key_here
    echo # GOOGLE_API_KEY=your_key_here
    ) > .env
    echo %GREEN%✅ Configuration file created%RESET%
)

REM Create START.bat
echo %CYAN%🚀 Creating START.bat...%RESET%
(
echo @echo off
echo echo.
echo echo ==========================================
echo echo   🚀 Workflow-Use Suite Launcher
echo echo ==========================================
echo echo.
echo echo Services will be available at:
echo echo   📡 Backend API: http://127.0.0.1:8000
echo echo   🌐 Browser Web-UI: http://127.0.0.1:7788
echo echo.
echo echo Press Ctrl+C to stop all services
echo echo.
echo.
echo uv run python main.py suite
echo.
echo echo.
echo echo 🛑 All services stopped.
echo pause
) > START.bat

REM Create component launchers
(
echo @echo off
echo echo 🔧 Starting Backend Only...
echo uv run python main.py backend
echo pause
) > start-backend.bat

(
echo @echo off
echo echo 🌐 Starting Web-UI Only...
echo uv run python main.py webui
echo pause
) > start-webui.bat

echo.
echo %GREEN%🎉 Deployment complete!%RESET%
echo.
echo %CYAN%📋 Created files:%RESET%
echo   - .venv/ (virtual environment)
echo   - START.bat (main launcher)
echo   - start-backend.bat (backend only)
echo   - start-webui.bat (web-ui only)
echo   - .env (configuration)
echo.
echo %YELLOW%💡 Next steps:%RESET%
echo   1. Edit .env to add your API keys
echo   2. Run START.bat to launch the suite
echo.
echo %GREEN%🚀 Quick commands:%RESET%
echo   - START.bat (complete suite)
echo   - start-backend.bat (backend only)
echo   - start-webui.bat (web-ui only)
echo.

REM Ask if user wants to start now
set /p launch_now="Start the suite now? (y/N): "
if /i "%launch_now%"=="y" (
    echo.
    echo %CYAN%🚀 Launching...%RESET%
    call START.bat
) else (
    echo.
    echo %GREEN%✅ Ready! Run START.bat when you want to begin.%RESET%
)

echo.
pause

