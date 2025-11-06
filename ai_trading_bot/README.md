# AI Trading Bot

Complete production-ready AI trading bot with multi-strategy support, real-time market data, and risk management.

## Features

- **AI-Powered Signals**: Uses OpenRouter API (DeepSeek model) for primary signal generation
- **Multiple Strategies**: Momentum, Mean Reversion, Breakout, and Trend Following
- **Real-Time Data**: WebSocket connection for live market data
- **Risk Management**: Drawdown limits, daily loss limits, position sizing
- **Paper Trading**: Safe testing environment with simulated execution
- **Position Monitoring**: Automatic stop loss and take profit execution

## Requirements

- Python 3.9+
- OpenRouter API Key (for AI signals)
- Binance Testnet API Keys (optional, for paper trading)

## Installation

1. Clone or download this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy and edit `config/config.yaml` if needed
2. Set environment variables:
```bash
export OPENROUTER_API_KEY="your-openrouter-api-key"
export BINANCE_API_KEY="your-binance-api-key"  # Optional
export BINANCE_API_SECRET="your-binance-api-secret"  # Optional
```

## Running the Bot

### Basic Usage
```bash
python -m ai_trading_bot.main
```

### Alternative Entry Point
```bash
python -m ai_trading_bot.start
```

## Configuration File

The bot uses `config/config.yaml` with environment variable support. Variables can be substituted using `${VAR_NAME}` syntax.

## Trading Parameters

- **Initial Capital**: $10.00 (configurable)
- **Max Position Size**: 1% of capital per trade
- **Max Drawdown**: 5%
- **Max Daily Loss**: 2%
- **Max Daily Trades**: 100
- **Signal Generation**: Every 30 seconds
- **Position Monitoring**: Every 5 seconds

## Deployment (Render.com)

1. Create a new Web Service on Render
2. Connect your repository
3. Set environment variables:
   - `OPENROUTER_API_KEY`
   - `BINANCE_API_KEY` (optional)
   - `BINANCE_API_SECRET` (optional)
4. Deploy using the provided `Procfile` and `render.yaml`

## Architecture

```
ai_trading_bot/
├── config/          # Configuration management
├── data/            # WebSocket client and data manager
├── features/        # Technical indicators
├── strategies/      # Trading strategies
├── allocator/       # Position allocation
├── risk/            # Risk management
├── execution/       # Order execution (paper trading)
└── utils/           # Utilities (logging, OpenRouter client)
```

## Logging

Logs are written to:
- Console (always)
- `logs/trading_bot.log` (if writable)

Logs rotate automatically (10MB, 3 backups).

## Safety Features

- Paper trading mode (default)
- Risk limits (drawdown, daily loss, position size)
- Automatic stop loss and take profit
- Graceful error handling
- Fail-open design (continues if AI unavailable)

## Disclaimer

This bot is for educational and testing purposes only. Trading cryptocurrencies involves risk. Always test thoroughly in paper trading mode before considering live trading.

