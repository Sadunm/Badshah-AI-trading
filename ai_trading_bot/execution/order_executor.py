"""
Order executor for paper trading (simulated execution).
"""
import random
from typing import Dict, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OrderExecutor:
    """Executes orders in paper trading mode."""
    
    def __init__(self, paper_trading: bool = True, slippage_pct: float = 0.001):
        """
        Initialize order executor.
        
        Args:
            paper_trading: Paper trading mode
            slippage_pct: Slippage percentage (0.1% default)
        """
        self.paper_trading = paper_trading
        self.slippage_pct = slippage_pct
    
    def execute_order(self, symbol: str, action: str, size: float, 
                     entry_price: float, fallback_price: Optional[float] = None) -> Optional[Dict]:
        """
        Execute an order (paper trading).
        
        Args:
            symbol: Trading symbol
            action: "LONG" or "SHORT"
            size: Position size
            entry_price: Desired entry price
            fallback_price: Fallback price if entry_price unavailable
            
        Returns:
            Execution dictionary with executed_price, size, fees, etc.
        """
        try:
            if not self.paper_trading:
                logger.warning("Live trading not implemented - use paper trading")
                return None
            
            # Use fallback price if entry_price is invalid
            if entry_price <= 0:
                if fallback_price and fallback_price > 0:
                    entry_price = fallback_price
                    logger.warning(f"Using fallback price for {symbol}: ${entry_price:.2f}")
                else:
                    logger.error(f"Invalid entry price for {symbol}")
                    return None
            
            # Simulate slippage
            slippage = random.uniform(-self.slippage_pct, self.slippage_pct)
            executed_price = entry_price * (1 + slippage)
            
            # Calculate fees (0.1% per side)
            fee_rate = 0.001
            fees = executed_price * size * fee_rate
            
            execution = {
                "symbol": symbol,
                "action": action,
                "size": size,
                "entry_price": entry_price,
                "executed_price": executed_price,
                "slippage": slippage,
                "fees": fees,
                "total_cost": executed_price * size + fees
            }
            
            logger.info(f"Order executed (paper): {symbol} {action} {size:.6f} @ ${executed_price:.2f} (slippage: {slippage*100:.3f}%)")
            
            return execution
            
        except Exception as e:
            logger.error(f"Error executing order: {e}", exc_info=True)
            return None
    
    def close_order(self, symbol: str, position: Dict, exit_price: float) -> Optional[Dict]:
        """
        Close an order (paper trading).
        
        Args:
            symbol: Trading symbol
            position: Position dictionary
            exit_price: Desired exit price
            
        Returns:
            Execution dictionary with executed_price, etc.
        """
        try:
            if exit_price <= 0:
                logger.error(f"Invalid exit price for {symbol}")
                return None
            
            # Simulate slippage
            slippage = random.uniform(-self.slippage_pct, self.slippage_pct)
            executed_price = exit_price * (1 + slippage)
            
            # Calculate fees (0.1% per side)
            fee_rate = 0.001
            size = position["size"]
            fees = executed_price * size * fee_rate
            
            execution = {
                "symbol": symbol,
                "action": "CLOSE",
                "size": size,
                "exit_price": exit_price,
                "executed_price": executed_price,
                "slippage": slippage,
                "fees": fees,
                "total_cost": executed_price * size + fees
            }
            
            logger.info(f"Order closed (paper): {symbol} @ ${executed_price:.2f} (slippage: {slippage*100:.3f}%)")
            
            return execution
            
        except Exception as e:
            logger.error(f"Error closing order: {e}", exc_info=True)
            return None

