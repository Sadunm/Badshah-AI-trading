"""
Risk manager for enforcing risk limits and tracking trades.
"""
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RiskManager:
    """Manages risk limits and trade tracking."""
    
    def __init__(self, initial_capital: float, max_drawdown_pct: float = 5.0,
                 max_daily_loss_pct: float = 2.0, max_daily_trades: int = 100):
        """
        Initialize risk manager.
        
        Args:
            initial_capital: Initial capital
            max_drawdown_pct: Maximum drawdown percentage
            max_daily_loss_pct: Maximum daily loss percentage
            max_daily_trades: Maximum trades per day
        """
        self.initial_capital = initial_capital
        self.max_drawdown_pct = max_drawdown_pct
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_daily_trades = max_daily_trades
        
        # State tracking
        self.current_capital = initial_capital
        self.peak_capital = initial_capital
        self.open_positions: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        
        # Daily tracking (use UTC for consistency)
        self.daily_start_time = datetime.now(timezone.utc)
        self.daily_trades = 0
        self.daily_pnl = 0.0
        
        # Fees
        self.fee_rate = 0.001  # 0.1% per side
    
    def can_open_position(self) -> bool:
        """
        Check if a new position can be opened.
        
        Returns:
            True if position can be opened
        """
        try:
            # Check drawdown
            if self.peak_capital <= 0:
                logger.warning("Invalid peak capital")
                return False
            
            drawdown_pct = ((self.peak_capital - self.current_capital) / self.peak_capital) * 100
            if drawdown_pct >= self.max_drawdown_pct:
                logger.warning(f"Max drawdown reached: {drawdown_pct:.2f}% >= {self.max_drawdown_pct}%")
                return False
            
            # Check daily loss
            if self.daily_pnl < 0 and self.initial_capital > 0:
                daily_loss_pct = abs(self.daily_pnl / self.initial_capital) * 100
                if daily_loss_pct >= self.max_daily_loss_pct:
                    logger.warning(f"Max daily loss reached: {daily_loss_pct:.2f}% >= {self.max_daily_loss_pct}%")
                    return False
            
            # Check daily trades
            if self.daily_trades >= self.max_daily_trades:
                logger.warning(f"Max daily trades reached: {self.daily_trades} >= {self.max_daily_trades}")
                return False
            
            # Reset daily counters if new day (use UTC timezone)
            now = datetime.now(timezone.utc)
            # Check if it's a new day (UTC)
            if (now.date() > self.daily_start_time.date()):
                self.daily_start_time = now
                self.daily_trades = 0
                self.daily_pnl = 0.0
                logger.info(f"Daily counters reset (UTC date: {now.date()})")
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking if position can be opened: {e}", exc_info=True)
            return False
    
    def open_position(self, symbol: str, position: Dict) -> bool:
        """
        Record an open position.
        
        Args:
            symbol: Trading symbol
            position: Position dictionary with action, size, entry_price, etc.
            
        Returns:
            True if position opened successfully
        """
        try:
            if not self.can_open_position():
                return False
            
            if symbol in self.open_positions:
                logger.warning(f"Position already exists for {symbol}")
                return False
            
            position["open_time"] = time.time()
            self.open_positions[symbol] = position
            self.daily_trades += 1
            
            logger.info(f"Position opened: {symbol} {position['action']} {position['size']:.6f} @ ${position['entry_price']:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"Error opening position: {e}", exc_info=True)
            return False
    
    def close_position(self, symbol: str, exit_price: float, reason: str = "Manual") -> Optional[Dict]:
        """
        Close a position and calculate P&L.
        
        Args:
            symbol: Trading symbol
            exit_price: Exit price
            reason: Reason for closing
            
        Returns:
            Trade record dictionary or None if position not found
        """
        try:
            if symbol not in self.open_positions:
                logger.warning(f"No open position found for {symbol}")
                return None
            
            position = self.open_positions.pop(symbol)
            
            # Calculate P&L
            action = position["action"]
            size = position["size"]
            entry_price = position["entry_price"]
            
            # Gross P&L
            if action == "LONG":
                gross_pnl = (exit_price - entry_price) * size
            elif action == "SHORT":
                gross_pnl = (entry_price - exit_price) * size
            else:
                gross_pnl = 0.0
            
            # Fees (0.1% each side)
            entry_fee = entry_price * size * self.fee_rate
            exit_fee = exit_price * size * self.fee_rate
            total_fees = entry_fee + exit_fee
            
            # Net P&L
            net_pnl = gross_pnl - total_fees
            
            # Update capital
            self.current_capital += net_pnl
            if self.current_capital > self.peak_capital:
                self.peak_capital = self.current_capital
            
            # Update daily P&L
            self.daily_pnl += net_pnl
            
            # Create trade record
            trade = {
                "symbol": symbol,
                "action": action,
                "size": size,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "gross_pnl": gross_pnl,
                "fees": total_fees,
                "net_pnl": net_pnl,
                "open_time": position["open_time"],
                "close_time": time.time(),
                "duration": time.time() - position["open_time"],
                "reason": reason
            }
            
            self.trade_history.append(trade)
            
            logger.info(f"Position closed: {symbol} {action} @ ${exit_price:.2f}, P&L: ${net_pnl:.2f} ({reason})")
            
            return trade
            
        except Exception as e:
            logger.error(f"Error closing position: {e}", exc_info=True)
            return None
    
    def check_stop_loss_take_profit(self, symbol: str, current_price: float) -> Optional[str]:
        """
        Check if stop loss or take profit should be triggered.
        
        Args:
            symbol: Trading symbol
            current_price: Current market price
            
        Returns:
            "stop_loss" or "take_profit" if triggered, None otherwise
        """
        try:
            if symbol not in self.open_positions:
                return None
            
            position = self.open_positions[symbol]
            action = position["action"]
            stop_loss = position.get("stop_loss", 0)
            take_profit = position.get("take_profit", 0)
            
            if action == "LONG":
                if current_price <= stop_loss:
                    return "stop_loss"
                if current_price >= take_profit:
                    return "take_profit"
            elif action == "SHORT":
                if current_price >= stop_loss:
                    return "stop_loss"
                if current_price <= take_profit:
                    return "take_profit"
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking stop loss/take profit: {e}", exc_info=True)
            return None
    
    def get_open_positions(self) -> Dict[str, Dict]:
        """Get all open positions."""
        return self.open_positions.copy()
    
    def get_trade_history(self) -> List[Dict]:
        """Get trade history."""
        return self.trade_history.copy()
    
    def get_current_capital(self) -> float:
        """Get current capital."""
        return self.current_capital
    
    def get_total_pnl(self) -> float:
        """Get total P&L."""
        return self.current_capital - self.initial_capital
    
    def get_drawdown_pct(self) -> float:
        """Get current drawdown percentage."""
        if self.peak_capital == 0:
            return 0.0
        return ((self.peak_capital - self.current_capital) / self.peak_capital) * 100

