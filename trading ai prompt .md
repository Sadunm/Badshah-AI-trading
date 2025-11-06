# 🚀 COMPLETE AI TRADING BOT - 100% READY BUILD PROMPT

I need you to build a COMPLETE, PRODUCTION-READY AI Trading Bot from scratch. 
This must be 100% functional with ZERO errors, all modules included, and ready for deployment.

# 🎯 PROJECT REQUIREMENTS

## Core Specifications
- **Language**: Python 3.9+
- **Exchange**: Binance Testnet (paper trading)
- **Trading Type**: Spot trading
- **Capital**: $10.00
- **Deployment**: Render.com (Linux environment)
- **AI Integration**: OpenRouter API (DeepSeek model)

## Architecture Requirements
Build a COMPLETE multi-strategy AI trading system with these exact modules:

### 1. DATA LAYER (Real-Time Market Data)
- WebSocket client for real-time OHLCV and orderbook data
- REST API fallback for historical data (200 candles per symbol)
- Data caching and local storage (optional, graceful degradation)
- Auto-reconnection with exponential backoff
- Support for Binance testnet format
- Real-time price updates every 100ms (orderbook)
- 5-minute candle updates

### 2. FEATURES LAYER (Technical Indicators)
- RSI (14, 7 periods)
- MACD (12, 26, 9)
- Bollinger Bands (20, 2 std)
- ATR (14 period)
- Volume ratios and spikes
- Volatility calculations
- Z-score calculations
- Momentum indicators
- EMA/SMA (multiple periods)
- All indicators must handle edge cases (NaN, division by zero, insufficient data)

### 3. AI SIGNAL GENERATION (PRIMARY)
- OpenRouter API integration (DeepSeek model)
- Analyze market data and generate LONG/SHORT/FLAT signals
- 30-second timeout with graceful fallback
- Returns: action, confidence (0-1), entry_price, stop_loss, take_profit, reason
- Proper error handling and retry logic
- Environment variable support for API key

### 4. RULE-BASED STRATEGIES (SECONDARY - Fallback)
- Momentum Strategy (LightGBM-based)
- Mean Reversion Strategy (z-score, Bollinger Bands)
- Breakout Strategy (ATR, volatility expansion)
- Trend Following Strategy (TFT forecasting - simplified)
- All strategies must validate signals before returning
- Use safe_get_last() helper to prevent NumPy array comparison errors

### 5. META AI VALIDATION (Risk Filter)
- AI risk review using OpenRouter
- News check (optional)
- Anomaly detection (optional)
- Approve/reject signals before execution
- Fail-open design (approve if AI unavailable)

### 6. POSITION ALLOCATION
- Confidence-weighted allocation
- Max 1% risk per trade
- Max 20% total portfolio risk
- Position size calculation based on risk
- Portfolio risk limits

### 7. RISK MANAGEMENT
- Max drawdown: 5%
- Max daily loss: 2%
- Max daily trades: 100
- Stop loss based on ATR
- Position size limits
- Daily counter reset
- Trade recording and P&L tracking

### 8. EXECUTION LAYER
- Paper trading mode (simulated execution)
- Order slicing (TWAP/VWAP) - optional
- Slippage simulation
- Spread filtering
- Idempotency checks
- Fallback prices for paper trading

### 9. POSITION MONITORING (CRITICAL)
- Monitor every 5 seconds (real-time)
- Check stop loss immediately
- Check take profit immediately
- Close positions automatically when targets hit
- Calculate P&L with fees (0.1% each side)
- Update capital automatically
- Record trades in history

### 10. LOGGING SYSTEM
- Console logging (always works)
- File logging with multiple fallback directories
- Works even if file system is read-only
- Windows-safe Unicode handling
- Rotating file handler (10MB, 3 backups)

## 📁 FOLDER STRUCTURE

