"""
Momentum Strategy - LightGBM-based momentum trading.
"""
from typing import Dict, Optional, Any
from .base_strategy import BaseStrategy
from ..features.indicators import safe_get_last
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MomentumStrategy(BaseStrategy):
    """Momentum-based trading strategy."""
    
    def __init__(self, min_confidence: float = 0.6):
        """Initialize momentum strategy."""
        super().__init__("Momentum Strategy", min_confidence)
    
    def generate_signal(self, market_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
        """
        Generate momentum signal.
        
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
            rsi_7 = market_data.get("rsi_7", 50)
            macd_signal = market_data.get("macd_signal", 0)
            macd_histogram = market_data.get("macd_histogram", 0)
            momentum = market_data.get("momentum", 1.0)
            volume_ratio = market_data.get("volume_ratio", 1.0)
            atr = market_data.get("atr", current_price * 0.01)
            
            # Momentum signals
            long_signals = 0
            short_signals = 0
            
            # RSI momentum
            if rsi_7 > 60 and rsi_14 > 55:
                long_signals += 1
            elif rsi_7 < 40 and rsi_14 < 45:
                short_signals += 1
            
            # MACD momentum
            if macd_signal > 0 and macd_histogram > 0:
                long_signals += 1
            elif macd_signal < 0 and macd_histogram < 0:
                short_signals += 1
            
            # Price momentum
            if momentum > 1.02:
                long_signals += 1
            elif momentum < 0.98:
                short_signals += 1
            
            # Volume confirmation
            volume_boost = 1.0
            if volume_ratio > 1.2:
                volume_boost = 1.2
            elif volume_ratio < 0.8:
                volume_boost = 0.8
            
            # Calculate confidence
            if long_signals >= 2:
                confidence = min(0.9, 0.5 + (long_signals * 0.15) * volume_boost)
                stop_loss = current_price - (atr * 2)
                take_profit = current_price + (atr * 3)
                
                return {
                    "action": "LONG",
                    "confidence": confidence,
                    "entry_price": current_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "reason": f"Momentum long: {long_signals} signals, volume_ratio={volume_ratio:.2f}"
                }
            elif short_signals >= 2:
                confidence = min(0.9, 0.5 + (short_signals * 0.15) * volume_boost)
                stop_loss = current_price + (atr * 2)
                take_profit = current_price - (atr * 3)
                
                return {
                    "action": "SHORT",
                    "confidence": confidence,
                    "entry_price": current_price,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                    "reason": f"Momentum short: {short_signals} signals, volume_ratio={volume_ratio:.2f}"
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error in momentum strategy for {symbol}: {e}", exc_info=True)
            return None

