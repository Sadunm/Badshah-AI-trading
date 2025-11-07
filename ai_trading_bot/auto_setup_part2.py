"""
Part 2: Auto-Setup - Parameter Optimization
This part handles parameter optimization using backtesting.
"""
from typing import Dict, Any
import copy

from .utils.logger import get_logger
from .backtesting.backtest_engine import BacktestEngine
from .data.data_manager import DataManager

logger = get_logger(__name__)


class AutoSetupPart2:
    """Part 2: Parameter optimization."""
    
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
                    
                    test_config = copy.deepcopy(config)
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
                            best_config = copy.deepcopy(test_config)
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
        capital = config["trading"]["initial_capital"]
        
        # Adjust confidence based on capital
        if capital < 100:
            strategies["momentum"]["min_confidence"] = 0.7
            strategies["mean_reversion"]["min_confidence"] = 0.75
            strategies["breakout"]["min_confidence"] = 0.8
            strategies["trend_following"]["min_confidence"] = 0.85
        else:
            strategies["momentum"]["min_confidence"] = 0.6
            strategies["mean_reversion"]["min_confidence"] = 0.65
            strategies["breakout"]["min_confidence"] = 0.7
            strategies["trend_following"]["min_confidence"] = 0.75
        
        return strategies