```
ai_trading_bot/
├── __init__.py
├── main.py                    # Main entry point
├── start.py                   # Alternative entry with error handling
├── config/
│   ├── __init__.py
│   └── config.yaml            # Complete config with env var support
├── data/
│   ├── __init__.py
│   ├── websocket_client.py    # WebSocket with auto-reconnect
│   └── data_manager.py        # Data fetching and caching
├── features/
│   ├── __init__.py
│   └── indicators.py          # All technical indicators
├── strategies/
│   ├── __init__.py
│   ├── base_strategy.py       # Abstract base class
│   ├── ai_signal_generator.py # PRIMARY: AI signal generation
│   ├── momentum_strategy.py
│   ├── mean_reversion_strategy.py
│   ├── breakout_strategy.py
│   ├── trend_following_strategy.py
│   └── meta_ai_strategy.py    # Risk filter
├── models/
│   ├── __init__.py
│   ├── lightgbm_model.py      # ML model (optional, not required)
│   └── tft_model.py           # Simplified TFT (optional)
├── allocator/
│   ├── __init__.py
│   └── position_allocator.py  # Position allocation logic
├── risk/
│   ├── __init__.py
│   └── risk_manager.py        # Risk management
├── execution/
│   ├── __init__.py
│   └── order_executor.py      # Order execution (paper trading)
├── utils/
│   ├── __init__.py
│   ├── logger.py              # Logging system
│   └── openrouter_client.py  # OpenRouter API client
├── requirements.txt           # All dependencies
├── Procfile                   # Render deployment
├── runtime.txt                # Python version
├── render.yaml                # Render config
└── README.md                  # Setup guide
```

## 🔧 CRITICAL REQUIREMENTS

### 1. Error Handling
- ALL file operations must have try/except
- ALL API calls must have timeout and retry
- ALL calculations must check for division by zero
- Bot continues even if components fail (graceful degradation)
- No crashes on missing files/directories

### 2. Real-Time Trading
- Position monitoring every 5 seconds
- Signal generation every 30 seconds
- WebSocket price updates every 100ms
- Stop loss/take profit checked immediately
- Positions closed automatically

### 3. Isolation
- Complete isolation from parent directories
- Only relative imports within package
- No sys.path manipulation for parent dirs
- Self-contained logger

### 4. Configuration
- Environment variable support (${VAR})
- Config loading with fallbacks
- Multiple path fallbacks
- Clear warnings if env vars missing

### 5. Deployment (Render)
- Works on Linux (Render)
- All paths cross-platform
- Logging works without file system
- Graceful error handling everywhere

## 📊 TRADING LOGIC

### Main Loop Flow:
```
1. Initialize all components
2. Connect WebSocket
3. Fetch historical data (200 candles)
4. Start trading loop:
   a. Monitor positions (every 5s)
      - Check stop loss
      - Check take profit
      - Close if targets hit
   b. Generate signals (every 30s)
      - AI signal generator (PRIMARY)
      - Rule-based strategies (FALLBACK)
      - Meta AI validation
   c. Allocate positions
   d. Execute orders (paper trading)
   e. Track P&L
```

### Position Monitoring:
- Check every 5 seconds
- Get current price from WebSocket cache
- Calculate P&L: gross_profit - fees - slippage
- Close if stop_loss hit
- Close if take_profit hit
- Update capital automatically
- Record trade history

### Signal Generation Priority:
1. AI Signal Generator (DeepSeek) - PRIMARY
2. Rule-based strategies - FALLBACK if AI fails
3. Meta AI validation - APPROVE/REJECT

## 🛡️ ERROR PREVENTION

### Must Handle:
- WebSocket disconnection → Auto-reconnect
- API timeout → Fallback to rule-based
- Missing historical data → Continue with WebSocket
- File system read-only → Console logging only
- Config not found → Multiple path fallbacks
- NumPy array comparisons → Use safe_get_last()
- Division by zero → Check denominators
- Missing env vars → Clear warnings, continue

## 📝 CODE QUALITY

- All functions must have docstrings
- Type hints where possible
- Clear variable names
- Comprehensive error messages
- Logging at appropriate levels
- No hardcoded values (use config)
- Magic numbers avoided

