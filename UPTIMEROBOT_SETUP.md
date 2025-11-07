# 🔔 UptimeRobot Setup Guide

## 📋 URL to Monitor

### ✅ Recommended: Health Check Endpoint

**URL to monitor:**
```
https://badshah-ai-trading.onrender.com/health
```

**Why this endpoint?**
- ✅ Specifically designed for health checks
- ✅ Returns `{"status": "healthy", "bot": "running"}`
- ✅ Lightweight and fast
- ✅ Perfect for uptime monitoring

---

### Alternative Options:

#### Option 1: Status Endpoint (More Detailed)
```
https://badshah-ai-trading.onrender.com/status
```

**Returns:**
```json
{
  "status": "ok",
  "bot_running": true,
  "service": "trading_bot",
  "error": null
}
```

#### Option 2: Root Endpoint (Simple)
```
https://badshah-ai-trading.onrender.com/
```

**Returns:**
```json
{
  "status": "ok",
  "bot": "running",
  "service": "Badshah AI Trading Bot"
}
```

---

## 🎯 UptimeRobot Configuration

### Step-by-Step:

1. **Monitor Type**: HTTP(S) monitoring ✅ (already selected)

2. **URL to monitor**: 
   ```
   https://badshah-ai-trading.onrender.com/health
   ```

3. **Monitoring Interval**: 
   - Free: 5 minutes (default)
   - Paid: 1 minute (optional)

4. **Alert Contacts**: 
   - Add your email
   - Or phone number for SMS

5. **Click "Create monitor"**

---

## ✅ Expected Response

When monitoring `/health` endpoint:

**Success (200 OK):**
```json
{
  "status": "healthy",
  "bot": "running"
}
```

**If bot is starting:**
```json
{
  "status": "healthy",
  "bot": "starting"
}
```

**If error:**
```json
{
  "status": "healthy",
  "bot": "starting",
  "error": "error message"
}
```

---

## 🔍 Why Use Health Endpoint?

1. **Keeps Service Awake**: 
   - Free tier sleeps after 15 min inactivity
   - UptimeRobot pings every 5 min = service stays awake! ✅

2. **Monitors Bot Status**: 
   - Not just web server, but actual bot status
   - Knows if bot is running or has errors

3. **Lightweight**: 
   - Fast response
   - Doesn't load the service

---

## 📊 Monitoring Best Practices

### Recommended Settings:

- **Monitor Type**: HTTP(S)
- **URL**: `https://badshah-ai-trading.onrender.com/health`
- **Interval**: 5 minutes (free) or 1 minute (paid)
- **Alert When**: 
  - Service is down
  - Response time > 5 seconds
  - HTTP status != 200

---

## 🎯 Quick Copy-Paste

**For UptimeRobot "URL to monitor" field:**

```
https://badshah-ai-trading.onrender.com/health
```

**That's it!** Just paste this URL and create the monitor.

---

## ✅ Summary

**Best URL for monitoring:**
```
https://badshah-ai-trading.onrender.com/health
```

This will:
- ✅ Keep your free Render service awake
- ✅ Monitor bot health status
- ✅ Alert you if service goes down
- ✅ Work perfectly with UptimeRobot

---

**Ready to monitor!** 🚀

