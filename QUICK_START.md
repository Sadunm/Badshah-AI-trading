# 🚀 Quick Start Guide - Smart Trading Bot

## এক কথায় কি করতে হবে?

**শুধু এই command run করুন:**

```bash
python run_smart_bot.py
```

**That's it!** Bot automatically সব setup করে নেবে এবং trading শুরু করবে!

## 📋 What Happens Automatically?

1. ✅ **Environment Detection** - API keys, exchange, capital detect করে
2. ✅ **Auto-Configuration** - Optimal settings configure করে
3. ✅ **Parameter Optimization** - Backtesting করে best parameters find করে
4. ✅ **Strategy Selection** - Best strategies select করে
5. ✅ **Start Trading** - Automatic trading শুরু করে
6. ✅ **Self-Optimization** - Performance অনুযায়ী automatically optimize করে

## 🎯 Usage Options

### Option 1: Fully Automatic (Recommended)
```bash
python run_smart_bot.py
```
Everything auto-detected and configured!

### Option 2: Custom Capital
```bash
python -m ai_trading_bot.smart_bot_merged --capital 500 --mode balanced
```

### Option 3: Regular Bot (No Smart Features)
```bash
python -m ai_trading_bot.main
```

### Option 4: Smart Bot via Module
```bash
python -m ai_trading_bot --smart --capital 100 --mode balanced
```

## ⚙️ Trading Modes

- **`auto`** - Fully automatic (recommended)
- **`balanced`** - Balanced risk/reward
- **`conservative`** - Lower risk, safer trades
- **`aggressive`** - Higher risk, more trades

## 🔑 Required Setup

### Minimum (Just AI Bot):
```bash
export OPENROUTER_API_KEY="your-key-here"
```

### Complete (Best Experience):
```bash
export OPENROUTER_API_KEY="your-key-here"
export BYBIT_API_KEY="your-key-here"  # Optional
export BYBIT_API_SECRET="your-secret-here"  # Optional
```

## 📊 What the Bot Does

- **Monitors** multiple cryptocurrencies
- **Analyzes** market conditions with AI
- **Generates** trading signals
- **Executes** trades automatically
- **Manages** risk with stop loss/take profit
- **Optimizes** itself based on performance

## 🛑 Stopping the Bot

Press `Ctrl+C` to stop gracefully.

## 🎉 That's It!

Just run `python run_smart_bot.py` and let the bot do its magic! 🪄