## 🚀 DEPLOYMENT READINESS

- Requirements.txt with exact versions
- Procfile for Render
- runtime.txt (Python 3.11)
- render.yaml configuration
- Environment variable documentation
- README with setup instructions

## ✅ TESTING REQUIREMENTS

- All imports must work
- Bot initializes without errors
- WebSocket connects successfully
- Data fetching works
- Signal generation works
- Position monitoring works
- P&L calculation correct

## 📋 CONFIG STRUCTURE

```yaml
openrouter:
  api_key: "${OPENROUTER_API_KEY}"
  base_url: "https://openrouter.ai/api/v1"
  default_model: "deepseek/deepseek-chat"
  timeout: 30.0

exchange:
  name: "binance"
  testnet: true
  trading_type: "spot"
  api_key: "${BINANCE_API_KEY}"
  api_secret: "${BINANCE_API_SECRET}"
  websocket_url: "wss://testnet.binance.vision/ws"

trading:
  initial_capital: 100.0
  paper_trading: true
  max_position_size_pct: 1.0
  max_portfolio_risk_pct: 20.0

strategies:
  momentum:
    enabled: true
    min_confidence: 0.6
  mean_reversion:
    enabled: true
    min_confidence: 0.65
  breakout:
    enabled: true
    min_confidence: 0.7
  trend_following:
    enabled: true
    min_confidence: 0.75
  meta_ai:
    enabled: true
    risk_check_enabled: true

risk:
  max_drawdown_pct: 5.0
  max_daily_loss_pct: 2.0
  max_daily_trades: 100
  stop_loss_pct: 0.5
  take_profit_pct: 1.0

data:
  symbols:
    - BTCUSDT
    - ETHUSDT
    - BNBUSDT
    - SOLUSDT
    - XRPUSDT
    - ADAUSDT
    - DOGEUSDT
    - AVAXUSDT
    - LINKUSDT
    - MATICUSDT
  kline_interval: "5m"
  kline_limit: 200
```

## 🎯 EXPECTED OUTPUT

When bot runs, it should:
1. Initialize all components successfully
2. Connect to WebSocket
3. Fetch historical data
4. Start monitoring positions
5. Generate AI signals every 30s
6. Execute trades (paper trading)
7. Monitor and close positions automatically
8. Log all activities clearly

## ⚠️ CRITICAL: NO ERRORS ALLOWED

- Zero import errors
- Zero runtime errors
- Zero calculation errors
- Zero file operation errors
- Bot must run from first try
- All edge cases handled

## 📦 DELIVERABLES

1. Complete folder structure
2. All Python modules with full implementation
3. Config file with all settings
4. Requirements.txt
5. Deployment files (Procfile, runtime.txt, render.yaml)
6. README with setup instructions
7. Error handling everywhere
8. Logging system
9. Real-time trading loop
10. Position monitoring
11. P&L tracking

## 🚨 IMPORTANT NOTES

- Use relative imports only (from .module import Class)
- All paths must be cross-platform (use Path())
- WebSocket must handle Binance format correctly
- AI timeout must be 30 seconds max
- Position monitoring must be every 5 seconds
- All prices must come from real-time WebSocket
- Fees must be calculated correctly (0.1% each side)
- Bot must continue even if AI fails
- Bot must continue even if file system fails

## 🎓 LESSONS FROM PREVIOUS BUILD

Based on experience, ensure:
1. Position monitoring loop exists (was missing before)
2. AI timeout implemented (was hanging before)
3. Order executor fallback prices (was failing before)
4. Complete isolation (was conflicting before)
5. Safe NumPy array handling (was erroring before)
6. Real-time price updates (was stale before)
7. Proper P&L calculation (was wrong before)

---

BUILD THIS COMPLETE SYSTEM WITH ALL MODULES, ZERO ERRORS, 100% READY FOR DEPLOYMENT.
MAKE IT PRODUCTION-READY FROM THE START.
