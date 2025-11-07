"""
Performance Analysis Module for Auto-Setup
Analyzes real trade history and calculates performance metrics.
"""
import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime, timedelta
import numpy as np

from .utils.logger import get_logger
from .utils.trade_storage import TradeStorage

logger = get_logger(__name__)


class PerformanceAnalyzer:
    """Analyzes trading performance from trade history."""
    
    def __init__(self, trade_storage: Optional[TradeStorage] = None):
        """
        Initialize performance analyzer.
        
        Args:
            trade_storage: TradeStorage instance (creates new if None)
        """
        self.trade_storage = trade_storage or TradeStorage()
    
    def analyze_performance(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze performance from last N days.
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Performance metrics dictionary
        """
        try:
            # Get trades from last N days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            trades = self.trade_storage.get_trades(
                start_date=start_date,
                end_date=end_date
            )
            
            if not trades or len(trades) == 0:
                logger.warning(f"No trades found in last {days} days")
                return self._empty_metrics()
            
            # Calculate metrics
            total_trades = len(trades)
            winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
            losing_trades = [t for t in trades if t.get("pnl", 0) < 0]
            
            win_count = len(winning_trades)
            loss_count = len(losing_trades)
            win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0
            
            # Calculate P&L
            total_pnl = sum(t.get("pnl", 0) for t in trades)
            avg_profit = total_pnl / total_trades if total_trades > 0 else 0.0
            
            # Calculate returns
            initial_capital = trades[0].get("initial_capital", 100.0) if trades else 100.0
            final_capital = initial_capital + total_pnl
            total_return = (total_pnl / initial_capital * 100) if initial_capital > 0 else 0.0
            
            # Calculate Sharpe ratio
            returns = [t.get("pnl", 0) / initial_capital for t in trades if initial_capital > 0]
            sharpe_ratio = self._calculate_sharpe_ratio(returns, days)
            
            # Calculate max drawdown
            equity_curve = self._calculate_equity_curve(trades, initial_capital)
            max_drawdown = self._calculate_max_drawdown(equity_curve)
            
            # Strategy performance
            strategy_performance = self._analyze_strategy_performance(trades)
            
            metrics = {
                "total_trades": total_trades,
                "winning_trades": win_count,
                "losing_trades": loss_count,
                "win_rate": win_rate / 100.0,  # Convert to 0-1 range
                "total_pnl": total_pnl,
                "avg_profit": avg_profit,
                "total_return": total_return,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
                "initial_capital": initial_capital,
                "final_capital": final_capital,
                "strategy_performance": strategy_performance,
                "period_days": days
            }
            
            logger.info(f"📊 Performance Analysis ({days} days):")
            logger.info(f"   Trades: {total_trades} (Win: {win_count}, Loss: {loss_count})")
            logger.info(f"   Win Rate: {win_rate:.2f}%")
            logger.info(f"   Total P&L: ${total_pnl:.2f}")
            logger.info(f"   Return: {total_return:.2f}%")
            logger.info(f"   Sharpe Ratio: {sharpe_ratio:.2f}")
            logger.info(f"   Max Drawdown: {max_drawdown:.2f}%")
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing performance: {e}", exc_info=True)
            return self._empty_metrics()
    
    def _calculate_sharpe_ratio(self, returns: List[float], days: int) -> float:
        """Calculate Sharpe ratio from returns."""
        if not returns or len(returns) < 2:
            return 0.0
        
        try:
            returns_array = np.array(returns)
            mean_return = np.mean(returns_array)
            std_return = np.std(returns_array)
            
            if std_return == 0:
                return 0.0
            
            # Annualized Sharpe ratio
            periods_per_year = 365 / days if days > 0 else 252
            sharpe = (mean_return / std_return) * np.sqrt(periods_per_year)
            return float(sharpe)
        except Exception:
            return 0.0
    
    def _calculate_equity_curve(self, trades: List[Dict], initial_capital: float) -> List[float]:
        """Calculate equity curve from trades."""
        equity = [initial_capital]
        current_equity = initial_capital
        
        for trade in trades:
            current_equity += trade.get("pnl", 0)
            equity.append(current_equity)
        
        return equity
    
    def _calculate_max_drawdown(self, equity_curve: List[float]) -> float:
        """Calculate maximum drawdown from equity curve."""
        if not equity_curve or len(equity_curve) < 2:
            return 0.0
        
        try:
            equity_array = np.array(equity_curve)
            peak = np.maximum.accumulate(equity_array)
            drawdown = (equity_array - peak) / peak * 100
            max_drawdown = abs(np.min(drawdown))
            return float(max_drawdown)
        except Exception:
            return 0.0
    
    def _analyze_strategy_performance(self, trades: List[Dict]) -> Dict[str, Dict[str, float]]:
        """Analyze performance by strategy."""
        strategy_stats = {}
        
        for trade in trades:
            strategy = trade.get("reason", "unknown")
            if strategy not in strategy_stats:
                strategy_stats[strategy] = {
                    "trades": 0,
                    "wins": 0,
                    "losses": 0,
                    "total_pnl": 0.0
                }
            
            stats = strategy_stats[strategy]
            stats["trades"] += 1
            pnl = trade.get("pnl", 0)
            stats["total_pnl"] += pnl
            
            if pnl > 0:
                stats["wins"] += 1
            elif pnl < 0:
                stats["losses"] += 1
        
        # Calculate win rates
        for strategy, stats in strategy_stats.items():
            stats["win_rate"] = (stats["wins"] / stats["trades"] * 100) if stats["trades"] > 0 else 0.0
            stats["avg_pnl"] = stats["total_pnl"] / stats["trades"] if stats["trades"] > 0 else 0.0
        
        return strategy_stats
    
    def _empty_metrics(self) -> Dict[str, Any]:
        """Return empty metrics dictionary."""
        return {
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "win_rate": 0.0,
            "total_pnl": 0.0,
            "avg_profit": 0.0,
            "total_return": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "initial_capital": 0.0,
            "final_capital": 0.0,
            "strategy_performance": {},
            "period_days": 0
        }

