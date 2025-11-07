"""
Smart Commands - Simple commands for managing the trading bot
Human-like interface for bot control.
"""
import argparse
import sys
from pathlib import Path
from typing import Optional

def setup(capital: Optional[float] = None, mode: str = "auto"):
    """Setup and configure the bot."""
    print("🤖 Setting up trading bot...")
    try:
        from .auto_setup_merged import setup_bot
        config = setup_bot(capital, mode)
        print("✅ Setup complete!")
        return config
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return None

def start(capital: Optional[float] = None, mode: str = "auto"):
    """Start the trading bot."""
    print("🚀 Starting trading bot...")
    try:
        from .smart_bot_merged import SmartTradingBot
        bot = SmartTradingBot(capital=capital, mode=mode)
        bot.start()
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        sys.exit(1)

def status():
    """Check bot status."""
    print("📊 Checking bot status...")
    try:
        from .utils.trade_storage import TradeStorage
        from .auto_setup_performance import PerformanceAnalyzer
        
        storage = TradeStorage()
        analyzer = PerformanceAnalyzer(storage)
        
        performance = analyzer.analyze_performance(days=7)
        
        print("\n" + "=" * 60)
        print("📈 Trading Performance (Last 7 Days)")
        print("=" * 60)
        print(f"Total Trades: {performance['total_trades']}")
        print(f"Win Rate: {performance['win_rate']*100:.2f}%")
        print(f"Total P&L: ${performance['total_pnl']:.2f}")
        print(f"Return: {performance['total_return']:.2f}%")
        print(f"Sharpe Ratio: {performance['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {performance['max_drawdown']:.2f}%")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Status check failed: {e}")

def optimize():
    """Run optimization."""
    print("🔄 Optimizing bot parameters...")
    try:
        from .auto_setup_merged import AutoSetup
        auto_setup = AutoSetup()
        optimized = auto_setup.auto_optimize(days=7)
        print("✅ Optimization complete!")
        return optimized
    except Exception as e:
        print(f"❌ Optimization failed: {e}")
        return None

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Smart Trading Bot - Simple Commands"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup and configure bot")
    setup_parser.add_argument("--capital", type=float, default=None)
    setup_parser.add_argument("--mode", type=str, default="auto", 
                             choices=["auto", "conservative", "aggressive", "balanced"])
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start trading bot")
    start_parser.add_argument("--capital", type=float, default=None)
    start_parser.add_argument("--mode", type=str, default="auto",
                             choices=["auto", "conservative", "aggressive", "balanced"])
    
    # Status command
    subparsers.add_parser("status", help="Check bot status")
    
    # Optimize command
    subparsers.add_parser("optimize", help="Optimize bot parameters")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        setup(args.capital, args.mode)
    elif args.command == "start":
        start(args.capital, args.mode)
    elif args.command == "status":
        status()
    elif args.command == "optimize":
        optimize()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

