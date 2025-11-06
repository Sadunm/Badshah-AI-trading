@echo off
chcp 65001 >nul
echo ========================================
echo AI Trading Bot - Quick Start Guide
echo ========================================
echo.

cd /d "%~dp0"

echo Step 1: Installing dependencies...
call install.bat
if errorlevel 1 (
    echo Installation failed!
    pause
    exit /b 1
)

echo.
echo Step 2: Setting up environment variables...
echo (You can skip this if you already set them)
echo.
choice /C YN /M "Do you want to set environment variables now?"
if errorlevel 2 goto skip_env
if errorlevel 1 call setup_env.bat

:skip_env
echo.
echo Step 3: Testing imports...
call test_imports.bat
if errorlevel 1 (
    echo Import test failed! Please check the errors above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo To run the bot, use:
echo   run_bot.bat
echo.
echo Or use the alternative entry point:
echo   run_bot_start.bat
echo.
pause

