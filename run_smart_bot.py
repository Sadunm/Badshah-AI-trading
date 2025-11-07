#!/usr/bin/env python3
"""
Quick start script for Smart Trading Bot
Just run this file and the bot will automatically setup and start trading!
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Run smart trading bot."""
    print("=" * 60)
    print("🤖 Smart Trading Bot - Auto-Setup System")
    print("=" * 60)
    print()
    print("This bot will automatically:")
    print("  ✅ Detect your environment")
    print("  ✅ Configure optimal settings")
    print("  ✅ Optimize parameters")
    print("  ✅ Start trading intelligently")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    try:
        from ai_trading_bot.smart_bot_merged import SmartTradingBot
        
        # Start smart bot with auto-detection
        bot = SmartTradingBot(
            capital=None,  # Auto-detect
            mode="auto",   # Auto mode
            auto_optimize=True
        )
        bot.start()
    except KeyboardInterrupt:
        print("\n\n⚠️ Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTrying regular bot mode...")
        try:
            from ai_trading_bot.main import TradingBot
            bot = TradingBot()
            bot.start()
        except Exception as e2:
            print(f"❌ Failed to start bot: {e2}")
            sys.exit(1)

if __name__ == "__main__":
    main()

