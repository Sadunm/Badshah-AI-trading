# 🤖 Smart Bot - Merge Instructions

## 📋 Overview

Smart Bot system কে parts-এ ভাগ করা হয়েছে timeout avoid করার জন্য। এই file guide দেবে কিভাবে merge করতে হবে।

## 📁 File Structure

### Auto-Setup Parts:
- `auto_setup_part1.py` - Environment detection and configuration
- `auto_setup_part2.py` - Parameter optimization
- `auto_setup_part3.py` - Performance analysis and adaptation
- `auto_setup_merged.py` - Complete merged AutoSetup class

### Smart Bot Parts:
- `smart_bot_part1.py` - Bot initialization and startup
- `smart_bot_part2.py` - Auto-optimization background thread
- `smart_bot_merged.py` - Complete merged SmartTradingBot class

## 🔄 Merge Instructions

### Option 1: Use Merged Files (Recommended)

যদি merged files use করতে চান, তাহলে:

1. **Auto-Setup use করতে:**
   ```python
   from ai_trading_bot.auto_setup_merged import AutoSetup, setup_bot
   ```

2. **Smart Bot use করতে:**
   ```python
   from ai_trading_bot.smart_bot_merged import SmartTradingBot
   ```

### Option 2: Merge into Single Files

যদি single files এ merge করতে চান:

#### Step 1: Merge auto_setup.py

`auto_setup.py` file এ সব parts combine করুন:

```python
# auto_setup.py structure:
# 1. Import all parts
from .auto_setup_part1 import AutoSetupPart1
from .auto_setup_part2 import AutoSetupPart2
from .auto_setup_part3 import AutoSetupPart3

# 2. Copy AutoSetup class from auto_setup_merged.py
# 3. Copy setup_bot function
```

#### Step 2: Merge smart_bot.py

`smart_bot.py` file এ সব parts combine করুন:

```python
# smart_bot.py structure:
# 1. Import all parts
from .smart_bot_part1 import SmartTradingBotPart1
from .smart_bot_part2 import SmartTradingBotPart2

# 2. Copy SmartTradingBot class from smart_bot_merged.py
# 3. Copy main() function
```

## ✅ Quick Start

### Using Merged Files:

```python
# Start smart bot
from ai_trading_bot.smart_bot_merged import SmartTradingBot

bot = SmartTradingBot(capital=100, mode="balanced")
bot.start()
```

### Or use auto-setup only:

```python
from ai_trading_bot.auto_setup_merged import setup_bot

# Auto-setup and configure
config = setup_bot(capital=100, mode="balanced")
```

## 📝 Notes

1. **Parts are independent** - Each part can work standalone
2. **Merged files use parts** - Merged files import and use the parts
3. **No code duplication** - Parts are reusable
4. **Easy to maintain** - Each part has single responsibility

## 🎯 Usage Example

```bash
# Run smart bot
python -m ai_trading_bot.smart_bot_merged --capital 100 --mode balanced

# Or import and use
python -c "from ai_trading_bot.smart_bot_merged import SmartTradingBot; SmartTradingBot(capital=100).start()"
```

## 🔧 If You Want to Merge Everything

1. Copy content from `auto_setup_part1.py` → `auto_setup.py`
2. Copy content from `auto_setup_part2.py` → Append to `auto_setup.py`
3. Copy content from `auto_setup_part3.py` → Append to `auto_setup.py`
4. Copy `AutoSetup` class from `auto_setup_merged.py` → Replace in `auto_setup.py`
5. Same for `smart_bot.py`

**Recommendation:** Use merged files directly - they're cleaner and easier to maintain!

