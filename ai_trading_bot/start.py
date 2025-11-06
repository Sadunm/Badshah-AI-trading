"""
Alternative entry point with enhanced error handling.
"""
import sys
import os
from pathlib import Path

# Add current directory and parent directory to path for Windows compatibility
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent.absolute()

# Add paths to Python path
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

# Change to the directory containing this file
try:
    os.chdir(current_dir)
except Exception:
    # If chdir fails, continue anyway (some environments may not allow it)
    pass

from ai_trading_bot.utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """Main entry point with error handling."""
    try:
        from ai_trading_bot.main import TradingBot
        
        config_path = None
        if len(sys.argv) > 1:
            config_path = Path(sys.argv[1])
        
        bot = TradingBot(config_path)
        bot.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

