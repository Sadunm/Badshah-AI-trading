@echo off
echo ========================================
echo AI Trading Bot - Environment Setup
echo ========================================
echo.

cd /d "%~dp0"

echo Setting up environment variables...
echo.
echo Enter your OpenRouter API Key (required):
set /p OPENROUTER_API_KEY="OpenRouter API Key: "

echo.
echo Enter your Binance API Key (optional, press Enter to skip):
set /p BINANCE_API_KEY="Binance API Key: "

echo.
echo Enter your Binance API Secret (optional, press Enter to skip):
set /p BINANCE_API_SECRET="Binance API Secret: "

echo.
echo Setting environment variables for this session...
setx OPENROUTER_API_KEY "%OPENROUTER_API_KEY%" >nul 2>&1
if not "%BINANCE_API_KEY%"=="" setx BINANCE_API_KEY "%BINANCE_API_KEY%" >nul 2>&1
if not "%BINANCE_API_SECRET%"=="" setx BINANCE_API_SECRET "%BINANCE_API_SECRET%" >nul 2>&1

echo.
echo Environment variables set!
echo.
echo NOTE: These are set permanently. To change them, run this script again.
echo.
pause

