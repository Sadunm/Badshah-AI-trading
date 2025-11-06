# 🔑 Bybit API Setup Guide

## ✅ কি কি দিতে হবে:

### 1. **Bybit API Key** (Required)
- Bybit website থেকে API Key তৈরি করুন
- Name: `badshah` (বা যেকোনো নাম)

### 2. **Bybit API Secret** (Required)
- API Key তৈরি করার সময় Secret Key পাবেন
- **⚠️ Important**: Secret Key শুধু একবার দেখানো হবে, save করে রাখুন!

### 3. **API Permissions** (Required)
Bybit API Key তৈরি করার সময় এই permissions select করুন:

**Trade Permissions:**
- ✅ **Contract > Orders** (checked)
  - Description: "Query order info; submit, modify or cancel orders (Derivatives)"
- ✅ **Contract > Positions** (checked)
  - Description: "Query positions info; modify margin balance, leverage and more (Derivatives)"
- ✅ **SPOT > Trade** (checked)
  - Description: "Query order info; submit or cancel orders (Spot)"

**Assets Permissions:**
- ⚠️ **Wallet > Account Transfer** (optional - যদি fund transfer করতে চান)
- ⚠️ **Wallet > Subaccount Transfer** (optional - যদি subaccount ব্যবহার করেন)

### 4. **IP Restriction** (Optional but Recommended)
- **Option 1**: "No IP restriction" (সহজ, কিন্তু কম secure)
  - ⚠️ Warning: API Key 3 মাস পর expire হবে
  - ⚠️ Account risk বাড়বে
  
- **Option 2**: "Only IPs with permissions granted" (Recommended)
  - Render server-এর IP address whitelist করুন
  - Render dashboard থেকে IP address জানতে পারবেন
  - Format: `192.168.1.1,192.168.1.2` (comma separated, max 100 IPs)

---

## 📝 Render Environment Variables

Render dashboard-এ এই environment variables add করুন:

```
BYBIT_API_KEY=your_api_key_here
BYBIT_API_SECRET=your_api_secret_here
```

---

## 🔧 API Key তৈরি করার Steps:

1. Bybit website-এ login করুন
2. Go to: **API Management** > **Create New Key**
3. Fill the form:
   - **Name**: `badshah` (বা আপনার পছন্দের নাম)
   - **API Key Permissions**: `Read-Write`
   - **Trade Permissions**: 
     - ✅ Contract > Orders
     - ✅ Contract > Positions
     - ✅ SPOT > Trade
   - **IP Restriction**: 
     - "No IP restriction" (সহজ)
     - অথবা Render server IP whitelist করুন
4. Click **Submit**
5. **Copy API Key এবং Secret Key** (Secret Key শুধু একবার দেখানো হবে!)

---

## ⚠️ Security Tips:

1. ✅ **Never share** API Key/Secret
2. ✅ **IP Restriction** enable করুন (যদি possible হয়)
3. ✅ **Read-Write** permission শুধু trading bot-এর জন্য
4. ✅ **Withdrawal permission** disable রাখুন (security-এর জন্য)
5. ✅ API Key **regularly rotate** করুন

---

## 📊 Bybit API Endpoints:

- **WebSocket Public**: `wss://stream.bybit.com/v5/public/spot`
- **REST API**: `https://api.bybit.com`
- **Rate Limit**: 600 requests per 5 seconds per IP

---

## ✅ Ready?

API Key এবং Secret Key পেয়ে গেলে, Render-এ environment variables set করুন এবং bot automatically Bybit-এ connect করবে!

