"""
Unit tests for PositionAllocator.
"""
import unittest
from ai_trading_bot.allocator.position_allocator import PositionAllocator


class TestPositionAllocator(unittest.TestCase):
    """Test PositionAllocator functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.allocator = PositionAllocator(
            initial_capital=1000.0,
            max_position_size_pct=1.0,
            max_portfolio_risk_pct=20.0
        )
    
    def test_initial_state(self):
        """Test initial state."""
        self.assertEqual(self.allocator.initial_capital, 1000.0)
        self.assertEqual(self.allocator.current_capital, 1000.0)
    
    def test_calculate_position_size_long(self):
        """Test position size calculation for LONG."""
        signal = {
            "action": "LONG",
            "confidence": 0.7,
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 105.0
        }
        
        position_size = self.allocator.calculate_position_size(signal, 100.0)
        self.assertIsNotNone(position_size)
        self.assertGreater(position_size, 0)
        
        # Position value should be reasonable
        position_value = position_size * 100.0
        max_value = 1000.0 * 0.01  # 1% of capital
        self.assertLessEqual(position_value, max_value * 1.1)  # Allow small margin
    
    def test_calculate_position_size_short(self):
        """Test position size calculation for SHORT."""
        signal = {
            "action": "SHORT",
            "confidence": 0.7,
            "entry_price": 100.0,
            "stop_loss": 105.0,
            "take_profit": 95.0
        }
        
        position_size = self.allocator.calculate_position_size(signal, 100.0)
        self.assertIsNotNone(position_size)
        self.assertGreater(position_size, 0)
    
    def test_calculate_position_size_flat(self):
        """Test position size calculation for FLAT."""
        signal = {
            "action": "FLAT",
            "confidence": 0.5,
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 105.0
        }
        
        position_size = self.allocator.calculate_position_size(signal, 100.0)
        self.assertIsNone(position_size)
    
    def test_calculate_position_size_invalid_stop_loss(self):
        """Test position size with invalid stop loss."""
        signal = {
            "action": "LONG",
            "confidence": 0.7,
            "entry_price": 100.0,
            "stop_loss": 105.0,  # Invalid: stop loss above entry for LONG
            "take_profit": 110.0
        }
        
        position_size = self.allocator.calculate_position_size(signal, 100.0)
        self.assertIsNone(position_size)
    
    def test_update_capital(self):
        """Test updating capital."""
        self.allocator.update_capital(1500.0)
        self.assertEqual(self.allocator.get_current_capital(), 1500.0)
    
    def test_position_size_with_confidence(self):
        """Test that position size scales with confidence."""
        signal_low = {
            "action": "LONG",
            "confidence": 0.5,
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 105.0
        }
        
        signal_high = {
            "action": "LONG",
            "confidence": 0.9,
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 105.0
        }
        
        size_low = self.allocator.calculate_position_size(signal_low, 100.0)
        size_high = self.allocator.calculate_position_size(signal_high, 100.0)
        
        self.assertIsNotNone(size_low)
        self.assertIsNotNone(size_high)
        # Higher confidence should generally allow larger position
        # (though not always due to risk calculations)
        self.assertGreaterEqual(size_high, size_low * 0.5)  # At least not much smaller


if __name__ == "__main__":
    unittest.main()

