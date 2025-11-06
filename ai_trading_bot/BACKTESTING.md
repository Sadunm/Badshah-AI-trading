# 📊 Backtesting Guide

## ✅ Complete Backtesting Setup

### Overview
The AI Trading Bot includes a comprehensive backtesting framework that allows you to test strategies on historical data before deploying to live/paper trading.

## 🚀 Quick Start

### Basic Usage

```bash
# Run backtest with default settings (30 days, symbols from config)
python -m ai_trading_bot.backtest

# Run backtest for specific symbols
python -m ai_trading_bot.backtest --symbols BTCUSDT ETHUSDT

# Run backtest for 60 days
python -m ai_trading_bot.backtest --days 60

# Save results to file
python -m ai_trading_bot.backtest --output results.json
```

### Advanced Usage

```bash
# Full options
python -m ai_trading_bot.backtest \
    --symbols BTCUSDT ETHUSDT BNBUSDT \
    --days 90 \
    --output backtest_results.json
```

## 📋 Features

### ✅ What's Included
- Historical data fetching from Binance
- Full strategy simulation (AI + rule-based)
- Position tracking and P&L calculation
- Risk management enforcement
- Performance metrics calculation
- Equity curve generation

### 📊 Metrics Calculated
- **Total Trades**: Number of completed trades
- **Win Rate**: Percentage of profitable trades
- **Total P&L**: Net profit/loss
- **Total Return**: Percentage return on capital
- **Max Drawdown**: Maximum peak-to-trough decline
- **Sharpe Ratio**: Risk-adjusted return measure

## 🔧 How It Works

### 1. Data Fetching
- Fetches historical candle data from Binance
- Supports date range filtering
- Validates and cleans data

### 2. Strategy Simulation
- Processes candles chronologically
- Calculates technical indicators
- Generates trading signals (AI + fallback)
- Executes trades with risk management

### 3. Position Management
- Opens positions based on signals
- Monitors stop loss/take profit
- Closes positions automatically
- Tracks all trades

### 4. Performance Analysis
- Calculates comprehensive metrics
- Generates equity curve
- Provides detailed trade history

## 📁 Output Format

Results are saved as JSON with:

```json
{
  "BTCUSDT": {
    "trades": [...],
    "equity_curve": [...],
    "metrics": {
      "total_trades": 25,
      "winning_trades": 15,
      "losing_trades": 10,
      "win_rate": 60.0,
      "total_pnl": 5.23,
      "total_return": 52.3,
      "max_drawdown": 3.2,
      "sharpe_ratio": 1.45,
      "initial_capital": 10.0,
      "final_capital": 15.23
    }
  }
}
```

## 🎯 Best Practices

### 1. **Test Multiple Time Periods**
```bash
# Test different market conditions
python -m ai_trading_bot.backtest --days 30   # Recent
python -m ai_trading_bot.backtest --days 90   # Medium
python -m ai_trading_bot.backtest --days 180  # Long term
```

### 2. **Test Multiple Symbols**
```bash
# Test diversification
python -m ai_trading_bot.backtest --symbols BTCUSDT ETHUSDT BNBUSDT SOLUSDT
```

### 3. **Save Results**
```bash
# Always save results for analysis
python -m ai_trading_bot.backtest --output results_$(date +%Y%m%d).json
```

### 4. **Compare Strategies**
- Run backtest with different configs
- Compare results
- Optimize parameters

## 🔍 Interpreting Results

### Good Performance Indicators
- ✅ Win rate > 50%
- ✅ Positive total return
- ✅ Sharpe ratio > 1.0
- ✅ Max drawdown < 10%
- ✅ Consistent equity curve growth

### Warning Signs
- ⚠️ Win rate < 40%
- ⚠️ Negative total return
- ⚠️ Max drawdown > 20%
- ⚠️ Erratic equity curve
- ⚠️ Too few trades (overfitting risk)

## 🛠️ Customization

### Modify Backtest Period
Edit `backtest.py`:
```python
run_backtest(days=60)  # Change days
```

### Adjust Risk Parameters
Edit `config/config.yaml`:
```yaml
risk:
  max_drawdown_pct: 5.0
  max_daily_loss_pct: 2.0
  max_daily_trades: 100
```

### Test Different Strategies
Edit `config/config.yaml`:
```yaml
strategies:
  momentum:
    enabled: true
  mean_reversion:
    enabled: false  # Disable strategy
```

## 📊 Example Output

```
Running backtest for BTCUSDT
============================================================
Fetching 30 days of historical data...
✅ BTCUSDT: 8640 candles

📊 Backtest Results for BTCUSDT:
  Total Trades: 25
  Winning Trades: 15
  Losing Trades: 10
  Win Rate: 60.00%
  Total P&L: $5.23
  Total Return: 52.30%
  Max Drawdown: 3.20%
  Sharpe Ratio: 1.45
  Initial Capital: $10.00
  Final Capital: $15.23

💾 Results saved to: backtest_results.json
```

## ⚠️ Limitations

1. **No Slippage Modeling**: Uses exact prices (can be added)
2. **No Order Book**: Uses close prices only
3. **No Partial Fills**: All-or-nothing execution
4. **Historical Data Only**: Past performance ≠ future results

## 🚀 Next Steps

After backtesting:
1. Analyze results
2. Adjust parameters if needed
3. Test on paper trading
4. Deploy to Render.com

---

**Status**: ✅ Backtesting Framework Complete
**Ready**: ✅ Test your strategies before live trading!

