# 🚀 Render.com Deployment Settings

## ⚠️ IMPORTANT: Service Type

**এই bot টা Web Service নয় - এটা Background Worker হওয়া উচিত!**

### Option 1: Background Worker (Recommended) ✅

1. **Service Type**: **Background Worker** (Web Service নয়!)
2. **Name**: `Badshah-AI-trading`
3. **Source Code**: `Sadunm / Badshah-AI-trading`
4. **Branch**: `main`
5. **Region**: Singapore (or your choice)

### Settings:

**Root Directory**: `ai_trading_bot`

**Build Command**: 
```
pip install -r ai_trading_bot/requirements.txt
```

**Start Command**: 
```
python -m ai_trading_bot.main
```

**Instance Type**: 
- **Minimum**: Starter ($7/month) - 24/7 operation এর জন্য
- **Free tier**: Works but may sleep after inactivity

**Environment Variables** (Add these):
```
OPENROUTER_API_KEY = your_openrouter_api_key_here
BINANCE_API_KEY = your_binance_testnet_key (optional)
BINANCE_API_SECRET = your_binance_testnet_secret (optional)
```

---

## Option 2: Web Service (If you must use Web Service)

**Note**: Trading bot continuous run করবে, web service হিসেবে configure করতে পারেন:

**Root Directory**: `ai_trading_bot`

**Build Command**: 
```
pip install -r ai_trading_bot/requirements.txt
```

**Start Command**: 
```
python -m ai_trading_bot.main
```

**Instance Type**: Starter ($7/month) minimum

**Environment Variables**: Same as above

---

## 📋 Step-by-Step Instructions

### 1. Create Background Worker

1. Render Dashboard → **New +** → **Background Worker**
2. Connect repository: `Sadunm / Badshah-AI-trading`
3. Branch: `main`

### 2. Configure Settings

**Name**: `Badshah-AI-trading`

**Root Directory**: 
```
ai_trading_bot
```

**Build Command**: 
```
pip install -r ai_trading_bot/requirements.txt
```

**Start Command**: 
```
python -m ai_trading_bot.main
```

**Instance Type**: 
- **Starter** ($7/month) - Recommended for 24/7
- **Free** - Works but may sleep

### 3. Environment Variables

Click **"Add Environment Variable"** and add:

| Name | Value |
|------|-------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key |
| `BINANCE_API_KEY` | Your Binance testnet key (optional) |
| `BINANCE_API_SECRET` | Your Binance testnet secret (optional) |

### 4. Deploy

Click **"Create Background Worker"**

---

## 🔍 Verification

After deployment, check logs:
1. Go to your service
2. Click **"Logs"** tab
3. Look for:
   - ✅ "Configuration loaded"
   - ✅ "All components initialized"
   - ✅ "WebSocket connected"
   - ✅ "Trading bot started"

---

## ⚙️ Runtime Environment Details

**Language**: Python 3

**Python Version**: 3.11.0 (specified in `runtime.txt`)

**Working Directory**: `ai_trading_bot/`

**Dependencies**: Auto-installed from `requirements.txt`

---

## 💰 Cost Estimate

- **Free Tier**: $0/month (may sleep after inactivity)
- **Starter**: $7/month (24/7 operation, recommended)
- **Standard**: $25/month (more resources)

For trading bot, **Starter ($7/month)** is recommended.

---

## 🎯 Quick Copy-Paste Settings

### Root Directory:
```
ai_trading_bot
```

### Build Command:
```
pip install -r ai_trading_bot/requirements.txt
```

### Start Command:
```
python -m ai_trading_bot.main
```

### Environment Variables:
```
OPENROUTER_API_KEY=your_key_here
```

---

**Ready to deploy!** Use Background Worker (not Web Service) for best results.

