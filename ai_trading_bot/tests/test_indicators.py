"""
Unit tests for technical indicators.
"""
import unittest
import numpy as np
from ai_trading_bot.features.indicators import (
    calculate_rsi,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    safe_get_last,
    safe_divide
)


class TestIndicators(unittest.TestCase):
    """Test technical indicator calculations."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Generate sample price data
        self.prices = [100 + i * 0.5 + np.random.uniform(-1, 1) for i in range(100)]
    
    def test_safe_get_last(self):
        """Test safe_get_last function."""
        arr = np.array([1, 2, 3, 4, 5])
        self.assertEqual(safe_get_last(arr), 5.0)
        
        # Test empty array
        arr = np.array([])
        self.assertEqual(safe_get_last(arr), 0.0)
        
        # Test NaN
        arr = np.array([1, 2, np.nan])
        self.assertEqual(safe_get_last(arr), 0.0)
    
    def test_safe_divide(self):
        """Test safe_divide function."""
        self.assertEqual(safe_divide(10, 2), 5.0)
        self.assertEqual(safe_divide(10, 0), 0.0)
        self.assertEqual(safe_divide(np.nan, 2), 0.0)
        self.assertEqual(safe_divide(10, np.inf), 0.0)
    
    def test_calculate_rsi(self):
        """Test RSI calculation."""
        rsi = calculate_rsi(self.prices, period=14)
        self.assertIsNotNone(rsi)
        self.assertIsInstance(rsi, np.ndarray)
        
        # RSI should be between 0 and 100
        last_rsi = safe_get_last(rsi)
        self.assertGreaterEqual(last_rsi, 0)
        self.assertLessEqual(last_rsi, 100)
        
        # Test with insufficient data
        rsi_short = calculate_rsi(self.prices[:10], period=14)
        self.assertIsNone(rsi_short)
    
    def test_calculate_macd(self):
        """Test MACD calculation."""
        macd_result = calculate_macd(self.prices)
        self.assertIsNotNone(macd_result)
        
        macd_line, signal_line, histogram = macd_result
        self.assertIsNotNone(macd_line)
        self.assertIsNotNone(signal_line)
        self.assertIsNotNone(histogram)
        
        # Test with insufficient data
        macd_short = calculate_macd(self.prices[:20])
        self.assertIsNone(macd_short)
    
    def test_calculate_bollinger_bands(self):
        """Test Bollinger Bands calculation."""
        bb_result = calculate_bollinger_bands(self.prices)
        self.assertIsNotNone(bb_result)
        
        upper, middle, lower = bb_result
        self.assertIsNotNone(upper)
        self.assertIsNotNone(middle)
        self.assertIsNotNone(lower)
        
        # Upper band should be above middle, middle above lower
        last_upper = safe_get_last(upper)
        last_middle = safe_get_last(middle)
        last_lower = safe_get_last(lower)
        
        self.assertGreater(last_upper, last_middle)
        self.assertGreater(last_middle, last_lower)
    
    def test_calculate_atr(self):
        """Test ATR calculation."""
        # Need high, low, close for ATR
        highs = [p + 1 for p in self.prices]
        lows = [p - 1 for p in self.prices]
        
        atr = calculate_atr(highs, lows, self.prices)
        self.assertIsNotNone(atr)
        
        last_atr = safe_get_last(atr)
        self.assertGreater(last_atr, 0)
        
        # Test with insufficient data
        atr_short = calculate_atr(highs[:10], lows[:10], self.prices[:10])
        self.assertIsNone(atr_short)


if __name__ == "__main__":
    unittest.main()

