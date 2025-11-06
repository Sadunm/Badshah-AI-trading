# 🤖 BADSHAI AI Trading Bot

Complete production-ready AI trading bot with multi-strategy support, real-time market data, backtesting, and comprehensive risk management.

## ✨ Features

- **AI-Powered Signals**: Uses OpenRouter API (DeepSeek model) for primary signal generation
- **Multiple Strategies**: Momentum, Mean Reversion, Breakout, and Trend Following
- **Real-Time Data**: WebSocket connection for live market data
- **Risk Management**: Drawdown limits, daily loss limits, position sizing
- **Paper Trading**: Safe testing environment with simulated execution
- **Position Monitoring**: Automatic stop loss and take profit execution
- **Backtesting**: Complete backtesting framework with performance metrics
- **Trade Persistence**: Automatic trade history storage
- **Performance Analytics**: Comprehensive metrics and reporting

## 📋 Requirements

- Python 3.9+
- OpenRouter API Key (for AI signals)
- Binance Testnet API Keys (optional, for paper trading)

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r ai_trading_bot/requirements.txt
```

### Configuration

1. Set environment variables:
```bash
export OPENROUTER_API_KEY="your-openrouter-api-key"
export BINANCE_API_KEY="your-binance-api-key"  # Optional
export BINANCE_API_SECRET="your-binance-api-secret"  # Optional
```

2. Edit `ai_trading_bot/config/config.yaml` if needed

### Running the Bot

```bash
# Run main bot
python -m ai_trading_bot.main

# Or use alternative entry point
python -m ai_trading_bot.start
```

### Backtesting

```bash
# Run backtest
python -m ai_trading_bot.backtest --symbols BTCUSDT --days 30

# Download historical data
python -m ai_trading_bot.download_historical_data --symbols BTCUSDT --days 60
```

### Export Trades

```bash
# Export to CSV
python -m ai_trading_bot.export_trades --format csv

# Export to JSON
python -m ai_trading_bot.export_trades --format json --symbol BTCUSDT
```

## 📁 Project Structure

```
ai_trading_bot/
├── config/          # Configuration management
├── data/            # WebSocket client and data manager
├── features/        # Technical indicators
├── strategies/      # Trading strategies
├── allocator/       # Position allocation
├── risk/            # Risk management
├── execution/       # Order execution (paper trading)
├── backtesting/     # Backtesting framework
├── utils/           # Utilities (logging, OpenRouter, trade storage)
└── tests/           # Unit tests
```

## 🔧 Configuration

The bot uses `config/config.yaml` with environment variable support. Key parameters:

- **Initial Capital**: $10.00 (configurable)
- **Max Position Size**: 1% of capital per trade
- **Max Drawdown**: 5%
- **Max Daily Loss**: 2%
- **Max Daily Trades**: 100
- **Signal Generation**: Every 30 seconds
- **Position Monitoring**: Every 5 seconds

## 📊 Backtesting

Complete backtesting framework included:

- Historical data fetching
- Strategy simulation
- Performance metrics
- Trade analysis
- Export capabilities

See `ai_trading_bot/BACKTESTING.md` for detailed guide.

## 🚀 Deployment (Render.com)

Ready for deployment on Render.com:

1. Push code to GitHub
2. Create Background Worker on Render
3. Set environment variables
4. Deploy!

See `ai_trading_bot/DEPLOYMENT.md` for step-by-step guide.

## 📈 Trading Parameters

- **Trading Mode**: Paper trading (default)
- **Exchange**: Binance Testnet
- **Trading Type**: Spot trading
- **Fee Rate**: 0.1% per side
- **Slippage**: 0.1% (simulated)

## 🛡️ Safety Features

- Paper trading mode (default)
- Risk limits (drawdown, daily loss, position size)
- Automatic stop loss and take profit
- Graceful error handling
- Fail-open design (continues if AI unavailable)
- Trade persistence (survives restarts)

## 📝 Documentation

- `README.md` - This file
- `ai_trading_bot/README.md` - Detailed bot documentation
- `ai_trading_bot/BACKTESTING.md` - Backtesting guide
- `ai_trading_bot/DEPLOYMENT.md` - Deployment guide
- `ai_trading_bot/IMPROVEMENTS.md` - Recent improvements
- `ai_trading_bot/MISSING_FEATURES_REVIEW.md` - Feature review

## 🧪 Testing

```bash
# Run unit tests
python -m unittest discover ai_trading_bot/tests

# Run validation
python -m ai_trading_bot.validate_all
```

## 📦 Key Components

### Strategies
- **AI Signal Generator** (Primary) - OpenRouter/DeepSeek
- **Momentum Strategy** - Technical indicator based
- **Mean Reversion Strategy** - Z-score and Bollinger Bands
- **Breakout Strategy** - ATR and volatility
- **Trend Following Strategy** - Trend analysis
- **Meta AI Strategy** - Risk validation

### Risk Management
- Max drawdown protection
- Daily loss limits
- Position size limits
- Automatic stop loss/take profit
- Trade history tracking

### Data Management
- Real-time WebSocket data
- Historical data fetching
- Data validation and cleaning
- Trade persistence

## ⚠️ Disclaimer

This bot is for educational and testing purposes only. Trading cryptocurrencies involves risk. Always test thoroughly in paper trading mode before considering live trading.

## 📄 License

This project is provided as-is for educational purposes.

## 🤝 Support

For issues and questions:
1. Check documentation files
2. Review `MISSING_FEATURES_REVIEW.md` for known limitations
3. Check logs in `logs/` directory

---

**Status**: ✅ Production Ready
**Version**: 1.0.0
**Last Updated**: 2024

