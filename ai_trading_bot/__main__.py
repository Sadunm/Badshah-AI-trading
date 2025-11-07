"""
Main entry point for running the trading bot.
Supports both regular bot and smart bot modes.
"""
import sys
import argparse
from pathlib import Path

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="AI Trading Bot - Smart Auto-Setup Trading System"
    )
    parser.add_argument(
        "--smart",
        action="store_true",
        help="Use smart bot mode (auto-setup and self-optimizing)"
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=None,
        help="Initial capital (for smart mode)"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="auto",
        choices=["auto", "conservative", "aggressive", "balanced"],
        help="Trading mode (for smart mode)"
    )
    parser.add_argument(
        "--no-auto-optimize",
        action="store_true",
        help="Disable auto-optimization (for smart mode)"
    )
    
    args = parser.parse_args()
    
    if args.smart:
        # Run smart bot
        try:
            from .smart_bot_merged import SmartTradingBot
            
            smart_bot = SmartTradingBot(
                capital=args.capital,
                mode=args.mode,
                auto_optimize=not args.no_auto_optimize
            )
            smart_bot.start()
        except ImportError:
            print("❌ Smart bot not available. Using regular bot mode.")
            print("   Run: python -m ai_trading_bot.main")
            from .main import TradingBot
            bot = TradingBot()
            bot.start()
    else:
        # Run regular bot
        from .main import TradingBot
        bot = TradingBot()
        bot.start()

if __name__ == "__main__":
    main()

