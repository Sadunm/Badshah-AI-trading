# 💰 Render.com Free Options for Trading Bot

## ⚠️ Problem: Background Worker Requires Paid Plan

**Background Worker** = Minimum **$7/month (Starter plan)**

Free tier এ Background Worker নেই! 😔

---

## ✅ Solution Options:

### Option 1: Web Service (Free) - Workaround ✅

**Good News**: Web Service free tier এ আছে, এবং আপনি এটা bot হিসেবে run করতে পারেন!

#### Settings for Free Web Service:

**Service Type**: Web Service (Free tier available)

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

**Instance Type**: **Free** ($0/month)

**Auto-Deploy**: Enable

**Note**: Free tier may sleep after 15 minutes of inactivity, but will wake up on:
- New code push
- Manual wake-up
- Scheduled pings (if you add health check)

---

### Option 2: Keep-Alive Script (Free Web Service)

Free web service sleep এ যেতে পারে। Solution: একটি simple health check endpoint add করুন।

#### Create `ai_trading_bot/health.py`:

```python
"""
Health check endpoint for Render free tier.
Prevents service from sleeping.
"""
from flask import Flask
import threading
import time

app = Flask(__name__)

# Import and start bot in background
def start_bot():
    from ai_trading_bot.main import main
    main()

# Start bot in separate thread
bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()

@app.route('/')
def health():
    return {'status': 'ok', 'bot': 'running'}, 200

@app.route('/health')
def health_check():
    return {'status': 'healthy'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
```

#### Update Start Command:
```
gunicorn ai_trading_bot.health:app --bind 0.0.0.0:$PORT
```

**Problem**: এটা complex, এবং bot logic change করতে হবে।

---

### Option 3: Simple Web Service (Recommended for Free) ✅

**Best Free Solution**: Web Service হিসেবে deploy করুন, কিন্তু bot run করবে!

#### Settings:

**Service Type**: Web Service

**Root Directory**: `ai_trading_bot`

**Build Command**: 
```
pip install -r ai_trading_bot/requirements.txt
```

**Start Command**: 
```
python -m ai_trading_bot.main
```

**Instance Type**: **Free**

**Environment Variables**:
```
OPENROUTER_API_KEY=your_key
```

#### Important Notes:

1. ✅ **Bot will run** - Start command directly runs bot
2. ⚠️ **May sleep** - Free tier sleeps after 15 min inactivity
3. ✅ **Auto-wake** - Wakes on code push
4. ⚠️ **Not 24/7** - But works for testing

---

### Option 4: External Keep-Alive Service (Free)

Use external service to ping your Render service:

1. **UptimeRobot** (free) - Every 5 minutes ping
2. **Cron-Job.org** (free) - Scheduled pings
3. **GitHub Actions** (free) - Auto-ping

This keeps your free web service awake!

---

## 🎯 Recommended: Free Web Service

### Step-by-Step (Free):

1. **Service Type**: Web Service (not Background Worker)
2. **Name**: `Badshah-AI-trading`
3. **Root Directory**: `ai_trading_bot`
4. **Build**: `pip install -r ai_trading_bot/requirements.txt`
5. **Start**: `python -m ai_trading_bot.main`
6. **Instance**: **Free** ($0/month)
7. **Environment Variables**: Add `OPENROUTER_API_KEY`

### Limitations (Free Tier):

- ⚠️ Sleeps after 15 minutes inactivity
- ⚠️ Not true 24/7
- ✅ But works for testing
- ✅ Auto-wakes on code push

---

## 💡 Best Solution for Free:

**Use Web Service (Free)** + **External Keep-Alive**

1. Deploy as Web Service (Free)
2. Use UptimeRobot to ping every 5 minutes
3. Bot stays awake!

**UptimeRobot Setup**:
- URL: `https://your-service.onrender.com/health`
- Interval: 5 minutes
- Free forever!

---

## 📊 Comparison:

| Option | Cost | 24/7 | Complexity |
|--------|------|------|------------|
| Background Worker | $7/month | ✅ Yes | Easy |
| Web Service (Free) | $0 | ⚠️ May sleep | Easy |
| Web Service + Keep-Alive | $0 | ✅ Yes | Medium |

---

## 🚀 Quick Setup (Free):

1. Render → New Web Service
2. Repository: `Sadunm / Badshah-AI-trading`
3. Root: `ai_trading_bot`
4. Build: `pip install -r ai_trading_bot/requirements.txt`
5. Start: `python -m ai_trading_bot.main`
6. Instance: **Free**
7. Deploy!

**Then**: Setup UptimeRobot to keep it awake (optional)

---

**Free tier works!** Just use Web Service instead of Background Worker.

