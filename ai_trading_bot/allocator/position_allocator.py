"""
Position allocator for calculating position sizes based on confidence and risk.
"""
from typing import Dict, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PositionAllocator:
    """Allocates position sizes based on confidence and risk parameters."""
    
    def __init__(self, initial_capital: float, max_position_size_pct: float = 1.0,
                 max_portfolio_risk_pct: float = 20.0):
        """
        Initialize position allocator.
        
        Args:
            initial_capital: Initial capital
            max_position_size_pct: Maximum position size as % of capital
            max_portfolio_risk_pct: Maximum portfolio risk as % of capital
        """
        self.initial_capital = initial_capital
        self.max_position_size_pct = max_position_size_pct
        self.max_portfolio_risk_pct = max_portfolio_risk_pct
        self.current_capital = initial_capital
    
    def calculate_position_size(self, signal: Dict, current_price: float) -> Optional[float]:
        """
        Calculate position size based on signal confidence and risk.
        
        Args:
            signal: Signal dictionary with action, confidence, entry_price, stop_loss
            current_price: Current market price
            
        Returns:
            Position size in base currency or None if invalid
        """
        try:
            action = signal.get("action", "FLAT")
            if action == "FLAT":
                return None
            
            confidence = signal.get("confidence", 0.5)
            entry_price = signal.get("entry_price", current_price)
            stop_loss = signal.get("stop_loss", current_price)
            
            # Calculate risk per unit
            if action == "LONG":
                risk_per_unit = entry_price - stop_loss
            elif action == "SHORT":
                risk_per_unit = stop_loss - entry_price
            else:
                return None
            
            if risk_per_unit <= 0:
                logger.warning("Invalid risk per unit - stop_loss too close to entry")
                return None
            
            # Calculate position size based on confidence
            # Base position size: 1% of capital per 0.1 confidence
            if confidence <= 0:
                confidence = 0.5  # Default confidence
            
            base_risk_pct = self.max_position_size_pct * (confidence / 0.5)
            base_risk_pct = min(base_risk_pct, self.max_position_size_pct)
            base_risk_pct = max(0.1, base_risk_pct)  # Minimum 0.1% risk
            
            # Risk amount
            if self.current_capital <= 0:
                logger.warning("Invalid current capital")
                return None
            
            risk_amount = self.current_capital * (base_risk_pct / 100.0)
            
            # Position size in units
            if risk_per_unit <= 0:
                logger.warning("Invalid risk per unit")
                return None
            
            position_size = risk_amount / risk_per_unit
            
            # Check maximum position size
            max_position_value = self.current_capital * (self.max_position_size_pct / 100.0)
            max_position_size = max_position_value / entry_price
            
            position_size = min(position_size, max_position_size)
            
            # Minimum position size check - adaptive based on capital
            position_value = position_size * entry_price
            
            # For small capital: use 50% of max position value as minimum (to allow some flexibility)
            # For $10 capital with 1% max: min = $0.05 (50% of $0.10)
            # For larger capital: use adaptive minimum
            if self.current_capital < 20:
                # Very small capital: minimum is 50% of max position value
                min_position_value = max_position_value * 0.5
                min_position_value = max(min_position_value, 0.05)  # Absolute minimum $0.05 for very small capital
            else:
                # Normal capital: adaptive minimum
                min_position_value = min(self.current_capital * 0.05, 0.5)
                min_position_value = max(min_position_value, 0.10)  # Absolute minimum $0.10
            
            # Add small tolerance for floating point comparison (0.1% tolerance)
            tolerance = min_position_value * 0.001
            if position_value < (min_position_value - tolerance):
                logger.debug(f"Position size too small: ${position_value:.6f} < ${min_position_value:.6f} (capital: ${self.current_capital:.2f}, max: ${max_position_value:.6f}) for {signal.get('action', 'UNKNOWN')}")
                return None
            
            # Ensure position size is reasonable (not too small due to rounding)
            if position_size < 0.000001:  # Very small position size
                logger.debug(f"Position size too small: {position_size:.8f} units")
                return None
            
            # Final validation: ensure position value is reasonable
            if position_value <= 0:
                logger.warning(f"Invalid position value: ${position_value:.6f}")
                return None
            
            logger.info(f"Position size calculated: {position_size:.8f} units @ ${entry_price:.6f} = ${position_value:.6f} (capital: ${self.current_capital:.2f}, max: ${max_position_value:.6f}, min: ${min_position_value:.6f})")
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}", exc_info=True)
            return None
    
    def update_capital(self, capital: float) -> None:
        """Update current capital."""
        self.current_capital = capital
    
    def get_current_capital(self) -> float:
        """Get current capital."""
        return self.current_capital

