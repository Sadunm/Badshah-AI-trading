"""
Mock data provider for testing without real exchange connection.
Simulates market data for trading bot development.
"""
import time
import random
import threading
from typing import Dict, Callable, Optional, List
from datetime import datetime, timezone
import math

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MockDataProvider:
    """Mock data provider that simulates market data."""
    
    def __init__(self, symbols: List[str] = None, update_interval: float = 1.0):
        """
        Initialize mock data provider.
        
        Args:
            symbols: List of trading symbols (e.g., ['BTCUSDT', 'ETHUSDT'])
            update_interval: Time between updates in seconds
        """
        self.symbols = symbols or ['BTCUSDT', 'ETHUSDT', 'BNBUSDT']
        self.update_interval = update_interval
        self.is_running = False
        self.is_connected = False  # Compatibility with WebSocketClient interface
        self.thread = None
        self.callbacks = {
            'kline': [],
            'ticker': [],
            'depth': []
        }
        
        # Base prices for each symbol
        self.base_prices = {
            'BTCUSDT': 45000.0,
            'ETHUSDT': 2500.0,
            'BNBUSDT': 300.0,
            'SOLUSDT': 100.0,
            'XRPUSDT': 0.5,
            'ADAUSDT': 0.4,
            'DOGEUSDT': 0.08,
            'AVAXUSDT': 35.0,
            'LINKUSDT': 15.0,
            'MATICUSDT': 0.8
        }
        
        # Current prices (will fluctuate)
        self.current_prices = self.base_prices.copy()
        
        logger.info(f"Mock data provider initialized for symbols: {self.symbols}")
    
    def start(self) -> bool:
        """Start generating mock data."""
        if self.is_running:
            logger.warning("Mock data provider already running")
            return True
        
        self.is_running = True
        self.is_connected = True  # Mock provider is always "connected"
        self.thread = threading.Thread(target=self._generate_data, daemon=True)
        self.thread.start()
        logger.info("Mock data provider started")
        return True
    
    def stop(self):
        """Stop generating mock data."""
        self.is_running = False
        self.is_connected = False
        if self.thread:
            self.thread.join(timeout=2)
        logger.info("Mock data provider stopped")
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol (compatibility with WebSocketClient interface)."""
        return self.current_prices.get(symbol)
    
    def get_orderbook(self, symbol: str) -> Optional[Dict]:
        """Get orderbook for symbol (compatibility with WebSocketClient interface)."""
        # Return None for now - can be implemented if needed
        return None
    
    def get_klines(self, symbol: str, limit: int = 200) -> List[Dict]:
        """Get klines for symbol (compatibility with WebSocketClient interface)."""
        # Return empty list for now - can be implemented if needed
        return []
    
    def on_kline(self, callback: Callable):
        """Register callback for kline updates."""
        self.callbacks['kline'].append(callback)
    
    def on_ticker(self, callback: Callable):
        """Register callback for ticker updates."""
        self.callbacks['ticker'].append(callback)
    
    def on_depth(self, callback: Callable):
        """Register callback for depth updates."""
        self.callbacks['depth'].append(callback)
    
    def _generate_data(self):
        """Generate mock market data in a loop."""
        logger.info("Starting mock data generation")
        
        # Generate initial klines for all symbols
        for symbol in self.symbols:
            self._generate_kline(symbol)
            self._generate_ticker(symbol)
        
        # Continuous updates
        while self.is_running:
            try:
                for symbol in self.symbols:
                    # Update price with random walk
                    self._update_price(symbol)
                    
                    # Generate kline every 5 seconds (simulating 5m candles)
                    if int(time.time()) % 5 == 0:
                        self._generate_kline(symbol)
                    
                    # Generate ticker update
                    self._generate_ticker(symbol)
                    
                    # Generate depth update
                    self._generate_depth(symbol)
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                logger.error(f"Error generating mock data: {e}", exc_info=True)
                time.sleep(1)
    
    def _update_price(self, symbol: str):
        """Update price with random walk (simulates market movement)."""
        base = self.base_prices.get(symbol, 100.0)
        current = self.current_prices.get(symbol, base)
        
        # Random walk: ±0.1% change per update
        change_pct = random.uniform(-0.001, 0.001)
        new_price = current * (1 + change_pct)
        
        # Keep price within reasonable range (±20% of base)
        min_price = base * 0.8
        max_price = base * 1.2
        new_price = max(min_price, min(max_price, new_price))
        
        self.current_prices[symbol] = new_price
    
    def _generate_kline(self, symbol: str):
        """Generate mock kline (candle) data."""
        price = self.current_prices.get(symbol, self.base_prices.get(symbol, 100.0))
        
        # Generate OHLC with some variation
        open_price = price
        high_price = price * random.uniform(1.0, 1.005)
        low_price = price * random.uniform(0.995, 1.0)
        close_price = price * random.uniform(0.998, 1.002)
        volume = random.uniform(100, 1000)
        
        kline = {
            'symbol': symbol,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume,
            'timestamp': int(time.time() * 1000),
            'interval': '5m'
        }
        
        # Call all registered callbacks
        for callback in self.callbacks['kline']:
            try:
                callback(symbol, kline)
            except Exception as e:
                logger.error(f"Error in kline callback: {e}")
    
    def _generate_ticker(self, symbol: str):
        """Generate mock ticker data."""
        price = self.current_prices.get(symbol, self.base_prices.get(symbol, 100.0))
        
        ticker = {
            'symbol': symbol,
            'price': price,
            'timestamp': int(time.time() * 1000)
        }
        
        # Call all registered callbacks
        for callback in self.callbacks['ticker']:
            try:
                callback(symbol, price)
            except Exception as e:
                logger.error(f"Error in ticker callback: {e}")
    
    def _generate_depth(self, symbol: str):
        """Generate mock order book depth data."""
        price = self.current_prices.get(symbol, self.base_prices.get(symbol, 100.0))
        
        # Generate mock bids and asks
        bids = [[price * 0.999, random.uniform(0.1, 1.0)] for _ in range(10)]
        asks = [[price * 1.001, random.uniform(0.1, 1.0)] for _ in range(10)]
        
        depth = {
            'symbol': symbol,
            'bids': bids,
            'asks': asks,
            'timestamp': int(time.time() * 1000)
        }
        
        # Call all registered callbacks
        for callback in self.callbacks['depth']:
            try:
                callback(symbol, depth)
            except Exception as e:
                logger.error(f"Error in depth callback: {e}")

