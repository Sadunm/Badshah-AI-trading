"""
Base strategy class for all trading strategies.
"""
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies."""
    
    def __init__(self, name: str, min_confidence: float = 0.6):
        """
        Initialize strategy.
        
        Args:
            name: Strategy name
            min_confidence: Minimum confidence threshold
        """
        self.name = name
        self.min_confidence = min_confidence
        self.enabled = True
    
    @abstractmethod
    def generate_signal(self, market_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
        """
        Generate trading signal.
        
        Args:
            market_data: Market data dictionary with indicators
            symbol: Trading symbol
            
        Returns:
            Signal dictionary with:
                - action: "LONG", "SHORT", or "FLAT"
                - confidence: 0.0-1.0
                - entry_price: Entry price
                - stop_loss: Stop loss price
                - take_profit: Take profit price
                - reason: Signal reason
            Returns None if no signal
        """
        pass
    
    def validate_signal(self, signal: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Validate signal before returning.
        
        Args:
            signal: Signal dictionary
            
        Returns:
            Validated signal or None if invalid
        """
        if signal is None:
            return None
        
        if not self.enabled:
            return None
        
        # Check confidence threshold
        confidence = signal.get("confidence", 0.0)
        if confidence < self.min_confidence:
            return None
        
        # Validate action
        action = signal.get("action", "FLAT")
        if action not in ["LONG", "SHORT", "FLAT"]:
            return None
        
        # Validate prices
        entry_price = signal.get("entry_price", 0)
        stop_loss = signal.get("stop_loss", 0)
        take_profit = signal.get("take_profit", 0)
        
        if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
            return None
        
        # For LONG: stop_loss < entry_price < take_profit
        # For SHORT: stop_loss > entry_price > take_profit
        if action == "LONG":
            if not (stop_loss < entry_price < take_profit):
                return None
        elif action == "SHORT":
            if not (stop_loss > entry_price > take_profit):
                return None
        
        return signal

