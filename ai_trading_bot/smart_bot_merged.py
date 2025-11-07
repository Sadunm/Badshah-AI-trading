"""
Smart Trading Bot - Merged from Parts 1 & 2
Import and use this after merging the parts.
"""
import argparse
import time
from typing import Optional
from pathlib import Path

from .smart_bot_part1 import SmartTradingBotPart1
from .smart_bot_part2 import SmartTradingBotPart2
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
        self.part1 = SmartTradingBotPart1(capital, mode)
        self.part2 = None
        self.auto_optimize = auto_optimize
        self.optimize_interval_hours = optimize_interval_hours
        
    def start(self) -> None:
        """Start the smart trading bot."""
        # Initialize and start bot
        bot = self.part1.initialize_and_start()
        
        # Start auto-optimization if enabled
        if self.auto_optimize:
            self.part2 = SmartTradingBotPart2(
                bot, 
                self.part1.auto_setup, 
                self.optimize_interval_hours
            )
            self.part2.start_auto_optimization()
            logger.info(f"   - Auto-optimize every {self.optimize_interval_hours} hours")
        
        # Keep running
        try:
            while self.part1.is_running:
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\n⚠️ Shutting down...")
            self.stop()
    
    def stop(self) -> None:
        """Stop the smart trading bot."""
        if self.part2:
            self.part2.stop()
        self.part1.stop()


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

