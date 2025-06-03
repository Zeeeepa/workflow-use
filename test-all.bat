@echo off
setlocal enabledelayedexpansion

REM Comprehensive Test Runner for Workflow-Use Suite
REM Validates all features and function sequences

echo.
echo ==========================================
echo   🧪 Workflow-Use Suite Validation
echo ==========================================
echo.

REM Color definitions
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "MAGENTA=[95m"
set "RESET=[0m"

echo %CYAN%🔍 Starting comprehensive validation...%RESET%
echo.

REM Check if validation script exists
if not exist "validate.py" (
    echo %RED%❌ validate.py not found%RESET%
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist ".venv" (
    echo %YELLOW%⚠️ Virtual environment not found. Running deploy.bat first...%RESET%
    if exist "deploy.bat" (
        call deploy.bat
        if errorlevel 1 (
            echo %RED%❌ Deployment failed%RESET%
            pause
            exit /b 1
        )
    ) else (
        echo %RED%❌ deploy.bat not found. Please run deployment first.%RESET%
        pause
        exit /b 1
    )
)

echo %CYAN%🧪 Running validation suite...%RESET%
echo.

REM Run the validation
uv run python validate.py
set VALIDATION_RESULT=%errorlevel%

echo.
echo %CYAN%📊 Validation completed with exit code: %VALIDATION_RESULT%%RESET%

REM Check if validation report was generated
if exist "validation_report.json" (
    echo %GREEN%✅ Validation report generated: validation_report.json%RESET%
    
    REM Display summary if possible
    echo.
    echo %CYAN%📋 Quick Summary:%RESET%
    findstr /C:"total_tests" /C:"passed" /C:"failed" /C:"success_rate" validation_report.json 2>nul
) else (
    echo %YELLOW%⚠️ No validation report generated%RESET%
)

echo.
if %VALIDATION_RESULT% EQU 0 (
    echo %GREEN%🎉 All validations passed! Workflow-Use Suite is ready.%RESET%
    echo.
    echo %CYAN%🚀 You can now use:%RESET%
    echo   - START.bat (complete suite)
    echo   - start-backend.bat (backend only)
    echo   - start-webui.bat (web-ui only)
) else (
    echo %YELLOW%⚠️ Some validations failed. Please review the results above.%RESET%
    echo.
    echo %CYAN%🔧 Common fixes:%RESET%
    echo   - Run deploy.bat to ensure proper setup
    echo   - Check that all dependencies are installed
    echo   - Verify Python 3.11+ is available
    echo   - Ensure uv package manager is installed
)

echo.
echo %CYAN%📄 For detailed results, check validation_report.json%RESET%
echo.

pause
exit /b %VALIDATION_RESULT%

