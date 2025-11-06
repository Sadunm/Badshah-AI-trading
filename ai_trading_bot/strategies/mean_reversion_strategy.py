"""
Mean Reversion Strategy - Z-score and Bollinger Bands based.
"""
from typing import Dict, Optional, Any
from .base_strategy import BaseStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MeanReversionStrategy(BaseStrategy):
    """Mean reversion trading strategy."""
    
    def __init__(self, min_confidence: float = 0.65):
        """Initialize mean reversion strategy."""
        super().__init__("Mean Reversion Strategy", min_confidence)
    
    def generate_signal(self, market_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
        """
        Generate mean reversion signal.
        
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
            z_score = market_data.get("z_score", 0)
            bb_position = market_data.get("bb_position", 0.5)
            bb_upper = market_data.get("bb_upper", current_price)
            bb_middle = market_data.get("bb_middle", current_price)
            bb_lower = market_data.get("bb_lower", current_price)
            rsi_14 = market_data.get("rsi_14", 50)
            atr = market_data.get("atr", current_price * 0.01)
            
            # Mean reversion signals
            long_signals = 0
            short_signals = 0
            
            # Z-score mean reversion (oversold)
            if z_score < -1.5:
                long_signals += 1
            elif z_score > 1.5:
                short_signals += 1
            
            # Bollinger Bands mean reversion
            if bb_position < 0.2:  # Near lower band
                long_signals += 1
            elif bb_position > 0.8:  # Near upper band
                short_signals += 1
            
            # RSI oversold/overbought
            if rsi_14 < 30:
                long_signals += 1
            elif rsi_14 > 70:
                short_signals += 1
            
            # Calculate confidence
            if long_signals >= 2:
                confidence = min(0.85, 0.55 + (long_signals * 0.1))
                stop_loss = min(current_price - (atr * 2), bb_lower * 0.995)
                take_profit = bb_middle
                
                return {
                    "action": "LONG",
                    "confidence": confidence,
                    "entry_price": current_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "reason": f"Mean reversion long: z_score={z_score:.2f}, bb_position={bb_position:.2f}"
                }
            elif short_signals >= 2:
                confidence = min(0.85, 0.55 + (short_signals * 0.1))
                stop_loss = max(current_price + (atr * 2), bb_upper * 1.005)
                take_profit = bb_middle
                
                return {
                    "action": "SHORT",
                    "confidence": confidence,
                    "entry_price": current_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "reason": f"Mean reversion short: z_score={z_score:.2f}, bb_position={bb_position:.2f}"
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error in mean reversion strategy for {symbol}: {e}", exc_info=True)
            return None

