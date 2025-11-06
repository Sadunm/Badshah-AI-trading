"""Configuration module"""
import os
import yaml
import re
from pathlib import Path
from typing import Dict, Any, Optional

# Import logger with fallback to avoid circular imports
try:
    from ..utils.logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file with environment variable substitution.
    
    Args:
        config_path: Path to config file (tries multiple fallbacks)
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        # Try multiple fallback paths (Windows and module import compatible)
        import os
        current_dir = Path(os.getcwd())
        script_dir = Path(__file__).parent.absolute()
        
        fallback_paths = [
            script_dir / "config.yaml",  # Relative to this file
            Path(__file__).parent / "config.yaml",  # Same as above, different method
            current_dir / "ai_trading_bot" / "config" / "config.yaml",  # From project root
            current_dir / "config" / "config.yaml",  # From current directory
            current_dir / "config.yaml",  # In current directory
            Path("ai_trading_bot/config/config.yaml"),  # Module path
            Path("config/config.yaml"),  # Relative path
            Path("config.yaml"),  # Current directory
        ]
    else:
        fallback_paths = [config_path]
    
    for path in fallback_paths:
        try:
            if path.exists():
                logger.info(f"Loading config from: {path}")
                with open(path, 'r', encoding='utf-8') as f:
                    config_str = f.read()
                
                # Substitute environment variables
                config_str = substitute_env_vars(config_str)
                
                # Parse YAML
                config = yaml.safe_load(config_str)
                
                # Validate required env vars
                validate_env_vars(config)
                
                # Validate config structure and values
                is_valid, errors = validate_config(config)
                if not is_valid:
                    logger.error(f"Configuration validation failed with {len(errors)} errors")
                    logger.warning("Continuing with default config due to validation errors")
                    # Return default config instead
                    return get_default_config()
                
                return config
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}")
            continue
    
    # Return default config if all paths fail
    logger.warning("Using default configuration")
    return get_default_config()


def substitute_env_vars(text: str) -> str:
    """
    Substitute environment variables in format ${VAR_NAME}.
    
    Args:
        text: Text with ${VAR} placeholders
        
    Returns:
        Text with substituted values
    """
    def replace_var(match):
        var_name = match.group(1)
        default = match.group(2) if match.lastindex > 1 else None
        value = os.getenv(var_name, default)
        if value is None:
            logger.warning(f"Environment variable {var_name} not set")
            return match.group(0)  # Return original if not found
        return value
    
    # Pattern: ${VAR} or ${VAR:default}
    pattern = r'\$\{([^}:]+)(?::([^}]+))?\}'
    return re.sub(pattern, replace_var, text)


def validate_env_vars(config: Dict[str, Any]) -> None:
    """Validate that required environment variables are set."""
    required_vars = []
    
    # Check OpenRouter API key
    openrouter_key = config.get("openrouter", {}).get("api_key", "")
    if "${OPENROUTER_API_KEY}" in openrouter_key or not openrouter_key:
        required_vars.append("OPENROUTER_API_KEY")
    
    # Check Binance API keys (optional for paper trading)
    exchange_key = config.get("exchange", {}).get("api_key", "")
    if "${BINANCE_API_KEY}" in exchange_key:
        logger.warning("BINANCE_API_KEY not set - some features may be limited")
    
    exchange_secret = config.get("exchange", {}).get("api_secret", "")
    if "${BINANCE_API_SECRET}" in exchange_secret:
        logger.warning("BINANCE_API_SECRET not set - some features may be limited")
    
    if required_vars:
        logger.warning(f"Required environment variables not set: {', '.join(required_vars)}")


