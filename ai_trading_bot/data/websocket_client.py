"""
WebSocket client for real-time market data from Binance.
"""
import json
import time
import threading
from typing import Dict, Optional, Callable, List
import websocket
from ..utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketClient:
    """WebSocket client for Binance with auto-reconnection."""
    
    def __init__(self, websocket_url: str, symbols: List[str]):
        """
        Initialize WebSocket client.
        
        Args:
            websocket_url: WebSocket URL
            symbols: List of trading symbols
        """
        self.websocket_url = websocket_url
        self.symbols = symbols
        self.ws: Optional[websocket.WebSocketApp] = None
        self.is_connected = False
        self.is_running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 1.0  # Start with 1 second
        
        # Data cache
        self.price_cache: Dict[str, float] = {}
        self.orderbook_cache: Dict[str, Dict] = {}
        self.kline_cache: Dict[str, List[Dict]] = {}
        
        # Callbacks
        self.on_price_update: Optional[Callable] = None
        self.on_kline_update: Optional[Callable] = None
        
        # Threading
        self.ws_thread: Optional[threading.Thread] = None
        self._reconnect_timer: Optional[threading.Timer] = None
        self.lock = threading.Lock()
        self._reconnect_lock = threading.Lock()  # Lock for reconnection operations
    
    def start(self) -> bool:
        """Start WebSocket connection."""
        if self.is_running:
            logger.warning("WebSocket already running")
            return True
        
        self.is_running = True
        return self._connect()
    
    def stop(self) -> None:
        """Stop WebSocket connection."""
        self.is_running = False
        
        # Cancel reconnection timer if active
        if hasattr(self, '_reconnect_timer') and self._reconnect_timer:
            try:
                self._reconnect_timer.cancel()
            except Exception:
                pass
        
        # Close WebSocket
        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                logger.error(f"Error closing WebSocket: {e}")
        
        with self.lock:
            self.is_connected = False
    
    def _connect(self) -> bool:
        """Connect to WebSocket."""
        try:
            # Build streams
            streams = []
            for symbol in self.symbols:
                symbol_lower = symbol.lower()
                streams.append(f"{symbol_lower}@ticker")  # Price updates
                streams.append(f"{symbol_lower}@kline_5m")  # 5-minute candles
                streams.append(f"{symbol_lower}@depth10@100ms")  # Orderbook
            
            stream_url = f"{self.websocket_url}/stream?streams={'/'.join(streams)}"
            
            logger.info(f"Connecting to WebSocket: {stream_url[:100]}...")
            
            self.ws = websocket.WebSocketApp(
                stream_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # Start WebSocket in a separate thread
            self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            self.ws_thread.start()
            
            # Wait a bit for connection
            time.sleep(2)
            return self.is_connected
            
        except Exception as e:
            logger.error(f"Error connecting to WebSocket: {e}", exc_info=True)
            return False
    
    def _on_open(self, ws) -> None:
        """Handle WebSocket open."""
        logger.info("WebSocket connected")
        self.is_connected = True
        self.reconnect_attempts = 0
        self.reconnect_delay = 1.0
    
    def _on_message(self, ws, message: str) -> None:
        """Handle WebSocket message."""
        try:
            data = json.loads(message)
            
            if "stream" in data and "data" in data:
                stream = data["stream"]
                payload = data["data"]
                
                # Parse stream name
                if "@ticker" in stream:
                    self._handle_ticker(payload)
                elif "@kline" in stream:
                    self._handle_kline(payload)
                elif "@depth" in stream:
                    self._handle_orderbook(payload)
                    
        except Exception as e:
            logger.error(f"Error processing WebSocket message: {e}")
    
    def _handle_ticker(self, data: Dict) -> None:
        """Handle ticker data."""
        try:
            symbol = data.get("s", "")
            price = float(data.get("c", 0))  # Last price
            
            with self.lock:
                self.price_cache[symbol] = price
            
            if self.on_price_update:
                self.on_price_update(symbol, price)
                
        except Exception as e:
            logger.error(f"Error handling ticker: {e}")
    
    def _handle_kline(self, data: Dict) -> None:
        """Handle kline (candle) data."""
        try:
            kline = data.get("k", {})
            symbol = kline.get("s", "")
            is_closed = kline.get("x", False)  # Is candle closed
            
            if is_closed:
                candle = {
                    "open_time": kline.get("t", 0),
                    "close_time": kline.get("T", 0),
                    "open": float(kline.get("o", 0)),
                    "high": float(kline.get("h", 0)),
                    "low": float(kline.get("l", 0)),
                    "close": float(kline.get("c", 0)),
                    "volume": float(kline.get("v", 0)),
                    "trades": kline.get("n", 0)
                }
                
                with self.lock:
                    if symbol not in self.kline_cache:
                        self.kline_cache[symbol] = []
                    self.kline_cache[symbol].append(candle)
                    # Keep only last 200 candles
                    if len(self.kline_cache[symbol]) > 200:
                        self.kline_cache[symbol] = self.kline_cache[symbol][-200:]
                
                if self.on_kline_update:
                    self.on_kline_update(symbol, candle)
                    
        except Exception as e:
            logger.error(f"Error handling kline: {e}")
    
    def _handle_orderbook(self, data: Dict) -> None:
        """Handle orderbook data."""
        try:
            symbol = data.get("s", "")
            
            with self.lock:
                self.orderbook_cache[symbol] = data
                
        except Exception as e:
            logger.error(f"Error handling orderbook: {e}")
    
    def _on_error(self, ws, error) -> None:
        """Handle WebSocket error with improved logging."""
        error_msg = str(error) if error else "Unknown error"
        logger.error(f"WebSocket error: {error_msg}")
        self.is_connected = False
        
        # Don't reconnect immediately on error - let _on_close handle it
        # This prevents rapid reconnection loops
        
    def _on_close(self, ws, close_status_code, close_msg) -> None:
        """Handle WebSocket close with improved reconnection logic."""
        close_reason = f"code={close_status_code}, msg={close_msg}" if close_msg else f"code={close_status_code}"
        logger.warning(f"WebSocket closed: {close_reason}")
        self.is_connected = False
        
        # Auto-reconnect if running
        if self.is_running:
            # Small delay before attempting reconnect
            time.sleep(1)
            self._reconnect()
        else:
            logger.info("WebSocket closed - not reconnecting (not running)")
    
    def _reconnect(self) -> None:
        """Reconnect with exponential backoff and improved error handling."""
        if not self.is_running:
            logger.info("WebSocket not running, skipping reconnect")
            return
        
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached. Stopping reconnection.")
            self.is_running = False
            return
        
        self.reconnect_attempts += 1
        delay = min(self.reconnect_delay * (2 ** (self.reconnect_attempts - 1)), 60)
        
        logger.info(f"Reconnecting in {delay:.1f}s (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        # Wait with periodic checks if we should still reconnect
        elapsed = 0
        check_interval = min(5.0, delay / 2)
        while elapsed < delay and self.is_running:
            time.sleep(check_interval)
            elapsed += check_interval
        
        if not self.is_running:
            logger.info("Reconnection cancelled - WebSocket stopped")
            return
        
        # Reset connection state (thread-safe)
        with self.lock:
            self.is_connected = False
            if self.ws:
                try:
                    self.ws.close()
                except Exception:
                    pass
                self.ws = None
        
        # Attempt reconnection
        logger.info(f"Attempting reconnection (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        success = self._connect()
        
        if success and self.is_connected:
            # Reset delay and attempts on successful connection
            self.reconnect_delay = 1.0
            self.reconnect_attempts = 0
            logger.info("Reconnection successful")
        else:
            # Schedule next reconnection attempt in a separate thread (daemon)
            # Use a single reconnection thread to avoid thread leaks
            if self.is_running:
                if not hasattr(self, '_reconnect_timer') or not self._reconnect_timer.is_alive():
                    self._reconnect_timer = threading.Timer(delay, self._reconnect)
                    self._reconnect_timer.daemon = True
                    self._reconnect_timer.start()
                else:
                    # If reconnect timer already running, just wait
                    logger.debug("Reconnection timer already active, waiting...")
    
    def get_price(self, symbol: str) -> Optional[float]:
        """Get current price for symbol."""
        with self.lock:
            return self.price_cache.get(symbol)
    
    def get_orderbook(self, symbol: str) -> Optional[Dict]:
        """Get orderbook for symbol."""
        with self.lock:
            return self.orderbook_cache.get(symbol)
    
    def get_klines(self, symbol: str, limit: int = 200) -> List[Dict]:
        """Get klines for symbol."""
        with self.lock:
            return self.kline_cache.get(symbol, [])[-limit:]

