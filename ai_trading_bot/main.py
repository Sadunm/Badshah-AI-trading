"""
Main trading bot entry point.
Implements the complete trading loop with position monitoring.
"""
import time
import threading
import os
import sys
from typing import Dict, Optional
from pathlib import Path

# Ensure proper path resolution for Windows when running as module
if __name__ == "__main__":
    # When running as script, ensure we can import the package
    current_file = Path(__file__).absolute()
    package_dir = current_file.parent
    parent_dir = package_dir.parent
    
    # Add both directories to path
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    if str(package_dir) not in sys.path:
        sys.path.insert(0, str(package_dir))
    
    # Change to package directory for relative paths
    os.chdir(package_dir)

try:
    from .config import load_config
except ImportError:
    # Fallback for direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from ai_trading_bot.config import load_config
# Import with fallback for direct execution
try:
    from .utils.logger import get_logger
    from .data.websocket_client import WebSocketClient
    from .data.data_manager import DataManager
    from .features.indicators import calculate_all_indicators
    from .strategies.ai_signal_generator import AISignalGenerator
    from .strategies.momentum_strategy import MomentumStrategy
    from .strategies.mean_reversion_strategy import MeanReversionStrategy
    from .strategies.breakout_strategy import BreakoutStrategy
    from .strategies.trend_following_strategy import TrendFollowingStrategy
    from .strategies.meta_ai_strategy import MetaAIStrategy
    from .allocator.position_allocator import PositionAllocator
    from .risk.risk_manager import RiskManager
    from .execution.order_executor import OrderExecutor
except ImportError:
    # Fallback for direct execution
    from ai_trading_bot.utils.logger import get_logger
    from ai_trading_bot.data.websocket_client import WebSocketClient
    from ai_trading_bot.data.data_manager import DataManager
    from ai_trading_bot.features.indicators import calculate_all_indicators
    from ai_trading_bot.strategies.ai_signal_generator import AISignalGenerator
    from ai_trading_bot.strategies.momentum_strategy import MomentumStrategy
    from ai_trading_bot.strategies.mean_reversion_strategy import MeanReversionStrategy
    from ai_trading_bot.strategies.breakout_strategy import BreakoutStrategy
    from ai_trading_bot.strategies.trend_following_strategy import TrendFollowingStrategy
    from ai_trading_bot.strategies.meta_ai_strategy import MetaAIStrategy
    from ai_trading_bot.allocator.position_allocator import PositionAllocator
    from ai_trading_bot.risk.risk_manager import RiskManager
    from ai_trading_bot.execution.order_executor import OrderExecutor

logger = get_logger(__name__)


