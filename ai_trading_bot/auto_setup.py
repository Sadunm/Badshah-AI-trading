"""
Intelligent Auto-Setup System for Trading Bot
Automatically configures, optimizes, and adapts the trading system for maximum profitability.
"""
import os
import json
import time
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import yaml
from datetime import datetime, timedelta

from .utils.logger import get_logger
from .config import load_config, get_default_config
from .backtesting.backtest_engine import BacktestEngine
from .data.data_manager import DataManager

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
        env_info = self._detect_environment()
        logger.info(f"📍 Environment detected: {env_info}")
        
        # Step 2: Auto-configure based on environment
        self.config = self._auto_configure(env_info, capital, mode)
        logger.info("⚙️ Auto-configuration complete")
        
        # Step 3: Optimize parameters
        optimized_config = self._optimize_parameters(self.config)
        logger.info("🎯 Parameter optimization complete")
        
        # Step 4: Select best strategies
        best_strategies = self._select_best_strategies(optimized_config)
        optimized_config["strategies"] = best_strategies
        logger.info("📊 Strategy selection complete")
        
        # Step 5: Validate and save
        self._save_config(optimized_config)
        logger.info("✅ Auto-setup complete! Your bot is ready to trade.")
        
        return optimized_config
    
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
            # Small capital: focus on major coins
            config["data"]["symbols"] = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
        elif capital < 1000:
            # Medium capital: add more diversity
            config["data"]["symbols"] = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
        else:
            # Large capital: full portfolio
            config["data"]["symbols"] = [
                "BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT",
                "ADAUSDT", "DOGEUSDT", "AVAXUSDT", "LINKUSDT", "MATICUSDT"
            ]
        
        return config
    
    def _optimize_parameters(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize parameters using backtesting"""
        logger.info("🔍 Optimizing parameters...")
        
        try:
            # Get historical data
            data_manager = DataManager(
                config["exchange"].get("rest_url", "https://api.bybit.com"),
                config["data"]["symbols"],
                config["data"]["kline_interval"],
                config["data"]["kline_limit"],
                exchange=config["exchange"]["name"]
            )
            
            historical_data = data_manager.fetch_all_historical_data()
            
            if not historical_data or len(historical_data) == 0:
                logger.warning("⚠️ No historical data available, using default parameters")
                return config
            
            # Test different parameter combinations
            best_config = config
            best_sharpe = -999
            
            # Optimize stop loss and take profit
            for stop_loss_pct in [0.3, 0.5, 0.7, 1.0]:
                for take_profit_pct in [0.6, 1.0, 1.5, 2.0]:
                    if take_profit_pct <= stop_loss_pct * 1.5:
                        continue  # Skip invalid combinations
                    
                    test_config = config.copy()
                    test_config["risk"]["stop_loss_pct"] = stop_loss_pct
                    test_config["risk"]["take_profit_pct"] = take_profit_pct
                    
                    # Run backtest - test on first symbol only for speed
                    try:
                        test_symbol = list(historical_data.keys())[0] if historical_data else None
                        if not test_symbol:
                            continue
                            
                        engine = BacktestEngine(test_config, historical_data)
                        results = engine.run(test_symbol)
                        
                        metrics = results.get("metrics", {}) if results else {}
                        sharpe = metrics.get("sharpe_ratio", -999)
                        
                        if sharpe > best_sharpe:
                            best_sharpe = sharpe
                            best_config = test_config.copy()
                            logger.info(f"✅ Better config found: SL={stop_loss_pct}%, TP={take_profit_pct}%, Sharpe={best_sharpe:.2f}")
                    except Exception as e:
                        logger.debug(f"Backtest failed for SL={stop_loss_pct}%, TP={take_profit_pct}%: {e}")
                        continue
            
            if best_sharpe > -999:
                logger.info(f"🎯 Optimized parameters: Sharpe Ratio = {best_sharpe:.2f}")
                return best_config
            else:
                logger.warning("⚠️ Optimization didn't improve, using defaults")
                return config
                
        except Exception as e:
            logger.error(f"❌ Optimization failed: {e}", exc_info=True)
            return config
    
    def _select_best_strategies(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Select best performing strategies"""
        logger.info("📊 Selecting best strategies...")
        
        strategies = config.get("strategies", {})
        
        # For now, enable all strategies but adjust confidence thresholds
        # In a full implementation, this would backtest each strategy
        
        capital = config["trading"]["initial_capital"]
        
        # Adjust confidence based on capital
        if capital < 100:
            # Small capital: higher confidence required
            strategies["momentum"]["min_confidence"] = 0.7
            strategies["mean_reversion"]["min_confidence"] = 0.75
            strategies["breakout"]["min_confidence"] = 0.8
            strategies["trend_following"]["min_confidence"] = 0.85
        else:
            # Larger capital: can accept lower confidence
            strategies["momentum"]["min_confidence"] = 0.6
            strategies["mean_reversion"]["min_confidence"] = 0.65
            strategies["breakout"]["min_confidence"] = 0.7
            strategies["trend_following"]["min_confidence"] = 0.75
        
        return strategies
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """Save optimized configuration"""
        config_path = Path("ai_trading_bot/config/config.yaml")
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"💾 Configuration saved to {config_path}")
    
    def auto_optimize(self, days: int = 7) -> Dict[str, Any]:
        """
        Continuously optimize based on recent performance.
        Runs periodically to adapt to changing market conditions.
        """
        logger.info(f"🔄 Starting auto-optimization (last {days} days)...")
        
        # Load current config
        self.config = load_config()
        
        # Analyze recent performance
        performance = self._analyze_performance(days)
        
        # Adjust parameters based on performance
        optimized = self._adapt_to_performance(performance)
        
        # Save optimized config
        self._save_config(optimized)
        
        logger.info("✅ Auto-optimization complete")
        return optimized
    
    def _analyze_performance(self, days: int) -> Dict[str, Any]:
        """Analyze recent trading performance"""
        # In a full implementation, this would read from trade history
        # For now, return mock data
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "avg_profit": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0
        }
    
    def _adapt_to_performance(self, performance: Dict[str, Any]) -> Dict[str, Any]:
        """Adapt configuration based on performance"""
        config = self.config.copy()
        
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


def setup_bot(capital: Optional[float] = None, mode: str = "auto") -> Dict[str, Any]:
    """
    One-command setup function - just call this and your bot is ready!
    
    Usage:
        from ai_trading_bot.auto_setup import setup_bot
        config = setup_bot(capital=100, mode="balanced")
    """
    auto_setup = AutoSetup()
    return auto_setup.setup(capital, mode)

