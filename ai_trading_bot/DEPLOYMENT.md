# 🚀 Deployment Guide - Render.com

## ✅ Complete Setup for Render.com Paper Trading Deployment

### Prerequisites
- GitHub repository with code
- Render.com account
- OpenRouter API key (for AI features)
- Binance Testnet API keys (optional, for paper trading)

## 📋 Step-by-Step Deployment

### 1. **Prepare Repository**
Ensure your repository structure:
```
BADSHAI AI TRADING MACHINE/
├── ai_trading_bot/
│   ├── __init__.py
│   ├── main.py
│   ├── start.py
│   ├── requirements.txt
│   ├── Procfile
│   ├── runtime.txt
│   ├── render.yaml
│   ├── config/
│   │   └── config.yaml
│   └── ... (all other modules)
```

### 2. **Create Render Service**

1. Go to [Render.com Dashboard](https://dashboard.render.com)
2. Click "New +" → "Background Worker"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `ai-trading-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r ai_trading_bot/requirements.txt`
   - **Start Command**: `python -m ai_trading_bot.main`

### 3. **Set Environment Variables**

In Render dashboard, go to your service → Environment tab:

**Required:**
```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

**Optional (for paper trading):**
```
BINANCE_API_KEY=your_binance_testnet_key
BINANCE_API_SECRET=your_binance_testnet_secret
```

### 4. **Deployment Files**

#### `Procfile` (already configured)
```
worker: python -m ai_trading_bot.main
```

#### `render.yaml` (already configured)
```yaml
services:
  - type: worker
    name: ai-trading-bot
    env: python
    buildCommand: pip install -r ai_trading_bot/requirements.txt
    startCommand: python -m ai_trading_bot.main
    envVars:
      - key: OPENROUTER_API_KEY
        sync: false
      - key: BINANCE_API_KEY
        sync: false
      - key: BINANCE_API_SECRET
        sync: false
```

#### `runtime.txt` (already configured)
```
python-3.11.0
```

### 5. **Deploy**

1. Click "Create Background Worker"
2. Render will:
   - Clone your repository
   - Install dependencies
   - Start the bot
3. Monitor logs in Render dashboard

## 🔍 Verification

### Check Logs
After deployment, check logs:
1. Go to your service in Render dashboard
2. Click "Logs" tab
3. Look for:
   - ✅ "Configuration loaded"
   - ✅ "All components initialized"
   - ✅ "WebSocket connected"
   - ✅ "Trading bot started"

### Expected Behavior
- Bot connects to Binance Testnet WebSocket
- Fetches historical data
- Starts generating signals every 30 seconds
- Monitors positions every 5 seconds
- Logs all activities

## 🐛 Troubleshooting

### Issue: "Module not found"
**Solution**: Ensure `ai_trading_bot` directory is in repository root

### Issue: "Config file not found"
**Solution**: Check that `config/config.yaml` exists in `ai_trading_bot/` directory

### Issue: "OPENROUTER_API_KEY not set"
**Solution**: Set environment variable in Render dashboard

### Issue: "WebSocket connection failed"
**Solution**: 
- Check Binance Testnet is accessible
- Verify network connectivity
- Check logs for specific error

### Issue: "Import errors"
**Solution**: 
- Verify all `__init__.py` files exist
- Check `requirements.txt` has all dependencies
- Ensure Python 3.9+ is used

## 📊 Monitoring

### Logs to Watch
- **INFO**: Normal operations
- **WARNING**: Non-critical issues (e.g., AI unavailable, fallback to rule-based)
- **ERROR**: Critical issues requiring attention

### Key Metrics
- Capital tracking
- Number of trades
- P&L
- Drawdown percentage
- Daily trades count

## 🔄 Updates

To update deployment:
1. Push changes to GitHub
2. Render auto-deploys (or manually trigger)
3. Monitor logs for successful deployment

## ⚠️ Important Notes

1. **Paper Trading**: Bot runs in paper trading mode by default
2. **Costs**: OpenRouter API calls cost money - monitor usage
3. **Rate Limits**: Bot has built-in rate limiting (10 req/min)
4. **Uptime**: Render free tier has limitations - consider paid plan for 24/7
5. **Logs**: Logs are available in Render dashboard (free tier: 7 days retention)

## 🎯 Success Indicators

✅ Bot is running if you see:
- Regular status logs every 30 seconds
- Signal generation attempts
- Position monitoring logs
- No critical errors

## 📞 Support

If issues persist:
1. Check Render logs
2. Verify all environment variables
3. Test locally first
4. Review `DEPLOYMENT.md` and `README.md`

---

**Status**: ✅ Ready for Render.com Deployment
**Paper Trading**: ✅ Enabled by default
**Production Ready**: ✅ All bugs fixed

