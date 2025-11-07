"""
Part 1: Smart Bot - Main Bot Initialization
This part handles bot initialization and starting.
"""
import time
from typing import Optional
from pathlib import Path

from .auto_setup_merged import AutoSetup
from .main import TradingBot
from .utils.logger import get_logger

logger = get_logger(__name__)


class SmartTradingBotPart1:
    """Part 1: Bot initialization and startup."""
    
    def __init__(self, capital: Optional[float] = None, mode: str = "auto"):
        self.capital = capital
        self.mode = mode
        self.auto_setup = AutoSetup()
        self.bot: Optional[TradingBot] = None
        self.is_running = False
        
    def initialize_and_start(self) -> TradingBot:
        """Initialize and start the trading bot."""
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
        logger.info("=" * 60)
        
        return self.bot
    
    def stop(self) -> None:
        """Stop the bot."""
        logger.info("🛑 Stopping Smart Trading Bot...")
        self.is_running = False
        
        if self.bot:
            self.bot.stop()
        
        logger.info("✅ Smart Trading Bot stopped.")

