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
) > pyproject_simple.toml

REM Use the simple pyproject.toml for installation
copy pyproject_simple.toml pyproject.toml >nul

uv sync
if errorlevel 1 (
    echo %RED%❌ Failed to install dependencies%RESET%
    pause
    exit /b 1
)
echo %GREEN%✅ Dependencies installed%RESET%
