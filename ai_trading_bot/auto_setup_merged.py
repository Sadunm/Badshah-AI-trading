"""
Auto-Setup System - Merged from Parts 1, 2, 3
Import and use this after merging the parts.
"""
from typing import Dict, Optional, Any
from pathlib import Path

from .auto_setup_part1 import AutoSetupPart1
from .auto_setup_part2 import AutoSetupPart2
from .auto_setup_part3 import AutoSetupPart3
from .utils.logger import get_logger
from .config import load_config

logger = get_logger(__name__)


class AutoSetup:
    """
    Intelligent auto-setup system that:
    1. Auto-detects environment
    2. Auto-optimizes parameters
    3. Auto-selects best strategies
    4. Self-adapts based on performance
    """
    
    def __init__(self):
        self.part1 = AutoSetupPart1()
        self.part2 = AutoSetupPart2()
        self.config = None
        self.optimization_history = []
        self.performance_data = {}
        
    def setup(self, capital: Optional[float] = None, mode: str = "auto") -> Dict[str, Any]:
        """
        Main setup function - one command to rule them all!
        
        Args:
            capital: Initial capital (auto-detected if None)
            mode: Setup mode - "auto", "conservative", "aggressive", "balanced"
        
        Returns:
            Optimized configuration
        """
        logger.info("🤖 Starting Intelligent Auto-Setup...")
        
        # Step 1: Detect environment
        env_info = self.part1._detect_environment()
        logger.info(f"📍 Environment detected: {env_info}")
        
        # Step 2: Auto-configure based on environment
        self.config = self.part1._auto_configure(env_info, capital, mode)
        logger.info("⚙️ Auto-configuration complete")
        
        # Step 3: Optimize parameters
        optimized_config = self.part2._optimize_parameters(self.config)
        logger.info("🎯 Parameter optimization complete")
        
        # Step 4: Select best strategies
        best_strategies = self.part2._select_best_strategies(optimized_config)
        optimized_config["strategies"] = best_strategies
        logger.info("📊 Strategy selection complete")
        
        # Step 5: Save config
        part3 = AutoSetupPart3(optimized_config)
        part3._save_config(optimized_config)
        logger.info("✅ Auto-setup complete! Your bot is ready to trade.")
        
        self.config = optimized_config
        return optimized_config
    
    def auto_optimize(self, days: int = 7) -> Dict[str, Any]:
        """
        Continuously optimize based on recent performance.
        Runs periodically to adapt to changing market conditions.
        """
        logger.info(f"🔄 Starting auto-optimization (last {days} days)...")
        
        # Load current config
        self.config = load_config()
        
        # Analyze recent performance
        part3 = AutoSetupPart3(self.config)
        performance = part3._analyze_performance(days)
        
        # Adjust parameters based on performance
        optimized = part3._adapt_to_performance(performance)
        
        # Save optimized config
        part3._save_config(optimized)
        
        logger.info("✅ Auto-optimization complete")
        return optimized


def setup_bot(capital: Optional[float] = None, mode: str = "auto") -> Dict[str, Any]:
    """
    One-command setup function - just call this and your bot is ready!
    
    Usage:
        from ai_trading_bot.auto_setup_merged import setup_bot
        config = setup_bot(capital=100, mode="balanced")
    """
    auto_setup = AutoSetup()
    return auto_setup.setup(capital, mode)

