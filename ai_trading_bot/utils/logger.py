"""
Logging system with multiple fallback mechanisms.
Works even if file system is read-only.
"""
import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


class SafeLogger:
    """Logger that gracefully handles file system errors."""
    
    def __init__(self, name: str = "ai_trading_bot", log_dir: Optional[Path] = None):
        """
        Initialize logger with fallback mechanisms.
        
        Args:
            name: Logger name
            log_dir: Optional log directory (tries multiple fallbacks)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Remove existing handlers
        self.logger.handlers.clear()
        
        # Console handler (always works)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        self.logger.addHandler(console_handler)
        
        # Try to add file handler with multiple fallback directories
        if log_dir is None:
            # Try multiple fallback directories (Windows and Linux compatible)
            import tempfile
            fallback_dirs = [
                Path("logs"),
                Path(".") / "logs",
                Path(__file__).parent.parent / "logs",  # Relative to package
                Path.home() / ".ai_trading_bot" / "logs",
                Path(tempfile.gettempdir()) / "ai_trading_bot_logs",  # Cross-platform temp
            ]
        else:
            fallback_dirs = [log_dir]
        
        file_handler = None
        for log_path in fallback_dirs:
            try:
                log_path.mkdir(parents=True, exist_ok=True)
                log_file = log_path / "trading_bot.log"
                
                # Create rotating file handler
                handler = RotatingFileHandler(
                    str(log_file),
                    maxBytes=10 * 1024 * 1024,  # 10MB
                    backupCount=3,
                    encoding='utf-8'
                )
                handler.setLevel(logging.INFO)
                file_format = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                handler.setFormatter(file_format)
                self.logger.addHandler(handler)
                file_handler = handler
                self.logger.info(f"File logging enabled: {log_file}")
                break
            except (OSError, PermissionError, IOError) as e:
                # Try next fallback directory
                continue
        
        if file_handler is None:
            self.logger.warning("File logging disabled - using console only")
    
    def get_logger(self) -> logging.Logger:
        """Get the logger instance."""
        return self.logger


# Global logger instance
_logger_instance: Optional[SafeLogger] = None


def get_logger(name: str = "ai_trading_bot") -> logging.Logger:
    """Get or create global logger instance."""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SafeLogger(name)
    return _logger_instance.get_logger()

