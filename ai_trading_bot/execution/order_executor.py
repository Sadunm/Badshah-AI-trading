"""
Order executor for paper trading and real trading.
"""
import random
from typing import Dict, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OrderExecutor:
    """Executes orders in paper trading or real trading mode."""
    
    def __init__(self, paper_trading: bool = True, slippage_pct: float = 0.001, 
                 exchange_config: Optional[Dict] = None):
        """
        Initialize order executor.
        
        Args:
            paper_trading: Paper trading mode (True = simulated, False = real)
            slippage_pct: Slippage percentage (0.1% default, only for paper trading)
            exchange_config: Exchange configuration with API credentials
        """
        self.paper_trading = paper_trading
        self.slippage_pct = slippage_pct
        self.exchange_config = exchange_config or {}
        self.rest_client = None
        
        # Initialize real trading client if not paper trading
        if not self.paper_trading:
            self._initialize_real_trading()
    
    def _initialize_real_trading(self) -> None:
        """Initialize real trading client based on exchange."""
        try:
            exchange_name = self.exchange_config.get("name", "").lower()
            api_key = self.exchange_config.get("api_key", "")
            api_secret = self.exchange_config.get("api_secret", "")
            rest_url = self.exchange_config.get("rest_url", "https://api.bybit.com")
            
            if not api_key or not api_secret:
                logger.error("API key or secret not provided for real trading")
                return
            
            if exchange_name == "bybit":
                try:
                    from ..data.bybit_rest_client import BybitRESTClient
                except ImportError:
                    from ai_trading_bot.data.bybit_rest_client import BybitRESTClient
                
                self.rest_client = BybitRESTClient(api_key, api_secret, rest_url)
                logger.info("Real trading initialized for Bybit")
            else:
                logger.warning(f"Real trading not yet implemented for {exchange_name}")
        except Exception as e:
            logger.error(f"Error initializing real trading: {e}", exc_info=True)
    
    def execute_order(self, symbol: str, action: str, size: float, 
                     entry_price: float, fallback_price: Optional[float] = None) -> Optional[Dict]:
        """
        Execute an order (paper trading or real trading).
        
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
            # Real trading
            if not self.paper_trading:
                return self._execute_real_order(symbol, action, size, entry_price, fallback_price)
            
            # Paper trading (simulated)
            
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
            
            # Calculate fees - Binance Spot Trading Fee: 0.1% per side (maker/taker)
            # This matches Binance exactly: 0.1% = 0.001
            fee_rate = 0.001  # 0.1% per side, matching Binance spot trading
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
    
    def _execute_real_order(self, symbol: str, action: str, size: float,
                           entry_price: float, fallback_price: Optional[float] = None) -> Optional[Dict]:
        """
        Execute a real order on exchange.
        
        Args:
            symbol: Trading symbol
            action: "LONG" or "SHORT"
            size: Position size
            entry_price: Desired entry price
            fallback_price: Fallback price if entry_price unavailable
            
        Returns:
            Execution dictionary or None if error
        """
        try:
            if not self.rest_client:
                logger.error("Real trading client not initialized")
                return None
            
            # Use fallback price if entry_price is invalid
            if entry_price <= 0:
                if fallback_price and fallback_price > 0:
                    entry_price = fallback_price
                    logger.warning(f"Using fallback price for {symbol}: ${entry_price:.2f}")
                else:
                    logger.error(f"Invalid entry price for {symbol}")
                    return None
            
            # Convert action to Bybit side
            side = "Buy" if action == "LONG" else "Sell"
            
            # Use Market order for real trading (more reliable)
            # Convert size to string (Bybit requires string)
            qty_str = f"{size:.8f}".rstrip("0").rstrip(".")
            
            # Place market order
            order_result = self.rest_client.place_order(
                symbol=symbol,
                side=side,
                order_type="Market",
                qty=qty_str
            )
            
            if not order_result:
                logger.error(f"Failed to place real order for {symbol}")
                return None
            
            # Get executed price from order result
            # Bybit market orders execute immediately, but we may need to query for fill price
            executed_price = entry_price  # Use entry price as approximation for market orders
            order_id = order_result.get("orderId", "")
            
            # Calculate fees (Bybit spot trading fee is typically 0.1%)
            fee_rate = 0.001
            fees = executed_price * size * fee_rate
            
            execution = {
                "symbol": symbol,
                "action": action,
                "size": size,
                "entry_price": entry_price,
                "executed_price": executed_price,
                "slippage": 0.0,  # Market orders, slippage is real
                "fees": fees,
                "total_cost": executed_price * size + fees,
                "order_id": order_id,
                "real_trading": True
            }
            
            logger.info(f"Order executed (REAL): {symbol} {action} {size:.6f} @ ${executed_price:.2f} (orderId: {order_id})")
            
            return execution
            
        except Exception as e:
            logger.error(f"Error executing real order: {e}", exc_info=True)
            return None
    
    def close_order(self, symbol: str, position: Dict, exit_price: float) -> Optional[Dict]:
        """
        Close an order (paper trading or real trading).
        
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
            
            # Real trading
            if not self.paper_trading:
                return self._close_real_order(symbol, position, exit_price)
            
            # Paper trading (simulated)
            slippage = random.uniform(-self.slippage_pct, self.slippage_pct)
            executed_price = exit_price * (1 + slippage)
            
            # Calculate fees - Binance Spot Trading Fee: 0.1% per side
            # This matches Binance exactly: 0.1% = 0.001 per side
            fee_rate = 0.001  # 0.1% per side, matching Binance spot trading
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
    
    def _close_real_order(self, symbol: str, position: Dict, exit_price: float) -> Optional[Dict]:
        """
        Close a real position on exchange.
        
        Args:
            symbol: Trading symbol
            position: Position dictionary
            exit_price: Desired exit price
            
        Returns:
            Execution dictionary or None if error
        """
        try:
            if not self.rest_client:
                logger.error("Real trading client not initialized")
                return None
            
            # Determine side (opposite of entry)
            action = position.get("action", "LONG")
            side = "Sell" if action == "LONG" else "Buy"
            size = position["size"]
            
            # Convert size to string
            qty_str = f"{size:.8f}".rstrip("0").rstrip(".")
            
            # Place market order to close
            order_result = self.rest_client.place_order(
                symbol=symbol,
                side=side,
                order_type="Market",
                qty=qty_str
            )
            
            if not order_result:
                logger.error(f"Failed to close real position for {symbol}")
                return None
            
            executed_price = exit_price  # Approximation for market orders
            order_id = order_result.get("orderId", "")
            
            # Calculate fees
            fee_rate = 0.001
            fees = executed_price * size * fee_rate
            
            execution = {
                "symbol": symbol,
                "action": "CLOSE",
                "size": size,
                "exit_price": exit_price,
                "executed_price": executed_price,
                "slippage": 0.0,
                "fees": fees,
                "total_cost": executed_price * size + fees,
                "order_id": order_id,
                "real_trading": True
            }
            
            logger.info(f"Order closed (REAL): {symbol} @ ${executed_price:.2f} (orderId: {order_id})")
            
            return execution
            
        except Exception as e:
            logger.error(f"Error closing real order: {e}", exc_info=True)
            return None

