# 🔐 Render.com Environment Variables Guide

## 📋 Required Environment Variables

### ✅ MUST HAVE (Required)

#### 1. OPENROUTER_API_KEY
**Purpose**: AI signal generation এর জন্য

**Value**: আপনার OpenRouter API key

**How to get**:
1. https://openrouter.ai/keys এ যান
2. Account create করুন (free)
3. API key generate করুন
4. Copy করুন

**Example**:
```
OPENROUTER_API_KEY=sk-or-v1-abc123xyz789...
```

**Without this**: Bot AI signals generate করতে পারবে না, শুধু rule-based strategies কাজ করবে

---

### ⚠️ OPTIONAL (But Recommended)

#### 2. BINANCE_API_KEY
**Purpose**: Binance Testnet API access (optional for paper trading)

**Value**: Binance Testnet API key

**How to get**:
1. https://testnet.binance.vision/ এ যান
2. API Management → Create API Key
3. Testnet key generate করুন

**Example**:
```
BINANCE_API_KEY=testnet_api_key_12345
```

**Note**: Paper trading এর জন্য optional, কিন্তু better data access এর জন্য recommended

---

#### 3. BINANCE_API_SECRET
**Purpose**: Binance Testnet API secret (optional)

**Value**: Binance Testnet API secret

**Example**:
```
BINANCE_API_SECRET=testnet_secret_67890
```

**Note**: API key এর সাথে pair করতে হবে

---

## 🎯 Minimum Setup (Just AI Bot)

**শুধু 1 টা variable লাগে**:

```
OPENROUTER_API_KEY = your_openrouter_key_here
```

এটাই enough! Bot run হবে, AI signals generate করবে।

---

## 📝 Complete Setup (Recommended)

**3 টা variables** (best experience):

```
OPENROUTER_API_KEY = sk-or-v1-...
BINANCE_API_KEY = testnet_key_...
BINANCE_API_SECRET = testnet_secret_...
```

---

## 🔧 Render.com এ Add করতে:

### Step-by-Step:

1. **Render Dashboard** → আপনার service → **Environment** tab
2. **"Add Environment Variable"** click করুন
3. **Name** field এ variable name দিন (e.g., `OPENROUTER_API_KEY`)
4. **Value** field এ actual value দিন
5. **Save** করুন
6. Repeat করুন সব variables এর জন্য

### Example:

| Name | Value |
|------|-------|
| `OPENROUTER_API_KEY` | `sk-or-v1-abc123...` |
| `BINANCE_API_KEY` | `testnet_key_123` |
| `BINANCE_API_SECRET` | `testnet_secret_456` |

---

## ⚠️ Security Notes:

1. ✅ **Never commit** API keys to GitHub
2. ✅ **Use Environment Variables** - Render এ set করুন
3. ✅ **.gitignore** already configured - keys protected
4. ✅ **Testnet keys** - Safe to use (not real money)

---

## 🧪 Test করতে:

### Check if variables are set:

Bot start হলে logs এ দেখবেন:
- ✅ "Configuration loaded"
- ✅ "OPENROUTER_API_KEY set" (or warning if not set)
- ✅ "All components initialized"

### If OPENROUTER_API_KEY missing:

Logs এ দেখবেন:
- ⚠️ "OPENROUTER_API_KEY not set - AI features will be disabled"
- Bot run হবে, কিন্তু AI signals generate হবে না
- Rule-based strategies কাজ করবে

---

## 📋 Quick Checklist:

### Minimum (Bot run হবে):
- [ ] `OPENROUTER_API_KEY` ✅

### Recommended (Best experience):
- [ ] `OPENROUTER_API_KEY` ✅
- [ ] `BINANCE_API_KEY` (optional)
- [ ] `BINANCE_API_SECRET` (optional)

---

## 💡 Pro Tips:

1. **OpenRouter Key**: Free tier আছে, test করার জন্য enough
2. **Binance Keys**: Testnet keys free, unlimited
3. **Security**: সব keys Render environment variables এ রাখুন
4. **Testing**: Local এ `.env` file use করতে পারেন

---

## 🚀 After Adding Variables:

1. **Save** all variables
2. **Redeploy** service (auto-deploy হবে)
3. **Check logs** - verify variables loaded
4. **Monitor** - bot should start successfully

---

**Summary**: 
- **Minimum**: শুধু `OPENROUTER_API_KEY` 
- **Recommended**: সব 3 টা variables

