"""
Breakout Strategy - ATR and volatility expansion based.
"""
from typing import Dict, Optional, Any
from .base_strategy import BaseStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BreakoutStrategy(BaseStrategy):
    """Breakout trading strategy."""
    
    def __init__(self, min_confidence: float = 0.7):
        """Initialize breakout strategy."""
        super().__init__("Breakout Strategy", min_confidence)
    
    def generate_signal(self, market_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
        """
        Generate breakout signal.
        
        Args:
            market_data: Market data with indicators
            symbol: Trading symbol
            
        Returns:
            Signal dictionary or None
        """
        try:
            current_price = market_data.get("current_price", 0)
            if current_price <= 0:
                return None
            
            # Get indicators
            bb_upper = market_data.get("bb_upper", current_price)
            bb_middle = market_data.get("bb_middle", current_price)
            bb_lower = market_data.get("bb_lower", current_price)
            bb_position = market_data.get("bb_position", 0.5)
            atr = market_data.get("atr", current_price * 0.01)
            volatility = market_data.get("volatility", 0.01)
            volume_ratio = market_data.get("volume_ratio", 1.0)
            momentum = market_data.get("momentum", 1.0)
            
            # Breakout signals
            long_signals = 0
            short_signals = 0
            
            # Upper breakout (with volume)
            if current_price > bb_upper * 1.001 and volume_ratio > 1.3:
                long_signals += 2  # Strong signal
            elif current_price > bb_middle * 1.005 and momentum > 1.01 and volume_ratio > 1.2:
                long_signals += 1
            
            # Lower breakout (with volume)
            if current_price < bb_lower * 0.999 and volume_ratio > 1.3:
                short_signals += 2  # Strong signal
            elif current_price < bb_middle * 0.995 and momentum < 0.99 and volume_ratio > 1.2:
                short_signals += 1
            
            # Volatility expansion confirmation
            if volatility > 0.02:  # High volatility
                if long_signals > 0:
                    long_signals += 1
                if short_signals > 0:
                    short_signals += 1
            
            # Calculate confidence
            if long_signals >= 2:
                confidence = min(0.9, 0.6 + (long_signals * 0.1))
                stop_loss = bb_upper  # Stop at breakout level
                take_profit = current_price + (atr * 4)
                
                return {
                    "action": "LONG",
                    "confidence": confidence,
                    "entry_price": current_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "reason": f"Breakout long: price={current_price:.2f}, bb_upper={bb_upper:.2f}, volume_ratio={volume_ratio:.2f}"
                }
            elif short_signals >= 2:
                confidence = min(0.9, 0.6 + (short_signals * 0.1))
                stop_loss = bb_lower  # Stop at breakout level
                take_profit = current_price - (atr * 4)
                
                return {
                    "action": "SHORT",
                    "confidence": confidence,
                    "entry_price": current_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "reason": f"Breakout short: price={current_price:.2f}, bb_lower={bb_lower:.2f}, volume_ratio={volume_ratio:.2f}"
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error in breakout strategy for {symbol}: {e}", exc_info=True)
            return None

