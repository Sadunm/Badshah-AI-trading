@echo off
echo ========================================
echo AI Trading Bot - Starting...
echo ========================================
echo.

cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    pause
    exit /b 1
)

REM Check if dependencies are installed
python -c "import numpy, requests, yaml" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Dependencies not installed!
    echo Please run install.bat first
    pause
    exit /b 1
)

REM Set PYTHONPATH to current directory
set "PYTHONPATH=%~dp0;%PYTHONPATH%"

REM Add parent directory to path for imports
set "PYTHONPATH=%~dp0..;%PYTHONPATH%"

echo Current directory: %CD%
echo Python path: %PYTHONPATH%
echo.

REM Check environment variables
if "%OPENROUTER_API_KEY%"=="" (
    echo WARNING: OPENROUTER_API_KEY not set!
    echo AI features may not work. Run setup_env.bat to set it.
    echo.
)

echo Starting bot...
echo Press Ctrl+C to stop
echo.

REM Run the bot
python -m ai_trading_bot.main

if errorlevel 1 (
    echo.
    echo ERROR: Bot crashed!
    echo Check the logs for details.
    pause
    exit /b 1
)

