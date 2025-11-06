# 🔧 Render Build Fix - Python Version Issue

## ❌ Problem

Build failing because:
- Python 3.13.4 being used (too new)
- NumPy compilation failing
- runtime.txt not being read correctly

## ✅ Solution

### 1. Root Directory Issue

Render needs `runtime.txt` in **project root**, not in `ai_trading_bot/` folder.

**Fixed**: Created `runtime.txt` in root directory.

### 2. Updated Settings

**Root Directory**: `ai_trading_bot` (keep this)

**Build Command**: 
```
pip install -r ai_trading_bot/requirements.txt
```

**Start Command**: 
```
gunicorn ai_trading_bot.health:app --bind 0.0.0.0:$PORT
```

**Python Version**: Will use 3.11.0 from `runtime.txt` in root

---

## 🔄 Update Your Render Service

### Option 1: Manual Update

1. Go to your Render service settings
2. **Build Command**: `pip install -r ai_trading_bot/requirements.txt`
3. **Start Command**: `gunicorn ai_trading_bot.health:app --bind 0.0.0.0:$PORT`
4. **Root Directory**: `ai_trading_bot`
5. **Manual Deploy** → Deploy latest commit

### Option 2: Re-deploy

1. Push latest code (already done)
2. Render → **Manual Deploy** → **Deploy latest commit**
3. Should use Python 3.11.0 now

---

## 📋 Correct Settings Summary

**Service Type**: Web Service

**Root Directory**: `ai_trading_bot`

**Build Command**: 
```
pip install -r ai_trading_bot/requirements.txt
```

**Start Command**: 
```
gunicorn ai_trading_bot.health:app --bind 0.0.0.0:$PORT
```

**Instance Type**: Free

**Environment Variables**:
```
OPENROUTER_API_KEY = your_key
PORT = 10000
```

---

## ✅ What's Fixed

1. ✅ `runtime.txt` in root directory (Python 3.11.0)
2. ✅ Build command path correct
3. ✅ Start command with gunicorn
4. ✅ All dependencies in requirements.txt

---

**After update, build should succeed!** 🚀

