"""
Rate limiter for API calls to prevent exceeding exchange rate limits.
"""
import time
import threading
from collections import deque
from typing import Optional
from .logger import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """
    Rate limiter for API calls with thread-safe operations.
    Implements token bucket algorithm for smooth rate limiting.
    """
    
    def __init__(self, max_calls: int, time_window: float = 60.0):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed in time_window
            time_window: Time window in seconds (default: 60 seconds)
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.call_timestamps: deque = deque(maxlen=max_calls)
        self.lock = threading.Lock()
    
    def acquire(self, timeout: Optional[float] = None) -> bool:
        """
        Acquire permission to make an API call.
        
        Args:
            timeout: Maximum time to wait (None = wait indefinitely)
        
        Returns:
            True if permission granted, False if timeout
        """
        start_time = time.time()
        
        while True:
            with self.lock:
                current_time = time.time()
                
                # Remove old timestamps outside time window
                while self.call_timestamps and (current_time - self.call_timestamps[0]) > self.time_window:
                    self.call_timestamps.popleft()
                
                # Check if we can make a call
                if len(self.call_timestamps) < self.max_calls:
                    self.call_timestamps.append(current_time)
                    return True
            
            # Check timeout
            if timeout is not None:
                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    logger.warning(f"Rate limit timeout after {elapsed:.2f}s")
                    return False
            
            # Wait a bit before retrying
            time.sleep(0.1)
    
    def wait_if_needed(self) -> None:
        """
        Wait if needed to respect rate limits.
        Non-blocking if rate limit not exceeded.
        """
        with self.lock:
            current_time = time.time()
            
            # Remove old timestamps
            while self.call_timestamps and (current_time - self.call_timestamps[0]) > self.time_window:
                self.call_timestamps.popleft()
            
            # If at limit, wait until oldest call expires
            if len(self.call_timestamps) >= self.max_calls:
                oldest_time = self.call_timestamps[0]
                wait_time = self.time_window - (current_time - oldest_time) + 0.1  # Add small buffer
                if wait_time > 0:
                    logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                    time.sleep(wait_time)
            
            # Record this call
            self.call_timestamps.append(time.time())
    
    def get_remaining_calls(self) -> int:
        """
        Get number of remaining calls in current time window.
        
        Returns:
            Number of remaining calls
        """
        with self.lock:
            current_time = time.time()
            
            # Remove old timestamps
            while self.call_timestamps and (current_time - self.call_timestamps[0]) > self.time_window:
                self.call_timestamps.popleft()
            
            return max(0, self.max_calls - len(self.call_timestamps))
    
    def reset(self) -> None:
        """Reset rate limiter (clear all timestamps)."""
        with self.lock:
            self.call_timestamps.clear()


# Global rate limiters for different exchanges
# Binance: 1200 requests per minute (20 per second)
# Bybit: 120 requests per minute (2 per second)
# We use conservative limits to stay safe

BINANCE_RATE_LIMITER = RateLimiter(max_calls=1000, time_window=60.0)  # 1000 calls per minute
BYBIT_RATE_LIMITER = RateLimiter(max_calls=100, time_window=60.0)  # 100 calls per minute

