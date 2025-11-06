"""
Unit tests for RiskManager.
"""
import unittest
from datetime import datetime, timezone, timedelta
from ai_trading_bot.risk.risk_manager import RiskManager


class TestRiskManager(unittest.TestCase):
    """Test RiskManager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.risk_manager = RiskManager(
            initial_capital=100.0,
            max_drawdown_pct=5.0,
            max_daily_loss_pct=2.0,
            max_daily_trades=10
        )
    
    def test_initial_state(self):
        """Test initial state of risk manager."""
        self.assertEqual(self.risk_manager.initial_capital, 100.0)
        self.assertEqual(self.risk_manager.current_capital, 100.0)
        self.assertEqual(self.risk_manager.peak_capital, 100.0)
        self.assertEqual(len(self.risk_manager.open_positions), 0)
        self.assertEqual(len(self.risk_manager.trade_history), 0)
    
    def test_can_open_position_initially(self):
        """Test that position can be opened initially."""
        self.assertTrue(self.risk_manager.can_open_position())
    
    def test_open_position(self):
        """Test opening a position."""
        position = {
            "action": "LONG",
            "size": 0.1,
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 105.0,
            "reason": "Test"
        }
        result = self.risk_manager.open_position("BTCUSDT", position)
        self.assertTrue(result)
        self.assertEqual(len(self.risk_manager.open_positions), 1)
        self.assertEqual(self.risk_manager.daily_trades, 1)
    
    def test_cannot_open_duplicate_position(self):
        """Test that duplicate positions cannot be opened."""
        position = {
            "action": "LONG",
            "size": 0.1,
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 105.0,
            "reason": "Test"
        }
        self.risk_manager.open_position("BTCUSDT", position)
        result = self.risk_manager.open_position("BTCUSDT", position)
        self.assertFalse(result)
    
    def test_close_position_long_profit(self):
        """Test closing a LONG position with profit."""
        position = {
            "action": "LONG",
            "size": 0.1,
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 105.0,
            "reason": "Test"
        }
        self.risk_manager.open_position("BTCUSDT", position)
        
        trade = self.risk_manager.close_position("BTCUSDT", 105.0, "Take profit")
        self.assertIsNotNone(trade)
        self.assertEqual(trade["action"], "LONG")
        self.assertEqual(trade["entry_price"], 100.0)
        self.assertEqual(trade["exit_price"], 105.0)
        self.assertGreater(trade["net_pnl"], 0)  # Should have profit
        self.assertEqual(len(self.risk_manager.open_positions), 0)
        self.assertEqual(len(self.risk_manager.trade_history), 1)
    
    def test_close_position_long_loss(self):
        """Test closing a LONG position with loss."""
        position = {
            "action": "LONG",
            "size": 0.1,
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 105.0,
            "reason": "Test"
        }
        self.risk_manager.open_position("BTCUSDT", position)
        
        trade = self.risk_manager.close_position("BTCUSDT", 95.0, "Stop loss")
        self.assertIsNotNone(trade)
        self.assertLess(trade["net_pnl"], 0)  # Should have loss
    
    def test_close_position_short(self):
        """Test closing a SHORT position."""
        position = {
            "action": "SHORT",
            "size": 0.1,
            "entry_price": 100.0,
            "stop_loss": 105.0,
            "take_profit": 95.0,
            "reason": "Test"
        }
        self.risk_manager.open_position("BTCUSDT", position)
        
        trade = self.risk_manager.close_position("BTCUSDT", 95.0, "Take profit")
        self.assertIsNotNone(trade)
        self.assertEqual(trade["action"], "SHORT")
        self.assertGreater(trade["net_pnl"], 0)  # Should have profit
    
    def test_stop_loss_take_profit_long(self):
        """Test stop loss and take profit triggers for LONG."""
        position = {
            "action": "LONG",
            "size": 0.1,
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 105.0,
            "reason": "Test"
        }
        self.risk_manager.open_position("BTCUSDT", position)
        
        # Test stop loss trigger
        trigger = self.risk_manager.check_stop_loss_take_profit("BTCUSDT", 94.0)
        self.assertEqual(trigger, "stop_loss")
        
        # Test take profit trigger
        trigger = self.risk_manager.check_stop_loss_take_profit("BTCUSDT", 106.0)
        self.assertEqual(trigger, "take_profit")
        
        # Test no trigger
        trigger = self.risk_manager.check_stop_loss_take_profit("BTCUSDT", 100.0)
        self.assertIsNone(trigger)
    
    def test_max_drawdown_limit(self):
        """Test max drawdown limit."""
        # Reduce capital to trigger drawdown
        self.risk_manager.current_capital = 94.0  # 6% drawdown
        self.risk_manager.peak_capital = 100.0
        
        # Should not be able to open position
        self.assertFalse(self.risk_manager.can_open_position())
    
    def test_max_daily_trades_limit(self):
        """Test max daily trades limit."""
        position = {
            "action": "LONG",
            "size": 0.01,
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 105.0,
            "reason": "Test"
        }
        
        # Open max trades
        for i in range(10):
            symbol = f"SYMBOL{i}"
            self.risk_manager.open_position(symbol, position)
            self.risk_manager.close_position(symbol, 100.0, "Test")
        
        # Should not be able to open more
        self.assertFalse(self.risk_manager.can_open_position())
    
    def test_get_current_capital(self):
        """Test getting current capital."""
        self.assertEqual(self.risk_manager.get_current_capital(), 100.0)
    
    def test_get_total_pnl(self):
        """Test getting total P&L."""
        position = {
            "action": "LONG",
            "size": 0.1,
            "entry_price": 100.0,
            "stop_loss": 95.0,
            "take_profit": 105.0,
            "reason": "Test"
        }
        self.risk_manager.open_position("BTCUSDT", position)
        self.risk_manager.close_position("BTCUSDT", 105.0, "Test")
        
        pnl = self.risk_manager.get_total_pnl()
        self.assertIsNotNone(pnl)


if __name__ == "__main__":
    unittest.main()

