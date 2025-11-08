"""
OpenRouter API client for AI signal generation with rate limiting and improved error handling.
"""
import os
import json
import time
from typing import Dict, Optional, Any
from collections import deque
import requests
from .logger import get_logger

logger = get_logger(__name__)


class OpenRouterClient:
    """Client for OpenRouter API with rate limiting."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://openrouter.ai/api/v1",
                 default_model: str = "deepseek/deepseek-chat", timeout: float = 30.0,
                 max_requests_per_minute: int = 10):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key (or from env var)
            base_url: OpenRouter base URL
            default_model: Default model to use
            timeout: Request timeout in seconds
            max_requests_per_minute: Maximum API requests per minute (rate limiting)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.timeout = timeout
        self.max_requests_per_minute = max_requests_per_minute
        
        # Rate limiting: track request timestamps
        self.request_timestamps: deque = deque(maxlen=max_requests_per_minute)
        self.last_request_time = 0.0
        
        # Error tracking
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        self.last_error_time = 0.0
        self.error_reset_interval = 300.0  # Reset errors after 5 minutes
        self.auth_error_permanent = False  # Permanent disable for 401 errors
        
        if not self.api_key:
            logger.warning("OPENROUTER_API_KEY not set - AI features will be disabled")
    
    def generate_signal(self, market_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
        """
        Generate trading signal using AI.
        
        Args:
            market_data: Market data dictionary with indicators
            symbol: Trading symbol
            
        Returns:
            Signal dictionary with action, confidence, prices, and reason
            Returns None if API call fails
        """
        if not self.api_key:
            # Only log once to avoid spam
            if not hasattr(self, '_api_key_warning_logged'):
                logger.warning("OpenRouter API key not available - AI signals will be disabled. Set OPENROUTER_API_KEY environment variable to enable AI features.")
                self._api_key_warning_logged = True
            return None
        
        # Check for permanent auth error (401)
        if self.auth_error_permanent:
            # Only log once per hour to avoid spam
            current_time = time.time()
            if not hasattr(self, '_auth_error_last_logged') or (current_time - self._auth_error_last_logged) > 3600:
                logger.warning("OpenRouter API authentication failed (401) - AI features permanently disabled. Please set a valid OPENROUTER_API_KEY.")
                self._auth_error_last_logged = current_time
            return None
        
        # Check if we should reset error counter (after some time)
        current_time = time.time()
        if self.consecutive_errors > 0 and (current_time - self.last_error_time) > self.error_reset_interval:
            logger.info(f"Resetting error counter after {self.error_reset_interval/60:.1f} minutes")
            self.consecutive_errors = 0
        
        # Check if we've exceeded error threshold
        if self.consecutive_errors >= self.max_consecutive_errors:
            logger.warning(f"Too many consecutive errors ({self.consecutive_errors}). Skipping AI call.")
            return None
        
        try:
            # Validate market data
            if not self._validate_market_data(market_data):
                logger.warning(f"Invalid market data for {symbol}, skipping AI signal")
                return None
            
            # Check rate limit
            if not self._check_rate_limit():
                logger.warning("Rate limit exceeded, skipping AI call")
                return None
            
            # Prepare prompt for AI
            prompt = self._create_prompt(market_data, symbol)
            
            # Make API request
            response = self._make_request(prompt)
            
            if response:
                # Parse response
                signal = self._parse_response(response, market_data)
                if signal:
                    # Reset error counter on success
                    self.consecutive_errors = 0
                    return signal
                else:
                    self.consecutive_errors += 1
                    self.last_error_time = time.time()
                    return None
            else:
                self.consecutive_errors += 1
                self.last_error_time = time.time()
                return None
                
        except Exception as e:
            self.consecutive_errors += 1
            self.last_error_time = time.time()
            logger.error(f"Error generating AI signal for {symbol}: {e}", exc_info=True)
            return None
    
    def _validate_market_data(self, market_data: Dict[str, Any]) -> bool:
        """Validate market data before sending to AI."""
        try:
            import math
            current_price = market_data.get("current_price", 0)
            if current_price <= 0:
                logger.warning("Invalid current_price in market data")
                return False
            
            # Check for NaN or infinite values
            for key, value in market_data.items():
                if isinstance(value, (int, float)):
                    # Check for NaN or infinite
                    if math.isnan(value) or math.isinf(value):
                        logger.warning(f"Invalid value in market_data[{key}]: {value}")
                        return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating market data: {e}")
            return False
    
    def _check_rate_limit(self) -> bool:
        """Check if we can make an API request (rate limiting)."""
        current_time = time.time()
        
        # Remove timestamps older than 1 minute
        while self.request_timestamps and (current_time - self.request_timestamps[0]) > 60:
            self.request_timestamps.popleft()
        
        # Check if we've exceeded the limit
        if len(self.request_timestamps) >= self.max_requests_per_minute:
            # Calculate wait time
            wait_time = 60 - (current_time - self.request_timestamps[0])
            if wait_time > 0:
                logger.warning(f"Rate limit exceeded. Wait {wait_time:.1f}s before next request")
                return False
        
        # Record this request
        self.request_timestamps.append(current_time)
        self.last_request_time = current_time
        return True
    
    def _create_prompt(self, market_data: Dict[str, Any], symbol: str) -> str:
        """Create prompt for AI analysis."""
        current_price = market_data.get("current_price", 0)
        rsi_14 = market_data.get("rsi_14", 50)
        rsi_7 = market_data.get("rsi_7", 50)
        macd_signal = market_data.get("macd_signal", 0)
        bb_position = market_data.get("bb_position", 0.5)
        volume_ratio = market_data.get("volume_ratio", 1.0)
        volatility = market_data.get("volatility", 0.01)
        
        prompt = f"""Analyze the following cryptocurrency market data for {symbol} and provide a trading signal.

