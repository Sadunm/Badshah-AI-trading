"""
Part 3: Auto-Setup - Performance Analysis and Adaptation
This part handles performance analysis and self-adaptation.
"""
from typing import Dict, Any
from pathlib import Path
import yaml

from .utils.logger import get_logger
from .config import load_config

logger = get_logger(__name__)


class AutoSetupPart3:
    """Part 3: Performance analysis and adaptation."""
    
    def __init__(self, config):
        self.config = config
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save optimized configuration"""
        config_path = Path("ai_trading_bot/config/config.yaml")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"💾 Configuration saved to {config_path}")
    
    def _analyze_performance(self, days: int) -> Dict[str, Any]:
        """Analyze recent trading performance"""
        try:
            from .auto_setup_performance import PerformanceAnalyzer
            analyzer = PerformanceAnalyzer()
            return analyzer.analyze_performance(days)
        except Exception as e:
            logger.warning(f"Performance analysis failed, using defaults: {e}")
            # Return empty metrics if analysis fails
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "avg_profit": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0
            }
    
    def _adapt_to_performance(self, performance: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt configuration based on performance"""
        import copy
        config = copy.deepcopy(self.config)
        
        win_rate = performance.get("win_rate", 0.0)
        sharpe = performance.get("sharpe_ratio", 0.0)
        
        # If performance is poor, tighten parameters
        if win_rate < 0.4 or sharpe < 0:
            config["risk"]["max_position_size_pct"] *= 0.8
            config["risk"]["max_drawdown_pct"] *= 0.9
            # Increase confidence thresholds
            for strategy in config["strategies"].values():
                if isinstance(strategy, dict) and "min_confidence" in strategy:
                    strategy["min_confidence"] = min(0.95, strategy["min_confidence"] * 1.1)
        
        # If performance is excellent, can be more aggressive
        elif win_rate > 0.6 and sharpe > 1.5:
            config["trading"]["max_position_size_pct"] = min(5.0, config["trading"]["max_position_size_pct"] * 1.1)
            # Lower confidence thresholds slightly
            for strategy in config["strategies"].values():
                if isinstance(strategy, dict) and "min_confidence" in strategy:
                    strategy["min_confidence"] = max(0.5, strategy["min_confidence"] * 0.95)
        
        return config

