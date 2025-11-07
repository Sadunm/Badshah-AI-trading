"""
Part 1: Auto-Setup - Environment Detection and Configuration
This part handles environment detection and initial configuration.
"""
import os
from typing import Dict, Optional, Any
from pathlib import Path

from .utils.logger import get_logger
from .config import load_config, get_default_config

logger = get_logger(__name__)


class AutoSetupPart1:
    """Part 1: Environment detection and configuration."""
    
    def __init__(self):
        self.config = None
    
    def _detect_environment(self) -> Dict[str, Any]:
        """Detect environment (API keys, exchange, capital, etc.)"""
        env = {
            "has_openrouter": bool(os.getenv("OPENROUTER_API_KEY")),
            "has_exchange_api": bool(os.getenv("BYBIT_API_KEY") or os.getenv("BINANCE_API_KEY")),
            "exchange": "bybit" if os.getenv("BYBIT_API_KEY") else "binance" if os.getenv("BINANCE_API_KEY") else "mock",
            "is_paper_trading": True,  # Default to paper trading for safety
            "platform": "render" if os.getenv("RENDER") else "local"
        }
        return env
    
    def _auto_configure(self, env_info: Dict, capital: Optional[float], mode: str) -> Dict[str, Any]:
        """Auto-configure based on environment and mode"""
        config = get_default_config()
        
        # Set capital
        if capital:
            config["trading"]["initial_capital"] = capital
        else:
            # Auto-detect from config or use default
            try:
                existing_config = load_config()
                config["trading"]["initial_capital"] = existing_config.get("trading", {}).get("initial_capital", 10.0)
            except:
                config["trading"]["initial_capital"] = 10.0
        
        capital = config["trading"]["initial_capital"]
        
        # Configure based on mode
        if mode == "conservative":
            config["trading"]["max_position_size_pct"] = 0.5
            config["risk"]["max_drawdown_pct"] = 2.0
            config["risk"]["max_daily_loss_pct"] = 1.0
            config["risk"]["stop_loss_pct"] = 0.3
            config["risk"]["take_profit_pct"] = 0.6
        elif mode == "aggressive":
            config["trading"]["max_position_size_pct"] = 5.0
            config["risk"]["max_drawdown_pct"] = 10.0
            config["risk"]["max_daily_loss_pct"] = 5.0
            config["risk"]["stop_loss_pct"] = 1.0
            config["risk"]["take_profit_pct"] = 2.0
        else:  # balanced or auto
            # Auto-adjust based on capital
            if capital < 50:
                config["trading"]["max_position_size_pct"] = 1.0
                config["risk"]["max_drawdown_pct"] = 5.0
                config["risk"]["max_daily_loss_pct"] = 2.0
            elif capital < 500:
                config["trading"]["max_position_size_pct"] = 2.0
                config["risk"]["max_drawdown_pct"] = 7.0
                config["risk"]["max_daily_loss_pct"] = 3.0
            else:
                config["trading"]["max_position_size_pct"] = 3.0
                config["risk"]["max_drawdown_pct"] = 10.0
                config["risk"]["max_daily_loss_pct"] = 4.0
        
        # Configure exchange
        config["exchange"]["name"] = env_info["exchange"]
        config["trading"]["paper_trading"] = env_info["is_paper_trading"]
        
        # Auto-select symbols based on capital
        if capital < 100:
            config["data"]["symbols"] = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        elif capital < 1000:
            config["data"]["symbols"] = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
        else:
            config["data"]["symbols"] = [
                "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
                "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "MATICUSDT"
            ]
        
        return config

