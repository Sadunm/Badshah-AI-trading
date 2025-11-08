"""
Meta AI Strategy - Risk filter using OpenRouter API.
Validates signals before execution.
"""
from typing import Dict, Optional, Any
from .base_strategy import BaseStrategy
from ..utils.openrouter_client import OpenRouterClient
from ..utils.logger import get_logger

logger = get_logger(__name__)


class MetaAIStrategy(BaseStrategy):
    """Meta AI strategy for risk validation."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://openrouter.ai/api/v1",
                 default_model: str = "deepseek/deepseek-chat", timeout: float = 30.0,
                 risk_check_enabled: bool = True):
        """
        Initialize meta AI strategy.
        
        Args:
            api_key: OpenRouter API key
            base_url: OpenRouter base URL
            default_model: Model to use
            timeout: Request timeout
            risk_check_enabled: Enable risk checking
        """
        super().__init__("Meta AI Strategy", min_confidence=0.5)
        self.client = OpenRouterClient(api_key, base_url, default_model, timeout)
        self.risk_check_enabled = risk_check_enabled
    
    def validate_signal_risk(self, signal: Dict[str, Any], market_data: Dict[str, Any], symbol: str) -> bool:
        """
        Validate signal risk using AI.
        
        Args:
            signal: Signal dictionary to validate
            market_data: Market data
            symbol: Trading symbol
            
        Returns:
            True if signal is approved, False if rejected
            Returns True (fail-open) if AI unavailable
        """
        if not self.risk_check_enabled:
            return True
        
        # Check if API key is available
        if not self.client.api_key:
            # Only log once to avoid spam
            if not hasattr(self, '_api_key_warning_logged'):
                logger.warning("Meta AI validation skipped - API key not available")
                self._api_key_warning_logged = True
            return True  # Fail-open
        
        # Check if client is permanently disabled (401 error)
        if hasattr(self.client, 'auth_error_permanent') and self.client.auth_error_permanent:
            # Already logged in openrouter_client, don't log again
            return True  # Fail-open
        
        try:
            # Create risk assessment prompt
            prompt = self._create_risk_prompt(signal, market_data, symbol)
            
            # Make API request (this will handle errors and logging internally)
            response = self.client._make_request(prompt)
            
            if response:
                # Parse response
                approved = self._parse_risk_response(response)
                if approved:
                    logger.info(f"Meta AI approved signal for {symbol}: {signal['action']}")
                else:
                    logger.warning(f"Meta AI rejected signal for {symbol}: {signal['action']}")
                return approved
            else:
                # Don't log warning if auth error is permanent (already logged)
                if not (hasattr(self.client, 'auth_error_permanent') and self.client.auth_error_permanent):
                    # Only log occasionally to avoid spam
                    if not hasattr(self, '_validation_failure_count'):
                        self._validation_failure_count = 0
                    self._validation_failure_count += 1
                    if self._validation_failure_count % 10 == 0:  # Log every 10th failure
                        logger.warning("Meta AI validation failed - approving signal (fail-open)")
                return True  # Fail-open
                
        except Exception as e:
            logger.error(f"Error in meta AI validation: {e}", exc_info=True)
            return True  # Fail-open
    
    def _create_risk_prompt(self, signal: Dict[str, Any], market_data: Dict[str, Any], symbol: str) -> str:
        """Create risk assessment prompt."""
        current_price = market_data.get("current_price", 0)
        volatility = market_data.get("volatility", 0.01)
        volume_ratio = market_data.get("volume_ratio", 1.0)
        
        action = signal.get("action", "FLAT")
        entry_price = signal.get("entry_price", current_price)
        stop_loss = signal.get("stop_loss", current_price)
        take_profit = signal.get("take_profit", current_price)
        confidence = signal.get("confidence", 0.5)
        
        # Calculate risk/reward
        if action == "LONG":
            risk = entry_price - stop_loss
            reward = take_profit - entry_price
        elif action == "SHORT":
            risk = stop_loss - entry_price
            reward = entry_price - take_profit
        else:
            risk = 0
            reward = 0
        
        risk_reward = reward / risk if risk > 0 else 0
        
        prompt = f"""Assess the risk of this trading signal for {symbol}:

Action: {action}
Entry Price: ${entry_price:.2f}
Stop Loss: ${stop_loss:.2f}
Take Profit: ${take_profit:.2f}
Confidence: {confidence:.2f}
Risk/Reward Ratio: {risk_reward:.2f}
Current Volatility: {volatility:.4f}
Volume Ratio: {volume_ratio:.2f}

Analyze the risk and respond with ONLY a JSON object:
{{
    "approved": true or false,
    "reason": "brief explanation"
}}

Respond with ONLY the JSON, no additional text."""
        return prompt
    
    def _parse_risk_response(self, response_text: str) -> bool:
        """Parse risk assessment response."""
        try:
            import json
            
            # Extract JSON from response
            response_text = response_text.strip()
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            
            # Parse JSON
            data = json.loads(response_text)
            approved = data.get("approved", True)  # Default to approved (fail-open)
            
            return bool(approved)
            
        except Exception as e:
            logger.error(f"Error parsing risk response: {e}")
            return True  # Fail-open
    
    def generate_signal(self, market_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
        """
        Meta AI strategy doesn't generate signals - it validates them.
        This method should not be called directly.
        """
        return None

