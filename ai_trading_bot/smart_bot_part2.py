"""
Part 2: Smart Bot - Auto-Optimization Loop
This part handles background auto-optimization.
"""
import time
import threading
from typing import Optional

from .auto_setup_merged import AutoSetup
from .main import TradingBot
from .utils.logger import get_logger

logger = get_logger(__name__)


class SmartTradingBotPart2:
    """Part 2: Auto-optimization background thread."""
    
    def __init__(self, bot: TradingBot, auto_setup: AutoSetup, 
                 optimize_interval_hours: int = 24):
        self.bot = bot
        self.auto_setup = auto_setup
        self.optimize_interval_hours = optimize_interval_hours
        self.is_running = False
        self.optimize_thread: Optional[threading.Thread] = None
        
    def start_auto_optimization(self) -> None:
        """Start background thread for auto-optimization."""
        def optimize_loop():
            while self.is_running:
                time.sleep(self.optimize_interval_hours * 3600)
                if not self.is_running:
                    break
                
                logger.info("🔄 Running auto-optimization...")
                try:
                    optimized_config = self.auto_setup.auto_optimize(days=7)
                    
                    # Reload bot with new config
                    if self.bot:
                        logger.info("🔄 Reloading bot with optimized configuration...")
                        self.bot.stop()
                        from pathlib import Path
                        config_path = Path("ai_trading_bot/config/config.yaml")
                        self.bot = TradingBot(config_path)
                        self.bot.start()
                        logger.info("✅ Bot reloaded with optimized settings!")
                except Exception as e:
                    logger.error(f"❌ Auto-optimization failed: {e}", exc_info=True)
        
        self.is_running = True
        self.optimize_thread = threading.Thread(target=optimize_loop, daemon=True)
        self.optimize_thread.start()
        logger.info(f"🔄 Auto-optimization enabled (every {self.optimize_interval_hours} hours)")
    
    def stop(self) -> None:
        """Stop auto-optimization."""
        self.is_running = False

