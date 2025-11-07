# 🤖 Smart Trading Bot - Complete Guide

## 🎯 What is Smart Bot?

Smart Bot হল **fully automated, self-optimizing trading system** যা:
- ✅ নিজে নিজে setup করে
- ✅ Parameters automatically optimize করে
- ✅ Performance analyze করে
- ✅ নিজে নিজে improve করে
- ✅ Human-like intelligent trading করে

## 🚀 Quick Start

### Simplest Way (One Command):

```bash
python run_smart_bot.py
```

**That's it!** Bot automatically সব করে দেবে!

### Alternative Ways:

```bash
# Using smart commands
python -m ai_trading_bot.smart_commands start

# Using module directly
python -m ai_trading_bot --smart --capital 100 --mode balanced

# Using merged smart bot
python -m ai_trading_bot.smart_bot_merged --capital 100 --mode balanced
```

## 📋 Commands

### Setup Bot:
```bash
python -m ai_trading_bot.smart_commands setup --capital 100 --mode balanced
```

### Start Bot:
```bash
python -m ai_trading_bot.smart_commands start --capital 100 --mode balanced
```

### Check Status:
```bash
python -m ai_trading_bot.smart_commands status
```

### Optimize:
```bash
python -m ai_trading_bot.smart_commands optimize
```

## ⚙️ Trading Modes

- **`auto`** - Fully automatic (recommended for beginners)
- **`balanced`** - Balanced risk/reward (recommended)
- **`conservative`** - Lower risk, safer trades
- **`aggressive`** - Higher risk, more trades

## 🔧 How It Works

### 1. Auto-Setup Phase:
- Environment detection (API keys, exchange, platform)
- Capital-based configuration
- Mode-based risk settings
- Symbol selection based on capital

### 2. Optimization Phase:
- Backtesting on historical data
- Parameter optimization (stop loss, take profit)
- Strategy selection
- Best configuration selection

### 3. Trading Phase:
- Real-time market monitoring
- AI-powered signal generation
- Automatic trade execution
- Risk management

### 4. Self-Improvement Phase:
- Performance analysis (every 24 hours)
- Parameter adjustment based on results
- Strategy optimization
- Auto-reload with new settings

## 📊 Features

### ✅ Automatic Setup:
- No manual configuration needed
- Detects environment automatically
- Optimizes for your capital

### ✅ Self-Optimization:
- Backtesting-based optimization
- Real performance analysis
- Dynamic parameter adjustment

### ✅ Performance Tracking:
- Trade history storage
- Performance metrics calculation
- Strategy comparison
- Win rate tracking

### ✅ Intelligent Adaptation:
- Adapts to market conditions
- Improves based on results
- Adjusts risk parameters
- Optimizes strategies

## 🎯 Usage Examples

### Example 1: Start with $100
```bash
python run_smart_bot.py
# Bot auto-detects $10 from config, or you can specify:
python -m ai_trading_bot.smart_commands start --capital 100
```

### Example 2: Conservative Mode
```bash
python -m ai_trading_bot.smart_commands start --mode conservative --capital 50
```

### Example 3: Check Performance
```bash
python -m ai_trading_bot.smart_commands status
```

### Example 4: Re-optimize
```bash
python -m ai_trading_bot.smart_commands optimize
```

## 📁 File Structure

### Core Files:
- `auto_setup_part1.py` - Environment detection
- `auto_setup_part2.py` - Parameter optimization
- `auto_setup_part3.py` - Performance analysis
- `auto_setup_merged.py` - Complete AutoSetup class
- `auto_setup_performance.py` - Performance analyzer

### Bot Files:
- `smart_bot_part1.py` - Bot initialization
- `smart_bot_part2.py` - Auto-optimization loop
- `smart_bot_merged.py` - Complete SmartBot class

### Utilities:
- `smart_commands.py` - CLI commands
- `run_smart_bot.py` - Quick start script
- `__main__.py` - Module entry point

## 🔑 Required Setup

### Minimum:
```bash
export OPENROUTER_API_KEY="your-key"
```

### Complete:
```bash
export OPENROUTER_API_KEY="your-key"
export BYBIT_API_KEY="your-key"  # Optional
export BYBIT_API_SECRET="your-secret"  # Optional
```

## 📈 Performance Metrics

Bot automatically tracks:
- Total trades
- Win rate
- Total P&L
- Return percentage
- Sharpe ratio
- Max drawdown
- Strategy performance

## 🎉 That's It!

**Just run `python run_smart_bot.py` and let the bot do its magic!** 🪄

The bot will:
1. ✅ Setup automatically
2. ✅ Optimize parameters
3. ✅ Start trading
4. ✅ Improve itself over time

**No manual configuration needed!** 🤖

