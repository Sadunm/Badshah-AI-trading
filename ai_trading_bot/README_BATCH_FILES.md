# Batch Files Guide (Windows)

এই ফোল্ডারে বেশ কিছু batch files আছে যা Windows এ bot run করতে সাহায্য করবে।

## Batch Files List

### 1. `QUICK_START.bat` ⭐ (Recommended)
সবকিছু setup করার জন্য সবচেয়ে সহজ way:
- Dependencies install করবে
- Environment variables setup করতে সাহায্য করবে
- Import test করবে
- সব setup complete হলে notify করবে

### 2. `install.bat`
সব dependencies install করার জন্য:
- Python version check
- pip upgrade
- requirements.txt থেকে সব packages install

### 3. `setup_env.bat`
Environment variables set করার জন্য:
- OPENROUTER_API_KEY (required)
- BINANCE_API_KEY (optional)
- BINANCE_API_SECRET (optional)

### 4. `run_bot.bat` ⭐
Bot run করার জন্য main script:
- Python এবং dependencies check
- PYTHONPATH set
- Bot start করে

### 5. `run_bot_start.bat`
Alternative entry point ব্যবহার করে bot run করার জন্য

### 6. `test_imports.bat`
সব modules import হচ্ছে কিনা check করার জন্য

### 7. `check_system.bat`
System check করার জন্য:
- Python installation
- Dependencies
- Environment variables
- File structure

### 8. `test_production_ready.bat` ⭐⭐
Production ready কিনা comprehensive test করার জন্য:
- সব imports test
- Config loading test
- Indicator calculations test
- Risk manager test
- Position allocator test
- Logger test

## Quick Start Steps

1. **First Time Setup:**
   ```
   QUICK_START.bat
   ```
   এটা সবকিছু setup করবে।

2. **Environment Variables Set (if not done):**
   ```
   setup_env.bat
   ```

3. **System Check:**
   ```
   check_system.bat
   ```

4. **Production Readiness Test:**
   ```
   test_production_ready.bat
   ```

5. **Run Bot:**
   ```
   run_bot.bat
   ```

## Troubleshooting

### Path Errors
যদি path errors আসে:
1. `check_system.bat` run করুন
2. `test_imports.bat` run করুন
3. Ensure যে আপনি `ai_trading_bot` folder এর মধ্যে আছেন

### Import Errors
যদি import errors আসে:
1. `install.bat` run করুন
2. `test_imports.bat` run করুন
3. Check করুন যে Python version 3.9+ আছে

### Config Not Found
যদি config file না পায়:
- Ensure `config/config.yaml` file exists
- Check current directory

### Module Not Found
যদি module not found error আসে:
- `run_bot.bat` ব্যবহার করুন (এটা PYTHONPATH set করে)
- বা manually PYTHONPATH set করুন

## Notes

- সব batch files double-click করে run করা যায়
- Batch files automatically working directory set করে
- Error হলে error messages দেখাবে

