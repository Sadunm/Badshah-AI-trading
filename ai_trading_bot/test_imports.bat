@echo off
echo ========================================
echo AI Trading Bot - Testing Imports
echo ========================================
echo.

cd /d "%~dp0"

REM Set PYTHONPATH
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
set "PYTHONPATH=%~dp0..;%PYTHONPATH%"

echo Testing Python imports...
echo.

python -c "print('Testing imports...')"
python -c "import sys; print('Python version:', sys.version)"
python -c "import numpy; print('NumPy:', numpy.__version__)"
python -c "import requests; print('Requests:', requests.__version__)"
python -c "import yaml; print('PyYAML: OK')"
python -c "import websocket; print('WebSocket: OK')"

echo.
echo Testing bot modules...
echo.

python -c "from ai_trading_bot.config import load_config; print('Config: OK')"
python -c "from ai_trading_bot.utils.logger import get_logger; print('Logger: OK')"
python -c "from ai_trading_bot.data.websocket_client import WebSocketClient; print('WebSocket Client: OK')"
python -c "from ai_trading_bot.data.data_manager import DataManager; print('Data Manager: OK')"
python -c "from ai_trading_bot.features.indicators import calculate_all_indicators; print('Indicators: OK')"
python -c "from ai_trading_bot.strategies.ai_signal_generator import AISignalGenerator; print('AI Strategy: OK')"
python -c "from ai_trading_bot.risk.risk_manager import RiskManager; print('Risk Manager: OK')"
python -c "from ai_trading_bot.execution.order_executor import OrderExecutor; print('Order Executor: OK')"

echo.
echo Testing config loading...
python -c "from ai_trading_bot.config import load_config; config = load_config(); print('Config loaded:', 'OK' if config else 'FAILED')"

echo.
echo ========================================
echo Import test completed!
echo ========================================
pause

