"""
Performance analytics for trading bot.
Calculates comprehensive performance metrics.
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .logger import get_logger

logger = get_logger(__name__)


class PerformanceAnalytics:
    """Calculates performance metrics."""
    
    @staticmethod
    def calculate_metrics(trades: List[Dict], initial_capital: float) -> Dict:
        """
        Calculate comprehensive performance metrics.
        
        Args:
            trades: List of trade dictionaries
            initial_capital: Initial capital
            
        Returns:
            Metrics dictionary
        """
        if not trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "total_return": 0.0,
                "average_pnl": 0.0,
                "profit_factor": 0.0,
                "average_win": 0.0,
                "average_loss": 0.0,
                "largest_win": 0.0,
                "largest_loss": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0,
                "average_hold_time": 0.0
            }
        
        # Basic metrics
        winning_trades = [t for t in trades if t.get("net_pnl", 0) > 0]
        losing_trades = [t for t in trades if t.get("net_pnl", 0) < 0]
        
        total_trades = len(trades)
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0.0
        
        # P&L metrics
        total_pnl = sum(t.get("net_pnl", 0) for t in trades)
        total_return = (total_pnl / initial_capital * 100) if initial_capital > 0 else 0.0
        average_pnl = total_pnl / total_trades if total_trades > 0 else 0.0
        
        # Win/loss metrics
        total_wins = sum(t.get("net_pnl", 0) for t in winning_trades)
        total_losses = abs(sum(t.get("net_pnl", 0) for t in losing_trades))
        
        average_win = total_wins / win_count if win_count > 0 else 0.0
        average_loss = total_losses / loss_count if loss_count > 0 else 0.0
        
        largest_win = max((t.get("net_pnl", 0) for t in winning_trades), default=0.0)
        largest_loss = min((t.get("net_pnl", 0) for t in losing_trades), default=0.0)
        
        profit_factor = total_wins / total_losses if total_losses > 0 else 0.0
        
        # Equity curve and drawdown
        equity = initial_capital
        equity_curve = [equity]
        peak = initial_capital
        max_drawdown = 0.0
        
        for trade in sorted(trades, key=lambda t: t.get("close_time", 0)):
            equity += trade.get("net_pnl", 0)
            equity_curve.append(equity)
            
            if equity > peak:
                peak = equity
            
            drawdown = ((peak - equity) / peak * 100) if peak > 0 else 0.0
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Sharpe ratio (simplified)
        if len(equity_curve) > 1:
            returns = []
            for i in range(1, len(equity_curve)):
                prev_equity = equity_curve[i-1]
                curr_equity = equity_curve[i]
                if prev_equity > 0:
                    ret = (curr_equity - prev_equity) / prev_equity
                    returns.append(ret)
            
            if returns and len(returns) > 1:
                import numpy as np
                mean_return = np.mean(returns)
                std_return = np.std(returns)
                sharpe_ratio = (mean_return / std_return * np.sqrt(252)) if std_return > 0 else 0.0
            else:
                sharpe_ratio = 0.0
        else:
            sharpe_ratio = 0.0
        
        # Average hold time
        hold_times = [t.get("duration", 0) for t in trades if t.get("duration")]
        average_hold_time = sum(hold_times) / len(hold_times) if hold_times else 0.0
        
        return {
            "total_trades": total_trades,
            "winning_trades": win_count,
            "losing_trades": loss_count,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "total_return": total_return,
            "average_pnl": average_pnl,
            "profit_factor": profit_factor,
            "average_win": average_win,
            "average_loss": average_loss,
            "largest_win": largest_win,
            "largest_loss": largest_loss,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "average_hold_time": average_hold_time,
            "final_equity": equity_curve[-1] if equity_curve else initial_capital
        }
    
    @staticmethod
    def calculate_strategy_metrics(trades: List[Dict], strategy_field: str = "reason") -> Dict[str, Dict]:
        """
        Calculate metrics per strategy.
        
        Args:
            trades: List of trades
            strategy_field: Field to use for strategy identification
            
        Returns:
            Dictionary of strategy -> metrics
        """
        strategies = {}
        
        for trade in trades:
            strategy = trade.get(strategy_field, "Unknown")
            if strategy not in strategies:
                strategies[strategy] = []
            strategies[strategy].append(trade)
        
        result = {}
        for strategy, strategy_trades in strategies.items():
            # Calculate metrics for this strategy
            winning = [t for t in strategy_trades if t.get("net_pnl", 0) > 0]
            total_pnl = sum(t.get("net_pnl", 0) for t in strategy_trades)
            
            result[strategy] = {
                "total_trades": len(strategy_trades),
                "winning_trades": len(winning),
                "losing_trades": len(strategy_trades) - len(winning),
                "win_rate": (len(winning) / len(strategy_trades) * 100) if strategy_trades else 0.0,
                "total_pnl": total_pnl,
                "average_pnl": total_pnl / len(strategy_trades) if strategy_trades else 0.0
            }
        
        return result
    
    @staticmethod
    def calculate_daily_metrics(trades: List[Dict]) -> Dict[str, Dict]:
        """
        Calculate metrics per day.
        
        Args:
            trades: List of trades
            
        Returns:
            Dictionary of date -> metrics
        """
        daily_trades = {}
        
        for trade in trades:
            # Get date from timestamp
            timestamp = trade.get("timestamp") or trade.get("close_time", 0)
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        date = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).date()
                    else:
                        date = datetime.fromtimestamp(timestamp).date()
                    
                    date_str = date.isoformat()
                    if date_str not in daily_trades:
                        daily_trades[date_str] = []
                    daily_trades[date_str].append(trade)
                except Exception:
                    continue
        
        result = {}
        for date_str, day_trades in daily_trades.items():
            winning = [t for t in day_trades if t.get("net_pnl", 0) > 0]
            total_pnl = sum(t.get("net_pnl", 0) for t in day_trades)
            
            result[date_str] = {
                "date": date_str,
                "total_trades": len(day_trades),
                "winning_trades": len(winning),
                "total_pnl": total_pnl,
                "win_rate": (len(winning) / len(day_trades) * 100) if day_trades else 0.0
            }
        
        return result