class TradingBot:
    """Main trading bot class."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """Initialize trading bot."""
        # Load configuration
        self.config = load_config(config_path)
        logger.info("Configuration loaded")
        
        # Initialize components
        self._initialize_components()
        
        # State
        self.is_running = False
        self.last_signal_time = {}
        
        # Threads
        self.monitor_thread: Optional[threading.Thread] = None
    
    def _initialize_components(self) -> None:
        """Initialize all bot components."""
        try:
            # Data layer
            exchange_config = self.config.get("exchange", {})
            data_config = self.config.get("data", {})
            
            symbols = data_config.get("symbols", ["BTCUSDT"])
            websocket_url = exchange_config.get("websocket_url", "wss://testnet.binance.vision/ws")
            rest_url = exchange_config.get("rest_url", "https://testnet.binance.vision/api")
            
            self.websocket_client = WebSocketClient(websocket_url, symbols)
            self.data_manager = DataManager(
                rest_url,
                symbols,
                data_config.get("kline_interval", "5m"),
                data_config.get("kline_limit", 200)
            )
            
            # Set up WebSocket callbacks
            self.websocket_client.on_kline_update = self._on_kline_update
            self.websocket_client.on_price_update = self._on_price_update
            
            # Strategies
            openrouter_config = self.config.get("openrouter", {})
            strategies_config = self.config.get("strategies", {})
            
            self.ai_signal_generator = AISignalGenerator(
                openrouter_config.get("api_key"),
                openrouter_config.get("base_url"),
                openrouter_config.get("default_model"),
                openrouter_config.get("timeout", 30.0),
                strategies_config.get("momentum", {}).get("min_confidence", 0.6)
            )
            
            self.momentum_strategy = MomentumStrategy(
                strategies_config.get("momentum", {}).get("min_confidence", 0.6)
            )
            self.mean_reversion_strategy = MeanReversionStrategy(
                strategies_config.get("mean_reversion", {}).get("min_confidence", 0.65)
            )
            self.breakout_strategy = BreakoutStrategy(
                strategies_config.get("breakout", {}).get("min_confidence", 0.7)
            )
            self.trend_following_strategy = TrendFollowingStrategy(
                strategies_config.get("trend_following", {}).get("min_confidence", 0.75)
            )
            
            meta_ai_config = strategies_config.get("meta_ai", {})
            self.meta_ai_strategy = MetaAIStrategy(
                openrouter_config.get("api_key"),
                openrouter_config.get("base_url"),
                openrouter_config.get("default_model"),
                openrouter_config.get("timeout", 30.0),
                meta_ai_config.get("risk_check_enabled", True)
            )
            
            # Risk and allocation
            trading_config = self.config.get("trading", {})
            risk_config = self.config.get("risk", {})
            
            initial_capital = trading_config.get("initial_capital", 10.0)
            
            self.position_allocator = PositionAllocator(
                initial_capital,
                trading_config.get("max_position_size_pct", 1.0),
                trading_config.get("max_portfolio_risk_pct", 20.0)
            )
            
            self.risk_manager = RiskManager(
                initial_capital,
                risk_config.get("max_drawdown_pct", 5.0),
                risk_config.get("max_daily_loss_pct", 2.0),
                risk_config.get("max_daily_trades", 100)
            )
            
            # Execution
            self.order_executor = OrderExecutor(
                trading_config.get("paper_trading", True)
            )
            
            # Trade storage (for persistence)
            from ..utils.trade_storage import TradeStorage
            self.trade_storage = TradeStorage("trades.json")
            
            logger.info("All components initialized")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}", exc_info=True)
            raise
    
    def _on_kline_update(self, symbol: str, candle: Dict) -> None:
        """Handle kline update from WebSocket."""
        try:
            self.data_manager.update_kline(symbol, candle)
        except Exception as e:
            logger.error(f"Error handling kline update: {e}", exc_info=True)
    
    def _on_price_update(self, symbol: str, price: float) -> None:
        """Handle price update from WebSocket."""
        # Price updates are handled in monitoring loop
        pass
    
    def start(self) -> None:
        """Start the trading bot."""
        try:
            logger.info("Starting trading bot...")
            
            # Connect WebSocket
            logger.info("Connecting to WebSocket...")
            if not self.websocket_client.start():
                logger.error("Failed to connect to WebSocket")
                return
            
            # Wait for connection
            time.sleep(3)
            
            # Fetch historical data
            logger.info("Fetching historical data...")
            self.data_manager.fetch_all_historical_data()
            
            # Start monitoring thread
            self.is_running = True
            self.monitor_thread = threading.Thread(target=self._monitor_positions, daemon=True)
            self.monitor_thread.start()
            
            # Start main trading loop
            logger.info("Trading bot started")
            self._trading_loop()
            
        except KeyboardInterrupt:
            logger.info("Shutting down trading bot...")
            self.stop()
        except Exception as e:
            logger.error(f"Error starting trading bot: {e}", exc_info=True)
            self.stop()
    
    def stop(self) -> None:
        """Stop the trading bot gracefully."""
        try:
            logger.info("Stopping trading bot gracefully...")
            self.is_running = False
            
            # Close WebSocket
            self.websocket_client.stop()
            
            # Save any remaining state
            if hasattr(self, 'trade_storage'):
                self.trade_storage._save_trades()
            
            logger.info("Trading bot stopped gracefully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}", exc_info=True)
    
    def _monitor_positions(self) -> None:
        """Monitor open positions every 5 seconds."""
        while self.is_running:
            try:
                open_positions = self.risk_manager.get_open_positions()
                
                for symbol, position in open_positions.items():
                    # Get current price
                    current_price = self.websocket_client.get_price(symbol)
                    
                    if current_price is None or current_price <= 0:
                        continue
                    
                    # Check stop loss and take profit
                    trigger = self.risk_manager.check_stop_loss_take_profit(symbol, current_price)
                    
                    if trigger:
                        # Close position
                        execution = self.order_executor.close_order(symbol, position, current_price)
                        if execution:
                            trade = self.risk_manager.close_position(
                                symbol,
                                execution["executed_price"],
                                trigger
                            )
                            
                            # Save trade to storage
                            if trade:
                                self.trade_storage.add_trade(trade)
                            
                            # Update allocator capital
                            self.position_allocator.update_capital(self.risk_manager.get_current_capital())
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                logger.error(f"Error in position monitoring: {e}", exc_info=True)
                time.sleep(5)
    
    def _trading_loop(self) -> None:
        """Main trading loop - generate signals every 30 seconds."""
        while self.is_running:
            try:
                # Generate signals for each symbol
                for symbol in self.config.get("data", {}).get("symbols", []):
                    # Check if we already have a position
                    if symbol in self.risk_manager.get_open_positions():
                        continue
                    
                    # Check if enough time has passed since last signal
                    last_time = self.last_signal_time.get(symbol, 0)
                    if time.time() - last_time < 30:
                        continue
                    
                    # Get market data
                    market_data = self._get_market_data(symbol)
                    if not market_data:
                        continue
                    
                    # Generate signal (try AI first, then fallback strategies)
                    signal = None
                    
                    # Try AI signal generator (PRIMARY)
                    if self.ai_signal_generator.enabled:
                        signal = self.ai_signal_generator.generate_signal(market_data, symbol)
                    
                    # Fallback to rule-based strategies if AI fails
                    if signal is None:
                        strategies = [
                            self.momentum_strategy,
                            self.mean_reversion_strategy,
                            self.breakout_strategy,
                            self.trend_following_strategy
                        ]
                        
                        for strategy in strategies:
                            if strategy.enabled:
                                signal = strategy.generate_signal(market_data, symbol)
                                if signal:
                                    break
                    
                    # Meta AI validation
                    if signal:
                        if not self.meta_ai_strategy.validate_signal_risk(signal, market_data, symbol):
                            logger.info(f"Meta AI rejected signal for {symbol}")
                            signal = None
                    
                    # Execute signal if valid
                    if signal and signal.get("action") != "FLAT":
                        self._execute_signal(symbol, signal, market_data)
                    
                    self.last_signal_time[symbol] = time.time()
                
                # Log status
                self._log_status()
                
                # Sleep for 30 seconds
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}", exc_info=True)
                time.sleep(30)
    
    def _get_market_data(self, symbol: str) -> Optional[Dict]:
        """Get market data with indicators for a symbol."""
        try:
            # Get candles
            candles = self.data_manager.get_historical_data(symbol)
            if not candles or len(candles) < 30:
                # Try WebSocket cache
                candles = self.websocket_client.get_klines(symbol, 200)
            
            if not candles or len(candles) < 30:
                logger.warning(f"Insufficient data for {symbol}: {len(candles) if candles else 0} candles")
                return None
            
            # Calculate indicators
            indicators = calculate_all_indicators(candles)
            
            if not indicators:
                logger.warning(f"Failed to calculate indicators for {symbol}")
                return None
            
            # Get current price
            current_price = self.websocket_client.get_price(symbol)
            if current_price is None or current_price <= 0:
                # Fallback to last close
                if candles and len(candles) > 0:
                    current_price = candles[-1].get("close", 0)
                    if current_price <= 0:
                        logger.warning(f"Invalid price for {symbol}")
                        return None
                else:
                    logger.warning(f"No price available for {symbol}")
                    return None
            
            indicators["current_price"] = current_price
            
            return indicators
            
        except (KeyError, IndexError, TypeError) as e:
            logger.error(f"Error getting market data for {symbol}: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Error getting market data for {symbol}: {e}", exc_info=True)
            return None
    
    def _execute_signal(self, symbol: str, signal: Dict, market_data: Dict) -> None:
        """Execute a trading signal."""
        try:
            # Check risk limits
            if not self.risk_manager.can_open_position():
                logger.warning("Cannot open position - risk limits reached")
                return
            
            # Calculate position size
            current_price = market_data.get("current_price", signal.get("entry_price", 0))
            position_size = self.position_allocator.calculate_position_size(signal, current_price)
            
            if position_size is None or position_size <= 0:
                logger.warning(f"Invalid position size for {symbol}")
                return
            
            # Execute order
            entry_price = signal.get("entry_price", current_price)
            execution = self.order_executor.execute_order(
                symbol,
                signal["action"],
                position_size,
                entry_price,
                current_price
            )
            
            if execution:
                # Open position
                position = {
                    "action": signal["action"],
                    "size": position_size,
                    "entry_price": execution["executed_price"],
                    "stop_loss": signal.get("stop_loss", entry_price * 0.995),
                    "take_profit": signal.get("take_profit", entry_price * 1.01),
                    "reason": signal.get("reason", "Signal")
                }
                
                if self.risk_manager.open_position(symbol, position):
                    logger.info(f"Position opened: {symbol} {signal['action']} {position_size:.6f} @ ${execution['executed_price']:.2f}")
                    # Note: Trade will be saved when position closes
                else:
                    logger.warning(f"Failed to open position for {symbol}")
            else:
                logger.error(f"Order execution failed for {symbol}")
                
        except Exception as e:
            logger.error(f"Error executing signal for {symbol}: {e}", exc_info=True)
    
    def _log_status(self) -> None:
        """Log bot status."""
        try:
            capital = self.risk_manager.get_current_capital()
            pnl = self.risk_manager.get_total_pnl()
            drawdown = self.risk_manager.get_drawdown_pct()
            open_positions = len(self.risk_manager.get_open_positions())
            total_trades = len(self.risk_manager.get_trade_history())
            
            logger.info(f"Status - Capital: ${capital:.2f}, P&L: ${pnl:.2f}, Drawdown: {drawdown:.2f}%, "
                       f"Open Positions: {open_positions}, Total Trades: {total_trades}")
            
        except Exception as e:
            logger.error(f"Error logging status: {e}", exc_info=True)


def main():
    """Main entry point."""
    try:
        bot = TradingBot()
        bot.start()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()

