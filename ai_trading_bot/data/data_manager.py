"""
Data manager for fetching and caching market data.
"""
import time
from typing import Dict, List, Optional
import requests
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DataManager:
    """Manages market data fetching and caching."""
    
    def __init__(self, rest_url: str, symbols: List[str], kline_interval: str = "5m", kline_limit: int = 200, exchange: str = "binance"):
        """
        Initialize data manager.
        
        Args:
            rest_url: REST API URL
            symbols: List of trading symbols
            kline_interval: Kline interval (e.g., "5m" for Binance, "5" for Bybit)
            kline_limit: Number of candles to fetch
            exchange: Exchange name ("binance" or "bybit")
        """
        self.rest_url = rest_url.rstrip("/")
        self.symbols = symbols
        self.kline_interval = kline_interval
        self.kline_limit = kline_limit
        self.exchange = exchange.lower()
        
        # Cache
        self.historical_data: Dict[str, List[Dict]] = {}
    
    def fetch_historical_data(self, symbol: str) -> List[Dict]:
        """
        Fetch historical kline data from REST API with validation.
        
        Args:
            symbol: Trading symbol
            
        Returns:
            List of candle dictionaries (validated)
        """
        if self.exchange == "bybit":
            return self._fetch_bybit_historical_data(symbol)
        else:
            return self._fetch_binance_historical_data(symbol)
    
    def _fetch_binance_historical_data(self, symbol: str) -> List[Dict]:
        """Fetch historical data from Binance."""
        try:
            url = f"{self.rest_url}/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": self.kline_interval,
                "limit": self.kline_limit
            }
            
            logger.info(f"Fetching Binance historical data for {symbol}...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                candles = []
                
                # Validate and parse candles
                for idx, item in enumerate(data):
                    try:
                        # Validate data structure
                        if not isinstance(item, list) or len(item) < 9:
                            logger.warning(f"Invalid candle data at index {idx} for {symbol}, skipping")
                            continue
                        
                        # Parse with validation
                        open_time = int(item[0])
                        close_time = int(item[6])
                        open_price = float(item[1])
                        high_price = float(item[2])
                        low_price = float(item[3])
                        close_price = float(item[4])
                        volume = float(item[5])
                        trades = int(item[8])
                        
                        # Validate price data
                        if not (open_price > 0 and high_price > 0 and low_price > 0 and close_price > 0):
                            logger.warning(f"Invalid price data at index {idx} for {symbol}, skipping")
                            continue
                        
                        # Validate OHLC logic
                        if not (low_price <= open_price <= high_price and 
                                low_price <= close_price <= high_price):
                            logger.warning(f"Invalid OHLC relationship at index {idx} for {symbol}, correcting")
                            low_price = min(open_price, close_price, low_price, high_price)
                            high_price = max(open_price, close_price, low_price, high_price)
                        
                        # Validate time
                        if close_time <= open_time:
                            logger.warning(f"Invalid time range at index {idx} for {symbol}, skipping")
                            continue
                        
                        candle = {
                            "open_time": open_time,
                            "close_time": close_time,
                            "open": open_price,
                            "high": high_price,
                            "low": low_price,
                            "close": close_price,
                            "volume": max(0.0, volume),
                            "trades": max(0, trades)
                        }
                        candles.append(candle)
                        
                    except (ValueError, TypeError, IndexError) as e:
                        logger.warning(f"Error parsing candle at index {idx} for {symbol}: {e}, skipping")
                        continue
                
                if candles:
                    self.historical_data[symbol] = candles
                    logger.info(f"Fetched {len(candles)} valid candles for {symbol}")
                else:
                    logger.warning(f"No valid candles fetched for {symbol}")
                
                return candles
            else:
                logger.error(f"Failed to fetch Binance historical data: {response.status_code} - {response.text[:200]}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching Binance historical data for {symbol}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching Binance historical data for {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching Binance historical data for {symbol}: {e}", exc_info=True)
            return []
    
    def _fetch_bybit_historical_data(self, symbol: str) -> List[Dict]:
        """Fetch historical data from Bybit."""
        try:
            # Convert interval format (e.g., "5m" -> "5")
            interval_map = {
                "1m": "1", "3m": "3", "5m": "5", "15m": "15", "30m": "30",
                "1h": "60", "2h": "120", "4h": "240", "6h": "360", "12h": "720",
                "1d": "D", "1w": "W", "1M": "M"
            }
            bybit_interval = interval_map.get(self.kline_interval, self.kline_interval.replace("m", "").replace("h", "").replace("d", "D"))
            
            url = f"{self.rest_url}/v5/market/kline"
            params = {
                "category": "spot",
                "symbol": symbol,
                "interval": bybit_interval,
                "limit": self.kline_limit
            }
            
            logger.info(f"Fetching Bybit historical data for {symbol}...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Bybit response format: {"retCode": 0, "retMsg": "OK", "result": {"list": [...], ...}}
                if data.get("retCode") != 0:
                    logger.error(f"Bybit API error: {data.get('retMsg', 'Unknown error')}")
                    return []
                
                result = data.get("result", {})
                kline_list = result.get("list", [])
                
                if not kline_list:
                    logger.warning(f"No kline data received from Bybit for {symbol}")
                    return []
                
                candles = []
                
                # Bybit kline format: [startTime, open, high, low, close, volume, turnover]
                for idx, item in enumerate(kline_list):
                    try:
                        if not isinstance(item, list) or len(item) < 7:
                            logger.warning(f"Invalid Bybit candle data at index {idx} for {symbol}, skipping")
                            continue
                        
                        # Parse Bybit format
                        # startTime might be float string, convert to float first then int
                        start_time = int(float(item[0]))
                        open_price = float(item[1])
                        high_price = float(item[2])
                        low_price = float(item[3])
                        close_price = float(item[4])
                        volume = float(item[5])
                        turnover = float(item[6])
                        
                        # Calculate close_time (approximate based on interval)
                        interval_ms = self._interval_to_ms(self.kline_interval)
                        close_time = start_time + interval_ms - 1
                        
                        # Validate price data
                        if not (open_price > 0 and high_price > 0 and low_price > 0 and close_price > 0):
                            logger.warning(f"Invalid price data at index {idx} for {symbol}, skipping")
                            continue
                        
                        # Validate OHLC logic
                        if not (low_price <= open_price <= high_price and 
                                low_price <= close_price <= high_price):
                            logger.warning(f"Invalid OHLC relationship at index {idx} for {symbol}, correcting")
                            low_price = min(open_price, close_price, low_price, high_price)
                            high_price = max(open_price, close_price, low_price, high_price)
                        
                        candle = {
                            "open_time": start_time,
                            "close_time": close_time,
                            "open": open_price,
                            "high": high_price,
                            "low": low_price,
                            "close": close_price,
                            "volume": max(0.0, volume),
                            "trades": 0  # Bybit doesn't provide trade count in this endpoint
                        }
                        candles.append(candle)
                        
                    except (ValueError, TypeError, IndexError) as e:
                        logger.warning(f"Error parsing Bybit candle at index {idx} for {symbol}: {e}, skipping")
                        continue
                
                # Bybit returns newest first, reverse to oldest first (like Binance)
                candles.reverse()
                
                if candles:
                    self.historical_data[symbol] = candles
                    logger.info(f"Fetched {len(candles)} valid candles for {symbol} from Bybit")
                else:
                    logger.warning(f"No valid candles fetched for {symbol} from Bybit")
                
                return candles
            else:
                logger.error(f"Failed to fetch Bybit historical data: {response.status_code} - {response.text[:200]}")
                return []
                
        except requests.exceptions.Timeout:
            logger.error(f"Timeout fetching Bybit historical data for {symbol}")
            return []
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching Bybit historical data for {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching Bybit historical data for {symbol}: {e}", exc_info=True)
            return []
    
    def _interval_to_ms(self, interval: str) -> int:
        """Convert interval string to milliseconds."""
        if interval.endswith("m"):
            minutes = int(interval[:-1])
            return minutes * 60 * 1000
        elif interval.endswith("h"):
            hours = int(interval[:-1])
            return hours * 60 * 60 * 1000
        elif interval.endswith("d"):
            days = int(interval[:-1])
            return days * 24 * 60 * 60 * 1000
        elif interval == "D":
            return 24 * 60 * 60 * 1000
        elif interval == "W":
            return 7 * 24 * 60 * 60 * 1000
        elif interval == "M":
            return 30 * 24 * 60 * 60 * 1000
        else:
            # Default to 5 minutes
            return 5 * 60 * 1000
    
    def fetch_all_historical_data(self) -> Dict[str, List[Dict]]:
        """Fetch historical data for all symbols."""
        result = {}
        for symbol in self.symbols:
            result[symbol] = self.fetch_historical_data(symbol)
            time.sleep(0.1)  # Rate limiting
        return result
    
    def get_historical_data(self, symbol: str) -> List[Dict]:
        """Get cached historical data."""
        return self.historical_data.get(symbol, [])
    
    def update_kline(self, symbol: str, candle: Dict) -> None:
        """Update kline cache with new candle (with validation)."""
        try:
            # Validate candle data
            required_keys = ["open_time", "close_time", "open", "high", "low", "close", "volume"]
            if not all(key in candle for key in required_keys):
                logger.warning(f"Invalid candle data for {symbol}, missing required keys")
                return
            
            # Validate prices
            if not (candle["open"] > 0 and candle["high"] > 0 and 
                    candle["low"] > 0 and candle["close"] > 0):
                logger.warning(f"Invalid price data in candle for {symbol}")
                return
            
            # Validate OHLC
            if not (candle["low"] <= candle["open"] <= candle["high"] and
                    candle["low"] <= candle["close"] <= candle["high"]):
                logger.warning(f"Invalid OHLC relationship in candle for {symbol}, correcting")
                candle["low"] = min(candle["open"], candle["close"], candle["low"], candle["high"])
                candle["high"] = max(candle["open"], candle["close"], candle["low"], candle["high"])
            
            if symbol not in self.historical_data:
                self.historical_data[symbol] = []
            
            candles = self.historical_data[symbol]
            
            # Check if this candle updates the last one
            if candles and candles[-1]["close_time"] == candle["close_time"]:
                candles[-1] = candle
            else:
                candles.append(candle)
                # Keep only last kline_limit candles
                if len(candles) > self.kline_limit:
                    candles.pop(0)
            
            self.historical_data[symbol] = candles
            
        except Exception as e:
            logger.error(f"Error updating kline for {symbol}: {e}", exc_info=True)

