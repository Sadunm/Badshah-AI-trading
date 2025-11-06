"""
Trend Following Strategy - Simplified TFT forecasting.
"""
from typing import Dict, Optional, Any
from .base_strategy import BaseStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TrendFollowingStrategy(BaseStrategy):
    """Trend following trading strategy."""
    
    def __init__(self, min_confidence: float = 0.75):
        """Initialize trend following strategy."""
        super().__init__("Trend Following Strategy", min_confidence)
    
    def generate_signal(self, market_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
        """
        Generate trend following signal.
        
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
            rsi_14 = market_data.get("rsi_14", 50)
            macd = market_data.get("macd", 0)
            macd_signal = market_data.get("macd_signal", 0)
            macd_histogram = market_data.get("macd_histogram", 0)
            bb_middle = market_data.get("bb_middle", current_price)
            momentum = market_data.get("momentum", 1.0)
            atr = market_data.get("atr", current_price * 0.01)
            
            # Trend signals
            long_signals = 0
            short_signals = 0
            
            # MACD trend
            if macd > macd_signal and macd_histogram > 0:
                long_signals += 2  # Strong trend
            elif macd < macd_signal and macd_histogram < 0:
                short_signals += 2  # Strong trend
            
            # Price above/below moving average
            if current_price > bb_middle * 1.002:
                long_signals += 1
            elif current_price < bb_middle * 0.998:
                short_signals += 1
            
            # Momentum trend
            if momentum > 1.01:
                long_signals += 1
            elif momentum < 0.99:
                short_signals += 1
            
            # RSI trend confirmation (not extreme)
            if 40 < rsi_14 < 70:
                if long_signals > 0:
                    long_signals += 1
                if short_signals > 0:
                    short_signals += 1
            
            # Calculate confidence (trend following requires stronger signals)
            if long_signals >= 3:
                confidence = min(0.9, 0.65 + (long_signals * 0.08))
                stop_loss = current_price - (atr * 2.5)
                take_profit = current_price + (atr * 5)
                
                return {
                    "action": "LONG",
                    "confidence": confidence,
                    "entry_price": current_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "reason": f"Trend following long: momentum={momentum:.4f}, macd={macd:.4f}"
                }
            elif short_signals >= 3:
                confidence = min(0.9, 0.65 + (short_signals * 0.08))
                stop_loss = current_price + (atr * 2.5)
                take_profit = current_price - (atr * 5)
                
                return {
                    "action": "SHORT",
                    "confidence": confidence,
                    "entry_price": current_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "reason": f"Trend following short: momentum={momentum:.4f}, macd={macd:.4f}"
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error in trend following strategy for {symbol}: {e}", exc_info=True)
            return None

