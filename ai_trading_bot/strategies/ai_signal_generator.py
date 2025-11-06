"""
AI Signal Generator using OpenRouter API (DeepSeek model).
PRIMARY strategy for signal generation.
"""
from typing import Dict, Optional, Any
from .base_strategy import BaseStrategy
from ..utils.openrouter_client import OpenRouterClient
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AISignalGenerator(BaseStrategy):
    """AI-powered signal generator using OpenRouter API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://openrouter.ai/api/v1",
                 default_model: str = "deepseek/deepseek-chat", timeout: float = 30.0,
                 min_confidence: float = 0.6):
        """
        Initialize AI signal generator.
        
        Args:
            api_key: OpenRouter API key
            base_url: OpenRouter base URL
            default_model: Model to use
            timeout: Request timeout
            min_confidence: Minimum confidence threshold
        """
        super().__init__("AI Signal Generator", min_confidence)
        self.client = OpenRouterClient(api_key, base_url, default_model, timeout)
    
    def generate_signal(self, market_data: Dict[str, Any], symbol: str) -> Optional[Dict[str, Any]]:
        """
        Generate AI trading signal.
        
        Args:
            market_data: Market data dictionary with indicators
            symbol: Trading symbol
            
        Returns:
            Signal dictionary or None if generation fails
        """
        try:
            # Generate signal using AI
            signal = self.client.generate_signal(market_data, symbol)
            
            if signal:
                # Validate signal
                validated_signal = self.validate_signal(signal)
                if validated_signal:
                    logger.info(f"AI signal generated for {symbol}: {validated_signal['action']} @ {validated_signal['entry_price']}")
                    return validated_signal
                else:
                    logger.debug(f"AI signal for {symbol} did not pass validation")
                    return None
            else:
                logger.debug(f"AI signal generation failed for {symbol}")
                return None
                
        except Exception as e:
            logger.error(f"Error in AI signal generation for {symbol}: {e}", exc_info=True)
            return None

