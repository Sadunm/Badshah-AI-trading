@echo off
echo ========================================
echo AI Trading Bot - Starting (Alternative Entry)
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

REM Set PYTHONPATH to current directory
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
set "PYTHONPATH=%~dp0..;%PYTHONPATH%"

echo Starting bot using start.py...
echo.

python -m ai_trading_bot.start

if errorlevel 1 (
    echo.
    echo ERROR: Bot crashed!
    pause
    exit /b 1
)

