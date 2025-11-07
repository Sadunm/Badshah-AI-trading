"""
Smart Trading Bot - Intelligent Auto-Setup and Self-Optimizing Trading System
Just run this and the bot will automatically:
1. Detect environment and configure itself
2. Optimize parameters for maximum profitability
3. Self-adapt based on performance
4. Trade intelligently like a human expert

Usage:
    python -m ai_trading_bot.smart_bot
    # Or with custom settings:
    python -m ai_trading_bot.smart_bot --capital 100 --mode balanced
"""
import argparse
import time
import threading
from typing import Optional
from pathlib import Path

from .auto_setup import AutoSetup, setup_bot
from .main import TradingBot
from .utils.logger import get_logger

logger = get_logger(__name__)


class SmartTradingBot:
    """
    Intelligent trading bot that automatically:
    - Sets up and configures itself
    - Optimizes parameters
    - Self-adapts to market conditions
    - Monitors and improves performance
    """
    
    def __init__(self, capital: Optional[float] = None, mode: str = "auto", 
                 auto_optimize: bool = True, optimize_interval_hours: int = 24):
        """
        Initialize smart trading bot.
        
        Args:
            capital: Initial capital (auto-detected if None)
            mode: Trading mode - "auto", "conservative", "aggressive", "balanced"
            auto_optimize: Enable automatic optimization
            optimize_interval_hours: Hours between auto-optimizations
        """
        self.capital = capital
        self.mode = mode
        self.auto_optimize = auto_optimize
        self.optimize_interval_hours = optimize_interval_hours
        
        self.auto_setup = AutoSetup()
        self.bot: Optional[TradingBot] = None
        self.optimize_thread: Optional[threading.Thread] = None
        self.is_running = False
        
    def start(self) -> None:
        """Start the smart trading bot."""
        logger.info("🚀 Starting Smart Trading Bot...")
        logger.info("=" * 60)
        
        # Step 1: Auto-setup
        logger.info("📋 Step 1: Auto-Setup and Configuration...")
        config = self.auto_setup.setup(self.capital, self.mode)
        logger.info("✅ Setup complete!")
        logger.info("")
        
        # Step 2: Initialize trading bot
        logger.info("🤖 Step 2: Initializing Trading Bot...")
        config_path = Path("ai_trading_bot/config/config.yaml")
        self.bot = TradingBot(config_path)
        logger.info("✅ Bot initialized!")
        logger.info("")
        
        # Step 3: Start trading
        logger.info("💰 Step 3: Starting Trading...")
        self.bot.start()
        self.is_running = True
        logger.info("✅ Trading started!")
        logger.info("")
        logger.info("=" * 60)
        logger.info("🎉 Smart Trading Bot is now running!")
        logger.info("📊 The bot will automatically:")
        logger.info("   - Monitor market conditions")
        logger.info("   - Generate trading signals")
        logger.info("   - Execute trades with risk management")
        if self.auto_optimize:
            logger.info(f"   - Auto-optimize every {self.optimize_interval_hours} hours")
        logger.info("=" * 60)
        
        # Step 4: Start auto-optimization thread
        if self.auto_optimize:
            self._start_auto_optimization()
        
        # Keep running
        try:
            while self.is_running:
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\n⚠️ Shutting down...")
            self.stop()
    
    def _start_auto_optimization(self) -> None:
        """Start background thread for auto-optimization."""
        def optimize_loop():
            while self.is_running:
                time.sleep(self.optimize_interval_hours * 3600)  # Convert hours to seconds
                if not self.is_running:
                    break
                
                logger.info("🔄 Running auto-optimization...")
                try:
                    optimized_config = self.auto_setup.auto_optimize(days=7)
                    
                    # Reload bot with new config
                    if self.bot:
                        logger.info("🔄 Reloading bot with optimized configuration...")
                        self.bot.stop()
                        config_path = Path("ai_trading_bot/config/config.yaml")
                        self.bot = TradingBot(config_path)
                        self.bot.start()
                        logger.info("✅ Bot reloaded with optimized settings!")
                except Exception as e:
                    logger.error(f"❌ Auto-optimization failed: {e}", exc_info=True)
        
        self.optimize_thread = threading.Thread(target=optimize_loop, daemon=True)
        self.optimize_thread.start()
        logger.info(f"🔄 Auto-optimization enabled (every {self.optimize_interval_hours} hours)")
    
    def stop(self) -> None:
        """Stop the smart trading bot."""
        logger.info("🛑 Stopping Smart Trading Bot...")
        self.is_running = False
        
        if self.bot:
            self.bot.stop()
        
        logger.info("✅ Smart Trading Bot stopped.")


def main():
    """Main entry point for smart trading bot."""
    parser = argparse.ArgumentParser(
        description="Smart Trading Bot - Auto-setup and self-optimizing trading system"
    )
    parser.add_argument(
        "--capital",
        type=float,
        default=None,
        help="Initial capital (auto-detected if not specified)"
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="auto",
        choices=["auto", "conservative", "aggressive", "balanced"],
        help="Trading mode: auto, conservative, aggressive, or balanced"
    )
    parser.add_argument(
        "--no-auto-optimize",
        action="store_true",
        help="Disable automatic optimization"
    )
    parser.add_argument(
        "--optimize-interval",
        type=int,
        default=24,
        help="Hours between auto-optimizations (default: 24)"
    )
    
    args = parser.parse_args()
    
    # Create and start smart bot
    smart_bot = SmartTradingBot(
        capital=args.capital,
        mode=args.mode,
        auto_optimize=not args.no_auto_optimize,
        optimize_interval_hours=args.optimize_interval
    )
    
    smart_bot.start()


if __name__ == "__main__":
    main()

