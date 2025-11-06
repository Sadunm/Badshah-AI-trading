"""
Backtesting engine for testing trading strategies on historical data.
"""
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
if str(Path(__file__).parent.parent.parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_trading_bot.utils.logger import get_logger
from ai_trading_bot.risk.risk_manager import RiskManager
from ai_trading_bot.allocator.position_allocator import PositionAllocator
from ai_trading_bot.execution.order_executor import OrderExecutor
from ai_trading_bot.features.indicators import calculate_all_indicators
from ai_trading_bot.strategies.ai_signal_generator import AISignalGenerator
from ai_trading_bot.strategies.momentum_strategy import MomentumStrategy
from ai_trading_bot.strategies.mean_reversion_strategy import MeanReversionStrategy
from ai_trading_bot.strategies.breakout_strategy import BreakoutStrategy
from ai_trading_bot.strategies.trend_following_strategy import TrendFollowingStrategy
from ai_trading_bot.strategies.meta_ai_strategy import MetaAIStrategy

logger = get_logger(__name__)


class BacktestEngine:
    """Backtesting engine for historical data."""
    
    def __init__(self, config: Dict[str, Any], historical_data: Dict[str, List[Dict]]):
        """
        Initialize backtesting engine.
        
        Args:
            config: Configuration dictionary
            trading_config: Trading configuration
            historical_data: Dictionary of symbol -> list of candles
        """
        self.config = config
        self.historical_data = historical_data
        
        # Initialize components
        trading_config = config.get("trading", {})
        risk_config = config.get("risk", {})
        strategies_config = config.get("strategies", {})
        openrouter_config = config.get("openrouter", {})
        
        initial_capital = trading_config.get("initial_capital", 10.0)
        
        # Risk and allocation
        self.risk_manager = RiskManager(
            initial_capital,
            risk_config.get("max_drawdown_pct", 5.0),
            risk_config.get("max_daily_loss_pct", 2.0),
            risk_config.get("max_daily_trades", 100)
        )
        
        self.position_allocator = PositionAllocator(
            initial_capital,
            trading_config.get("max_position_size_pct", 1.0),
            trading_config.get("max_portfolio_risk_pct", 20.0)
        )
        
        self.order_executor = OrderExecutor(
            trading_config.get("paper_trading", True)
        )
        
        # Strategies
        self.ai_signal_generator = AISignalGenerator(
            openrouter_config.get("api_key"),
            openrouter_config.get("base_url"),
            openrouter_config.get("default_model"),
            openrouter_config.get("timeout", 30.0),
            strategies_config.get("momentum", {}).get("min_confidence", 0.6)
        )
        
        self.momentum_strategy = MomentumStrategy(
            strategies_config.get("momentum", {}).get("min_confidence", 0.6)
        )
        self.mean_reversion_strategy = MeanReversionStrategy(
            strategies_config.get("mean_reversion", {}).get("min_confidence", 0.65)
        )
        self.breakout_strategy = BreakoutStrategy(
            strategies_config.get("breakout", {}).get("min_confidence", 0.7)
        )
        self.trend_following_strategy = TrendFollowingStrategy(
            strategies_config.get("trend_following", {}).get("min_confidence", 0.75)
        )
        
        self.meta_ai_strategy = MetaAIStrategy(
            openrouter_config.get("api_key"),
            openrouter_config.get("base_url"),
            openrouter_config.get("default_model"),
            openrouter_config.get("timeout", 30.0),
            strategies_config.get("meta_ai", {}).get("risk_check_enabled", True)
        )
        
        # Results
        self.results: Dict[str, Any] = {
            "trades": [],
            "daily_pnl": {},
            "equity_curve": [],
            "metrics": {}
        }
    
    def run(self, symbol: str, start_date: Optional[datetime] = None, 
            end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        Run backtest on historical data.
        
        Args:
            symbol: Trading symbol
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            Backtest results dictionary
        """
        if symbol not in self.historical_data:
            logger.error(f"No historical data for {symbol}")
            return {}
        
        candles = self.historical_data[symbol]
        if not candles:
            logger.error(f"Empty historical data for {symbol}")
            return {}
        
        # Filter by date if provided
        if start_date or end_date:
            filtered_candles = []
            for candle in candles:
                candle_time = datetime.fromtimestamp(candle["open_time"] / 1000)
                if start_date and candle_time < start_date:
                    continue
                if end_date and candle_time > end_date:
                    continue
                filtered_candles.append(candle)
            candles = filtered_candles
        
        if len(candles) < 30:
            logger.error(f"Insufficient data for {symbol}: {len(candles)} candles")
            return {}
        
        logger.info(f"Running backtest for {symbol} with {len(candles)} candles")
        
        # Reset state
        self.results = {
            "trades": [],
            "daily_pnl": {},
            "equity_curve": [],
            "metrics": {}
        }
        
        # Process candles in chronological order
        for i in range(30, len(candles)):  # Start from 30 to have enough data for indicators
            try:
                # Get historical candles up to current point
                historical_candles = candles[:i+1]
                current_candle = candles[i]
                current_price = current_candle["close"]
                current_time = datetime.fromtimestamp(current_candle["open_time"] / 1000)
                
                # Calculate indicators
                indicators = calculate_all_indicators(historical_candles)
                if not indicators:
                    continue
                
                indicators["current_price"] = current_price
                
                # Check existing positions for stop loss/take profit
                open_positions = self.risk_manager.get_open_positions()
                for pos_symbol, position in list(open_positions.items()):
                    if pos_symbol == symbol:
                        trigger = self.risk_manager.check_stop_loss_take_profit(symbol, current_price)
                        if trigger:
                            execution = self.order_executor.close_order(symbol, position, current_price)
                            if execution:
                                trade = self.risk_manager.close_position(
                                    symbol,
                                    execution["executed_price"],
                                    trigger
                                )
                                if trade:
                                    self.results["trades"].append({
                                        **trade,
                                        "timestamp": current_time.isoformat()
                                    })
                                    self.position_allocator.update_capital(
                                        self.risk_manager.get_current_capital()
                                    )
                
                # Skip if already have position
                if symbol in open_positions:
                    # Update equity curve
                    equity = self.risk_manager.get_current_capital()
                    self.results["equity_curve"].append({
                        "timestamp": current_time.isoformat(),
                        "equity": equity,
                        "price": current_price
                    })
                    continue
                
                # Generate signal (every 30 candles to simulate 30-second intervals)
                if i % 6 == 0:  # Every 6 candles (30 minutes if 5m candles)
                    signal = None
                    
                    # Try AI signal generator
                    if self.ai_signal_generator.enabled:
                        signal = self.ai_signal_generator.generate_signal(indicators, symbol)
                    
                    # Fallback to rule-based strategies
                    if signal is None:
                        strategies = [
                            self.momentum_strategy,
                            self.mean_reversion_strategy,
                            self.breakout_strategy,
                            self.trend_following_strategy
                        ]
                        
                        for strategy in strategies:
                            if strategy.enabled:
                                signal = strategy.generate_signal(indicators, symbol)
                                if signal:
                                    break
                    
                    # Meta AI validation
                    if signal:
                        if not self.meta_ai_strategy.validate_signal_risk(signal, indicators, symbol):
                            logger.debug(f"Meta AI rejected signal for {symbol}")
                            signal = None
                    
                    # Execute signal
                    if signal and signal.get("action") != "FLAT":
                        if self.risk_manager.can_open_position():
                            position_size = self.position_allocator.calculate_position_size(
                                signal, current_price
                            )
                            
                            if position_size and position_size > 0:
                                execution = self.order_executor.execute_order(
                                    symbol,
                                    signal["action"],
                                    position_size,
                                    signal.get("entry_price", current_price),
                                    current_price
                                )
                                
                                if execution:
                                    position = {
                                        "action": signal["action"],
                                        "size": position_size,
                                        "entry_price": execution["executed_price"],
                                        "stop_loss": signal.get("stop_loss", current_price * 0.995),
                                        "take_profit": signal.get("take_profit", current_price * 1.01),
                                        "reason": signal.get("reason", "Signal")
                                    }
                                    
                                    if self.risk_manager.open_position(symbol, position):
                                        logger.debug(f"Position opened in backtest: {symbol} {signal['action']} @ ${execution['executed_price']:.2f}")
                
                # Update equity curve
                equity = self.risk_manager.get_current_capital()
                self.results["equity_curve"].append({
                    "timestamp": current_time.isoformat(),
                    "equity": equity,
                    "price": current_price
                })
                
            except Exception as e:
                logger.error(f"Error processing candle {i} for {symbol}: {e}", exc_info=True)
                continue
        
        # Close any remaining positions
        open_positions = self.risk_manager.get_open_positions()
        for pos_symbol, position in list(open_positions.items()):
            if pos_symbol == symbol:
                last_price = candles[-1]["close"]
                execution = self.order_executor.close_order(symbol, position, last_price)
                if execution:
                    trade = self.risk_manager.close_position(symbol, execution["executed_price"], "Backtest end")
                    if trade:
                        self.results["trades"].append({
                            **trade,
                            "timestamp": datetime.fromtimestamp(candles[-1]["open_time"] / 1000).isoformat()
                        })
        
        # Calculate metrics
        self._calculate_metrics()
        
        return self.results
    
    def _calculate_metrics(self) -> None:
        """Calculate backtest performance metrics."""
        trades = self.results["trades"]
        equity_curve = self.results["equity_curve"]
        
        if not trades:
            self.results["metrics"] = {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "total_return": 0.0,
                "max_drawdown": 0.0,
                "sharpe_ratio": 0.0
            }
            return
        
        # Basic metrics
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.get("net_pnl", 0) > 0)
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        
        total_pnl = sum(t.get("net_pnl", 0) for t in trades)
        initial_capital = self.risk_manager.initial_capital
        total_return = (total_pnl / initial_capital * 100) if initial_capital > 0 else 0.0
        
        # Max drawdown
        if equity_curve:
            equity_values = [e["equity"] for e in equity_curve]
            peak = equity_values[0]
            max_drawdown = 0.0
            for equity in equity_values:
                if equity > peak:
                    peak = equity
                drawdown = ((peak - equity) / peak * 100) if peak > 0 else 0.0
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
        else:
            max_drawdown = 0.0
        
        # Sharpe ratio (simplified)
        if len(equity_curve) > 1:
            returns = []
            for i in range(1, len(equity_curve)):
                prev_equity = equity_curve[i-1]["equity"]
                curr_equity = equity_curve[i]["equity"]
                if prev_equity > 0:
                    ret = (curr_equity - prev_equity) / prev_equity
                    returns.append(ret)
            
            if returns:
                import numpy as np
                mean_return = np.mean(returns)
                std_return = np.std(returns)
                sharpe_ratio = (mean_return / std_return * np.sqrt(252)) if std_return > 0 else 0.0
            else:
                sharpe_ratio = 0.0
        else:
            sharpe_ratio = 0.0
        
        self.results["metrics"] = {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "total_return": total_return,
            "max_drawdown": max_drawdown,
            "sharpe_ratio": sharpe_ratio,
            "final_capital": self.risk_manager.get_current_capital(),
            "initial_capital": initial_capital
        }

