"""
WebSocket client for real-time market data from Bybit.
"""
import json
import time
import threading
from typing import Dict, Optional, Callable, List
import websocket
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BybitWebSocketClient:
    """WebSocket client for Bybit with auto-reconnection."""
    
    def __init__(self, websocket_url: str, symbols: List[str]):
        """
        Initialize Bybit WebSocket client.
        
        Args:
            websocket_url: WebSocket URL (e.g., "wss://stream.bybit.com/v5/public/spot")
            symbols: List of trading symbols (e.g., ["BTCUSDT", "ETHUSDT"])
        """
        self.websocket_url = websocket_url.rstrip("/")
        self.symbols = symbols
        self.ws: Optional[websocket.WebSocketApp] = None
        self.is_connected = False
        self.is_running = False
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.reconnect_delay = 1.0
        
        # Data cache
        self.price_cache: Dict[str, float] = {}
        self.orderbook_cache: Dict[str, Dict] = {}
        self.kline_cache: Dict[str, List[Dict]] = {}
        
        # Callbacks (compatible with WebSocketClient interface)
        self.on_price_update: Optional[Callable] = None
        self.on_kline_update: Optional[Callable] = None
        self.on_orderbook_update: Optional[Callable] = None
        
        # Threading
        self.ws_thread: Optional[threading.Thread] = None
        self.lock = threading.Lock()
    
    def start(self) -> bool:
        """Start WebSocket connection."""
        if self.is_running:
            logger.warning("Bybit WebSocket already running")
            return True
        
        self.is_running = True
        return self._connect()
    
    def stop(self) -> None:
        """Stop WebSocket connection."""
        self.is_running = False
        if self.ws:
            try:
                self.ws.close()
            except Exception as e:
                logger.error(f"Error closing Bybit WebSocket: {e}")
        self.is_connected = False
    
    def _connect(self) -> bool:
        """Connect to Bybit WebSocket."""
        try:
            logger.info(f"Connecting to Bybit WebSocket: {self.websocket_url}")
            
            self.ws = websocket.WebSocketApp(
                self.websocket_url,
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
            logger.error(f"Error connecting to Bybit WebSocket: {e}", exc_info=True)
            return False
    
    def _on_open(self, ws) -> None:
        """Handle WebSocket open and subscribe to topics."""
        logger.info("Bybit WebSocket connected")
        self.is_connected = True
        self.reconnect_attempts = 0
        self.reconnect_delay = 1.0
        
        # Subscribe to topics
        self._subscribe()
    
    def _subscribe(self) -> None:
        """Subscribe to Bybit WebSocket topics."""
        try:
            # Bybit v5 uses JSON-RPC format for subscriptions
            subscriptions = []
            
            for symbol in self.symbols:
                # Ticker subscription
                subscriptions.append({
                    "op": "subscribe",
                    "args": [f"tickers.{symbol}"]
                })
                
                # Kline subscription (5-minute candles)
                subscriptions.append({
                    "op": "subscribe",
                    "args": [f"kline.5.{symbol}"]
                })
                
                # Orderbook subscription
                subscriptions.append({
                    "op": "subscribe",
                    "args": [f"orderbook.50.{symbol}"]
                })
            
            # Send all subscriptions
            for sub in subscriptions:
                message = json.dumps(sub)
                if self.ws:
                    self.ws.send(message)
                    logger.debug(f"Subscribed to: {sub['args'][0]}")
                    time.sleep(0.1)  # Small delay between subscriptions
            
            logger.info(f"Subscribed to {len(subscriptions)} topics for {len(self.symbols)} symbols")
            
        except Exception as e:
            logger.error(f"Error subscribing to Bybit topics: {e}", exc_info=True)
    
    def _on_message(self, ws, message: str) -> None:
        """Handle WebSocket message."""
        try:
            data = json.loads(message)
            
            # Bybit v5 response format
            if "topic" in data and "data" in data:
                topic = data["topic"]
                payload = data["data"]
                
                # Parse topic type
                if topic.startswith("tickers."):
                    self._handle_ticker(topic, payload)
                elif topic.startswith("kline."):
                    self._handle_kline(topic, payload)
                elif topic.startswith("orderbook."):
                    self._handle_orderbook(topic, payload)
            
            # Handle subscription confirmation
            elif "success" in data:
                if data.get("success"):
                    logger.debug(f"Subscription confirmed: {data.get('ret_msg', '')}")
                else:
                    logger.warning(f"Subscription failed: {data.get('ret_msg', '')}")
                    
        except Exception as e:
            logger.error(f"Error processing Bybit WebSocket message: {e}")
    
    def _handle_ticker(self, topic: str, data: Dict) -> None:
        """Handle ticker data."""
        try:
            # Bybit ticker format: {"symbol": "BTCUSDT", "lastPrice": "45000.0", ...}
            if isinstance(data, list) and len(data) > 0:
                ticker = data[0]
            else:
                ticker = data
            
            symbol = ticker.get("symbol", "")
            price_str = ticker.get("lastPrice", "0")
            
            try:
                price = float(price_str)
            except (ValueError, TypeError):
                logger.warning(f"Invalid price in ticker: {price_str}")
                return
            
            if price <= 0:
                return
            
            with self.lock:
                self.price_cache[symbol] = price
            
            if self.on_price_update:
                self.on_price_update(symbol, price)
                
        except Exception as e:
            logger.error(f"Error handling Bybit ticker: {e}")
    
    def _handle_kline(self, topic: str, data: Dict) -> None:
        """Handle kline (candle) data."""
        try:
            # Bybit kline format: {"symbol": "BTCUSDT", "start": 1234567890, "open": "45000", ...}
            if isinstance(data, list) and len(data) > 0:
                kline = data[0]
            else:
                kline = data
            
            symbol = kline.get("symbol", "")
            confirm = kline.get("confirm", False)  # Is candle closed
            
            if confirm:  # Only process closed candles
                try:
                    candle = {
                        "open_time": int(kline.get("start", 0)),
                        "close_time": int(kline.get("end", 0)),
                        "open": float(kline.get("open", 0)),
                        "high": float(kline.get("high", 0)),
                        "low": float(kline.get("low", 0)),
                        "close": float(kline.get("close", 0)),
                        "volume": float(kline.get("volume", 0)),
                        "trades": int(kline.get("turnover", 0))
                    }
                    
                    # Validate candle data
                    if not (candle["open"] > 0 and candle["high"] > 0 and 
                           candle["low"] > 0 and candle["close"] > 0):
                        return
                    
                    with self.lock:
                        if symbol not in self.kline_cache:
                            self.kline_cache[symbol] = []
                        self.kline_cache[symbol].append(candle)
                        # Keep only last 200 candles
                        if len(self.kline_cache[symbol]) > 200:
                            self.kline_cache[symbol] = self.kline_cache[symbol][-200:]
                    
                    if self.on_kline_update:
                        self.on_kline_update(symbol, candle)
                        
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error parsing Bybit kline data: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling Bybit kline: {e}")
    
    def _handle_orderbook(self, topic: str, data: Dict) -> None:
        """Handle orderbook data."""
        try:
            if isinstance(data, list) and len(data) > 0:
                orderbook = data[0]
            else:
                orderbook = data
            
            symbol = orderbook.get("s", "")
            
            with self.lock:
                self.orderbook_cache[symbol] = orderbook
                
        except Exception as e:
            logger.error(f"Error handling Bybit orderbook: {e}")
    
    def _on_error(self, ws, error) -> None:
        """Handle WebSocket error."""
        error_msg = str(error) if error else "Unknown error"
        logger.error(f"Bybit WebSocket error: {error_msg}")
        self.is_connected = False
        
    def _on_close(self, ws, close_status_code, close_msg) -> None:
        """Handle WebSocket close with improved reconnection logic."""
        close_reason = f"code={close_status_code}, msg={close_msg}" if close_msg else f"code={close_status_code}"
        logger.warning(f"Bybit WebSocket closed: {close_reason}")
        self.is_connected = False
        
        # Auto-reconnect if running
        if self.is_running:
            time.sleep(1)
            self._reconnect()
        else:
            logger.info("Bybit WebSocket closed - not reconnecting (not running)")
    
    def _reconnect(self) -> None:
        """Reconnect with exponential backoff."""
        if not self.is_running:
            logger.info("Bybit WebSocket not running, skipping reconnect")
            return
        
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached. Stopping reconnection.")
            self.is_running = False
            return
        
        self.reconnect_attempts += 1
        delay = min(self.reconnect_delay * (2 ** (self.reconnect_attempts - 1)), 60)
        
        logger.info(f"Reconnecting to Bybit in {delay:.1f}s (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        
        # Wait with periodic checks
        elapsed = 0
        check_interval = min(5.0, delay / 2)
        while elapsed < delay and self.is_running:
            time.sleep(check_interval)
            elapsed += check_interval
        
        if not self.is_running:
            logger.info("Bybit reconnection cancelled - WebSocket stopped")
            return
        
        # Reset connection state
        self.is_connected = False
        if self.ws:
            try:
                self.ws.close()
            except Exception:
                pass
            self.ws = None
        
        # Attempt reconnection
        logger.info(f"Attempting Bybit reconnection (attempt {self.reconnect_attempts}/{self.max_reconnect_attempts})")
        success = self._connect()
        
        if success and self.is_connected:
            self.reconnect_delay = 1.0
            logger.info("Bybit reconnection successful")
        else:
            self.reconnect_delay = delay
            if self.is_running:
                threading.Timer(0.1, self._reconnect).start()
    
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