def validate_config(config: Dict[str, Any]) -> tuple:
    """
    Validate configuration structure and values.
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    warnings = []
    
    # Validate OpenRouter config
    openrouter = config.get("openrouter", {})
    if not isinstance(openrouter, dict):
        errors.append("openrouter config must be a dictionary")
    else:
        if not openrouter.get("base_url", "").startswith(("http://", "https://")):
            errors.append("openrouter.base_url must be a valid URL")
        if openrouter.get("timeout", 0) <= 0:
            errors.append("openrouter.timeout must be positive")
        if not openrouter.get("default_model"):
            warnings.append("openrouter.default_model not set")
    
    # Validate Exchange config
    exchange = config.get("exchange", {})
    if not isinstance(exchange, dict):
        errors.append("exchange config must be a dictionary")
    else:
        if not exchange.get("websocket_url", "").startswith(("ws://", "wss://")):
            errors.append("exchange.websocket_url must be a valid WebSocket URL")
        if not exchange.get("rest_url", "").startswith(("http://", "https://")):
            errors.append("exchange.rest_url must be a valid URL")
    
    # Validate Trading config
    trading = config.get("trading", {})
    if not isinstance(trading, dict):
        errors.append("trading config must be a dictionary")
    else:
        initial_capital = trading.get("initial_capital", 0)
        if not isinstance(initial_capital, (int, float)) or initial_capital <= 0:
            errors.append("trading.initial_capital must be a positive number")
        
        max_position_pct = trading.get("max_position_size_pct", 0)
        if not isinstance(max_position_pct, (int, float)) or max_position_pct <= 0 or max_position_pct > 100:
            errors.append("trading.max_position_size_pct must be between 0 and 100")
        
        max_portfolio_risk = trading.get("max_portfolio_risk_pct", 0)
        if not isinstance(max_portfolio_risk, (int, float)) or max_portfolio_risk <= 0 or max_portfolio_risk > 100:
            errors.append("trading.max_portfolio_risk_pct must be between 0 and 100")
    
    # Validate Risk config
    risk = config.get("risk", {})
    if not isinstance(risk, dict):
        errors.append("risk config must be a dictionary")
    else:
        max_drawdown = risk.get("max_drawdown_pct", 0)
        if not isinstance(max_drawdown, (int, float)) or max_drawdown <= 0 or max_drawdown > 100:
            errors.append("risk.max_drawdown_pct must be between 0 and 100")
        
        max_daily_loss = risk.get("max_daily_loss_pct", 0)
        if not isinstance(max_daily_loss, (int, float)) or max_daily_loss <= 0 or max_daily_loss > 100:
            errors.append("risk.max_daily_loss_pct must be between 0 and 100")
        
        max_daily_trades = risk.get("max_daily_trades", 0)
        if not isinstance(max_daily_trades, int) or max_daily_trades <= 0:
            errors.append("risk.max_daily_trades must be a positive integer")
    
    # Validate Data config
    data = config.get("data", {})
    if not isinstance(data, dict):
        errors.append("data config must be a dictionary")
    else:
        symbols = data.get("symbols", [])
        if not isinstance(symbols, list) or len(symbols) == 0:
            errors.append("data.symbols must be a non-empty list")
        
        kline_interval = data.get("kline_interval", "")
        valid_intervals = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d"]
        if kline_interval not in valid_intervals:
            warnings.append(f"data.kline_interval '{kline_interval}' may not be supported (valid: {valid_intervals})")
        
        kline_limit = data.get("kline_limit", 0)
        if not isinstance(kline_limit, int) or kline_limit <= 0 or kline_limit > 1000:
            errors.append("data.kline_limit must be between 1 and 1000")
    
    # Validate Strategies config
    strategies = config.get("strategies", {})
    if not isinstance(strategies, dict):
        errors.append("strategies config must be a dictionary")
    
    # Log warnings
    for warning in warnings:
        logger.warning(f"Config warning: {warning}")
    
    # Log errors
    for error in errors:
        logger.error(f"Config error: {error}")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    return {
        "openrouter": {
            "api_key": os.getenv("OPENROUTER_API_KEY", ""),
            "base_url": "https://openrouter.ai/api/v1",
            "default_model": "deepseek/deepseek-chat",
            "timeout": 30.0
        },
        "exchange": {
            "name": "binance",
            "testnet": True,
            "trading_type": "spot",
            "api_key": os.getenv("BINANCE_API_KEY", ""),
            "api_secret": os.getenv("BINANCE_API_SECRET", ""),
            "websocket_url": "wss://testnet.binance.vision/ws",
            "rest_url": "https://testnet.binance.vision/api"
        },
        "trading": {
            "initial_capital": 10.0,
            "paper_trading": True,
            "max_position_size_pct": 1.0,
            "max_portfolio_risk_pct": 20.0
        },
        "strategies": {
            "momentum": {"enabled": True, "min_confidence": 0.6},
            "mean_reversion": {"enabled": True, "min_confidence": 0.65},
            "breakout": {"enabled": True, "min_confidence": 0.7},
            "trend_following": {"enabled": True, "min_confidence": 0.75},
            "meta_ai": {"enabled": True, "risk_check_enabled": True}
        },
        "risk": {
            "max_drawdown_pct": 5.0,
            "max_daily_loss_pct": 2.0,
            "max_daily_trades": 100,
            "stop_loss_pct": 0.5,
            "take_profit_pct": 1.0
        },
        "data": {
            "symbols": ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"],
            "kline_interval": "5m",
            "kline_limit": 200
        }
    }