Current Price: ${current_price}
RSI (14): {rsi_14:.2f}
RSI (7): {rsi_7:.2f}
MACD Signal: {macd_signal:.4f}
Bollinger Bands Position: {bb_position:.2f} (0=lower band, 1=upper band)
Volume Ratio: {volume_ratio:.2f}
Volatility: {volatility:.4f}

Provide your analysis in JSON format:
{{
    "action": "LONG" or "SHORT" or "FLAT",
    "confidence": 0.0-1.0,
    "entry_price": estimated entry price,
    "stop_loss": stop loss price,
    "take_profit": take profit price,
    "reason": "brief explanation"
}}

Respond with ONLY the JSON, no additional text."""
        return prompt
    
    def _make_request(self, prompt: str) -> Optional[str]:
        """Make API request to OpenRouter."""
        # Check if permanently disabled (401 error) - return early without logging
        if hasattr(self, 'auth_error_permanent') and self.auth_error_permanent:
            return None
        
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/ai-trading-bot",
                "X-Title": "AI Trading Bot"
            }
            
            payload = {
                "model": self.default_model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 500
            }
            
            start_time = time.time()
            response = requests.post(url, json=payload, headers=headers, timeout=self.timeout)
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                logger.info(f"OpenRouter API call successful ({elapsed:.2f}s)")
                return content
            elif response.status_code == 401:
                # Invalid API key - permanently disable
                if not self.auth_error_permanent:
                    logger.error(f"OpenRouter API authentication failed (401). Please check your OPENROUTER_API_KEY.")
                    logger.error(f"Response: {response.text[:200]}")
                    logger.error("AI features will be permanently disabled until a valid API key is set.")
                self.auth_error_permanent = True
                self.consecutive_errors = self.max_consecutive_errors
                self.last_error_time = time.time()
                return None
            else:
                logger.error(f"OpenRouter API error: {response.status_code} - {response.text[:200]}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error(f"OpenRouter API timeout after {self.timeout}s")
            return None
        except Exception as e:
            logger.error(f"OpenRouter API request failed: {e}", exc_info=True)
            return None
    
    def _parse_response(self, response_text: str, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse AI response into signal dictionary with improved error handling."""
        if not response_text or not response_text.strip():
            logger.warning("Empty response from AI")
            return None
        
        try:
            # Extract JSON from response
            response_text = response_text.strip()
            original_text = response_text
            
            # Try to find JSON in response (handle various formats)
            json_start = -1
            json_end = -1
            
            # Try ```json format
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
            # Try ``` format
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
            # Try { format (direct JSON)
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
            
            if json_start > 0 and json_end > json_start:
                response_text = response_text[json_start:json_end].strip()
            
            # Try to parse JSON
            try:
                data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to fix common JSON issues
                # Remove trailing commas
                response_text = response_text.rstrip().rstrip(',')
                # Try parsing again
                try:
                    data = json.loads(response_text)
                except json.JSONDecodeError:
                    logger.error(f"Failed to parse JSON. Response: {original_text[:200]}")
                    return None
            
            # Validate and extract signal
            action = str(data.get("action", "FLAT")).upper().strip()
            if action not in ["LONG", "SHORT", "FLAT"]:
                logger.warning(f"Invalid action '{action}', defaulting to FLAT")
                action = "FLAT"
            
            # Validate confidence
            try:
                confidence = float(data.get("confidence", 0.5))
                confidence = max(0.0, min(1.0, confidence))
            except (ValueError, TypeError):
                logger.warning("Invalid confidence value, defaulting to 0.5")
                confidence = 0.5
            
            # Validate prices
            current_price = float(market_data.get("current_price", 0))
            if current_price <= 0:
                logger.error("Invalid current_price in market_data")
                return None
            
            try:
                entry_price = float(data.get("entry_price", current_price))
                if entry_price <= 0:
                    entry_price = current_price
            except (ValueError, TypeError):
                entry_price = current_price
            
            try:
                stop_loss = float(data.get("stop_loss", current_price * 0.995))
                if stop_loss <= 0:
                    stop_loss = current_price * 0.995
            except (ValueError, TypeError):
                stop_loss = current_price * 0.995
            
            try:
                take_profit = float(data.get("take_profit", current_price * 1.01))
                if take_profit <= 0:
                    take_profit = current_price * 1.01
            except (ValueError, TypeError):
                take_profit = current_price * 1.01
            
            # Validate stop loss and take profit relative to entry
            if action == "LONG":
                if stop_loss >= entry_price:
                    stop_loss = entry_price * 0.995
                if take_profit <= entry_price:
                    take_profit = entry_price * 1.01
            elif action == "SHORT":
                if stop_loss <= entry_price:
                    stop_loss = entry_price * 1.005
                if take_profit >= entry_price:
                    take_profit = entry_price * 0.99
            
            reason = str(data.get("reason", "AI analysis")).strip()
            if not reason:
                reason = "AI analysis"
            
            signal = {
                "action": action,
                "confidence": confidence,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": reason
            }
            
            logger.info(f"AI signal generated: {action} @ ${entry_price:.2f} (confidence: {confidence:.2f}, SL: ${stop_loss:.2f}, TP: ${take_profit:.2f})")
            return signal
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}", exc_info=True)
            logger.debug(f"Response text (first 500 chars): {response_text[:500] if response_text else 'None'}")
            return None

