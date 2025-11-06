@echo off
chcp 65001 >nul
echo ========================================
echo AI Trading Bot - System Check
echo ========================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.9+ from https://www.python.org/
    goto end
) else (
    echo [OK] Python found
    python --version
)

echo.
echo Checking dependencies...
python -c "import numpy" >nul 2>&1
if errorlevel 1 (
    echo [MISSING] NumPy - Run install.bat
) else (
    echo [OK] NumPy installed
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo [MISSING] Requests - Run install.bat
) else (
    echo [OK] Requests installed
)

python -c "import yaml" >nul 2>&1
if errorlevel 1 (
    echo [MISSING] PyYAML - Run install.bat
) else (
    echo [OK] PyYAML installed
)

python -c "import websocket" >nul 2>&1
if errorlevel 1 (
    echo [MISSING] WebSocket-Client - Run install.bat
) else (
    echo [OK] WebSocket-Client installed
)

echo.
echo Checking environment variables...
if "%OPENROUTER_API_KEY%"=="" (
    echo [WARNING] OPENROUTER_API_KEY not set
    echo AI features will not work without this
) else (
    echo [OK] OPENROUTER_API_KEY is set
)

if "%BINANCE_API_KEY%"=="" (
    echo [INFO] BINANCE_API_KEY not set (optional)
) else (
    echo [OK] BINANCE_API_KEY is set
)

echo.
echo Checking file structure...
if exist "config\config.yaml" (
    echo [OK] Config file exists
) else (
    echo [ERROR] Config file not found!
)

if exist "main.py" (
    echo [OK] main.py exists
) else (
    echo [ERROR] main.py not found!
)

if exist "requirements.txt" (
    echo [OK] requirements.txt exists
) else (
    echo [ERROR] requirements.txt not found!
)

echo.
echo Checking directories...
if exist "data" (
    echo [OK] data/ directory exists
) else (
    echo [ERROR] data/ directory not found!
)

if exist "strategies" (
    echo [OK] strategies/ directory exists
) else (
    echo [ERROR] strategies/ directory not found!
)

if exist "utils" (
    echo [OK] utils/ directory exists
) else (
    echo [ERROR] utils/ directory not found!
)

echo.
echo ========================================
echo System check complete!
echo ========================================
echo.

:end
pause

