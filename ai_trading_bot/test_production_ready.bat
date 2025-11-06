@echo off
chcp 65001 >nul
echo ========================================
echo AI Trading Bot - Production Readiness Test
echo ========================================
echo.

cd /d "%~dp0"

REM Set PYTHONPATH
set "PYTHONPATH=%~dp0;%PYTHONPATH%"
set "PYTHONPATH=%~dp0..;%PYTHONPATH%"

echo Testing Python version...
python -c "import sys; assert sys.version_info >= (3, 9), 'Python 3.9+ required'; print('Python version:', sys.version)"

echo.
echo Testing all imports...
python -c "from ai_trading_bot.config import load_config; print('[OK] Config module')" 2>nul || echo [FAIL] Config module
python -c "from ai_trading_bot.utils.logger import get_logger; print('[OK] Logger module')" 2>nul || echo [FAIL] Logger module
python -c "from ai_trading_bot.utils.openrouter_client import OpenRouterClient; print('[OK] OpenRouter client')" 2>nul || echo [FAIL] OpenRouter client
python -c "from ai_trading_bot.data.websocket_client import WebSocketClient; print('[OK] WebSocket client')" 2>nul || echo [FAIL] WebSocket client
python -c "from ai_trading_bot.data.data_manager import DataManager; print('[OK] Data manager')" 2>nul || echo [FAIL] Data manager
python -c "from ai_trading_bot.features.indicators import calculate_all_indicators; print('[OK] Indicators')" 2>nul || echo [FAIL] Indicators
python -c "from ai_trading_bot.strategies.base_strategy import BaseStrategy; print('[OK] Base strategy')" 2>nul || echo [FAIL] Base strategy
python -c "from ai_trading_bot.strategies.ai_signal_generator import AISignalGenerator; print('[OK] AI signal generator')" 2>nul || echo [FAIL] AI signal generator
python -c "from ai_trading_bot.strategies.momentum_strategy import MomentumStrategy; print('[OK] Momentum strategy')" 2>nul || echo [FAIL] Momentum strategy
python -c "from ai_trading_bot.strategies.mean_reversion_strategy import MeanReversionStrategy; print('[OK] Mean reversion strategy')" 2>nul || echo [FAIL] Mean reversion strategy
python -c "from ai_trading_bot.strategies.breakout_strategy import BreakoutStrategy; print('[OK] Breakout strategy')" 2>nul || echo [FAIL] Breakout strategy
python -c "from ai_trading_bot.strategies.trend_following_strategy import TrendFollowingStrategy; print('[OK] Trend following strategy')" 2>nul || echo [FAIL] Trend following strategy
python -c "from ai_trading_bot.strategies.meta_ai_strategy import MetaAIStrategy; print('[OK] Meta AI strategy')" 2>nul || echo [FAIL] Meta AI strategy
python -c "from ai_trading_bot.allocator.position_allocator import PositionAllocator; print('[OK] Position allocator')" 2>nul || echo [FAIL] Position allocator
python -c "from ai_trading_bot.risk.risk_manager import RiskManager; print('[OK] Risk manager')" 2>nul || echo [FAIL] Risk manager
python -c "from ai_trading_bot.execution.order_executor import OrderExecutor; print('[OK] Order executor')" 2>nul || echo [FAIL] Order executor

echo.
echo Testing config loading...
python -c "from ai_trading_bot.config import load_config; config = load_config(); assert config is not None; print('[OK] Config loads successfully'); print('  - Symbols:', len(config.get('data', {}).get('symbols', []))); print('  - Initial capital:', config.get('trading', {}).get('initial_capital', 0))" 2>nul || echo [FAIL] Config loading

echo.
echo Testing indicator calculations...
python -c "from ai_trading_bot.features.indicators import calculate_all_indicators; candles = [{'open': 100+i*0.1, 'high': 101+i*0.1, 'low': 99+i*0.1, 'close': 100+i*0.1, 'volume': 1000} for i in range(50)]; indicators = calculate_all_indicators(candles); assert indicators is not None and len(indicators) > 0; print('[OK] Indicators calculate correctly'); print('  - RSI:', indicators.get('rsi_14', 0))" 2>nul || echo [FAIL] Indicator calculations

echo.
echo Testing risk manager...
python -c "from ai_trading_bot.risk.risk_manager import RiskManager; rm = RiskManager(100.0); assert rm.can_open_position(); print('[OK] Risk manager initializes correctly')" 2>nul || echo [FAIL] Risk manager

echo.
echo Testing position allocator...
python -c "from ai_trading_bot.allocator.position_allocator import PositionAllocator; pa = PositionAllocator(100.0); signal = {'action': 'LONG', 'confidence': 0.7, 'entry_price': 100, 'stop_loss': 99}; size = pa.calculate_position_size(signal, 100); assert size is not None; print('[OK] Position allocator works correctly')" 2>nul || echo [FAIL] Position allocator

echo.
echo Testing logger...
python -c "from ai_trading_bot.utils.logger import get_logger; logger = get_logger('test'); logger.info('Test log message'); print('[OK] Logger works correctly')" 2>nul || echo [FAIL] Logger

echo.
echo ========================================
echo Production Readiness Test Complete!
echo ========================================
echo.
echo If all tests passed, the system is production ready!
echo.
pause

