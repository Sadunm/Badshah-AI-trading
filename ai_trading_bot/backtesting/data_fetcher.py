"""
Data fetcher for backtesting - downloads historical data from Binance.
"""
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests
from ..utils.logger import get_logger

logger = get_logger(__name__)


class BacktestDataFetcher:
    """Fetches historical data for backtesting."""
    
    def __init__(self, rest_url: str = "https://testnet.binance.vision/api"):
        """
        Initialize data fetcher.
        
        Args:
            rest_url: Binance REST API URL
        """
        self.rest_url = rest_url.rstrip("/")
    
    def fetch_historical_data(self, symbol: str, interval: str = "5m", 
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None,
                            limit: int = 1000) -> List[Dict]:
        """
        Fetch historical kline data.
        
        Args:
            symbol: Trading symbol
            interval: Kline interval (1m, 5m, 1h, etc.)
            start_date: Start date (optional)
            end_date: End date (optional)
            limit: Maximum candles to fetch per request
            
        Returns:
            List of candle dictionaries
        """
        try:
            all_candles = []
            
            # If start_date is provided, fetch in chunks
            if start_date and end_date:
                current_start = start_date
                
                while current_start < end_date:
                    params = {
                        "symbol": symbol,
                        "interval": interval,
                        "limit": limit,
                        "startTime": int(current_start.timestamp() * 1000)
                    }
                    
                    url = f"{self.rest_url}/api/v3/klines"
                    logger.info(f"Fetching data for {symbol} from {current_start}...")
                    
                    response = requests.get(url, params=params, timeout=30)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if not data:
                            break
                        
                        candles = []
                        for item in data:
                            try:
                                candle_time = datetime.fromtimestamp(int(item[0]) / 1000)
                                
                                # Stop if we've passed end_date
                                if candle_time > end_date:
                                    break
                                
                                candle = {
                                    "open_time": int(item[0]),
                                    "close_time": int(item[6]),
                                    "open": float(item[1]),
                                    "high": float(item[2]),
                                    "low": float(item[3]),
                                    "close": float(item[4]),
                                    "volume": float(item[5]),
                                    "trades": int(item[8])
                                }
                                
                                # Validate
                                if (candle["open"] > 0 and candle["high"] > 0 and 
                                    candle["low"] > 0 and candle["close"] > 0):
                                    candles.append(candle)
                            except (ValueError, TypeError, IndexError) as e:
                                logger.warning(f"Error parsing candle: {e}")
                                continue
                        
                        if candles:
                            all_candles.extend(candles)
                            # Move to next period
                            last_time = datetime.fromtimestamp(candles[-1]["open_time"] / 1000)
                            current_start = last_time + timedelta(minutes=5)  # For 5m interval
                        else:
                            break
                        
                        # Rate limiting
                        time.sleep(0.5)
                    else:
                        logger.error(f"Failed to fetch data: {response.status_code}")
                        break
            else:
                # Fetch single batch
                params = {
                    "symbol": symbol,
                    "interval": interval,
                    "limit": limit
                }
                
                url = f"{self.rest_url}/api/v3/klines"
                logger.info(f"Fetching {limit} candles for {symbol}...")
                
                response = requests.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    for item in data:
                        try:
                            candle = {
                                "open_time": int(item[0]),
                                "close_time": int(item[6]),
                                "open": float(item[1]),
                                "high": float(item[2]),
                                "low": float(item[3]),
                                "close": float(item[4]),
                                "volume": float(item[5]),
                                "trades": int(item[8])
                            }
                            
                            # Validate
                            if (candle["open"] > 0 and candle["high"] > 0 and 
                                candle["low"] > 0 and candle["close"] > 0):
                                all_candles.append(candle)
                        except (ValueError, TypeError, IndexError) as e:
                            logger.warning(f"Error parsing candle: {e}")
                            continue
            
            logger.info(f"Fetched {len(all_candles)} candles for {symbol}")
            return all_candles
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching data for {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}", exc_info=True)
            return []

