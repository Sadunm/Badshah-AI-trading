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

# Ensure proper path resolution for Windows/Linux when running as module
# This works for both direct execution and module execution
current_file = Path(__file__).absolute()
package_dir = current_file.parent
parent_dir = package_dir.parent

# Add both directories to path (works on Windows and Linux)
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
if str(package_dir) not in sys.path:
    sys.path.insert(0, str(package_dir))

# Change to package directory for relative paths (config files, etc.)
try:
    os.chdir(package_dir)
except Exception:
    # If chdir fails, continue anyway (some environments may not allow it)
    pass

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
            use_mock = exchange_config.get("use_mock_data", False) or exchange_config.get("name") == "mock"
            
            if use_mock:
                # Use mock data provider instead of real exchange
                logger.info("Using mock data provider (no real exchange connection needed)")
                try:
                    from .data.mock_data_provider import MockDataProvider
                except ImportError:
                    from ai_trading_bot.data.mock_data_provider import MockDataProvider
                
                self.websocket_client = MockDataProvider(symbols, update_interval=1.0)
                self.data_manager = DataManager(
                    "mock://localhost",  # Mock URL
                    symbols,
                    data_config.get("kline_interval", "5m"),
                    data_config.get("kline_limit", 200),
                    exchange="mock"
                )
                
                # Set up mock data callbacks
                self.websocket_client.on_kline(self._on_kline_update)
                self.websocket_client.on_ticker(self._on_price_update)
            else:
                # Use real exchange (Binance or Bybit)
                exchange_name = exchange_config.get("name", "binance").lower()
                websocket_url = exchange_config.get("websocket_url")
                rest_url = exchange_config.get("rest_url")
                
                if not websocket_url or not rest_url:
                    logger.error(f"{exchange_name} WebSocket or REST URL not configured")
                    raise ValueError(f"{exchange_name} URLs are required")
                
                if exchange_name == "bybit":
                    # Use Bybit WebSocket client
                    try:
                        from .data.bybit_websocket_client import BybitWebSocketClient
                    except ImportError:
                        from ai_trading_bot.data.bybit_websocket_client import BybitWebSocketClient
                    
                    logger.info("Initializing Bybit WebSocket client")
                    self.websocket_client = BybitWebSocketClient(websocket_url, symbols)
                    self.data_manager = DataManager(
                        rest_url,
                        symbols,
                        data_config.get("kline_interval", "5m"),
                        data_config.get("kline_limit", 200),
                        exchange="bybit"
                    )
                    
                    # Set up Bybit WebSocket callbacks
                    self.websocket_client.on_kline_update = self._on_kline_update
                    self.websocket_client.on_price_update = self._on_price_update
                else:
                    # Use Binance WebSocket client (default)
                    logger.info("Initializing Binance WebSocket client")
                    self.websocket_client = WebSocketClient(websocket_url, symbols)
                    self.data_manager = DataManager(
                        rest_url,
                        symbols,
                        data_config.get("kline_interval", "5m"),
                        data_config.get("kline_limit", 200),
                        exchange="binance"
                    )
                    
                    # Set up Binance WebSocket callbacks
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
            
            # Execution - FORCE PAPER TRADING FOR SAFETY
            paper_trading_mode = trading_config.get("paper_trading", True)
            if not paper_trading_mode:
                logger.warning("⚠️  Real trading disabled - forcing paper trading mode for safety")
                paper_trading_mode = True
            
            self.order_executor = OrderExecutor(
                paper_trading=paper_trading_mode,
                exchange_config=exchange_config if not paper_trading_mode else None
            )
            
            logger.info(f"📊 Trading Mode: {'PAPER TRADING (Simulated)' if paper_trading_mode else 'REAL TRADING'}")
            
            # Trade storage (for persistence)
            try:
                from .utils.trade_storage import TradeStorage
            except ImportError:
                from ai_trading_bot.utils.trade_storage import TradeStorage
            self.trade_storage = TradeStorage("trades.json")
            
            # Log initial status
            self._log_startup_summary()
            
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
            websocket_started = self.websocket_client.start()
            
            # Wait for connection with timeout
            max_wait_time = 60  # Wait up to 60 seconds
            wait_interval = 2
            waited = 0
            
            while waited < max_wait_time:
                if self.websocket_client.is_connected:
                    logger.info("WebSocket connected successfully")
                    break
                if not self.websocket_client.is_running:
                    # Connection failed completely, try fallback to mock data
                    logger.warning("Binance connection failed. Attempting fallback to mock data...")
                    if self._fallback_to_mock_data():
                        logger.info("Successfully switched to mock data provider")
                        break
                    else:
                        logger.error("Failed to initialize mock data fallback")
                        return
                time.sleep(wait_interval)
                waited += wait_interval
            
            # Final check: if WebSocketClient failed to connect after timeout, use mock fallback
            if isinstance(self.websocket_client, WebSocketClient) and not self.websocket_client.is_connected:
                logger.warning("WebSocket connection timeout. Switching to mock data...")
                if self._fallback_to_mock_data():
                    logger.info("Successfully switched to mock data provider")
                else:
                    logger.error("Failed to initialize mock data fallback")
                    return
            
            # Fetch historical data
            logger.info("Fetching historical data...")
            try:
                self.data_manager.fetch_all_historical_data()
            except Exception as e:
                logger.warning(f"Could not fetch historical data: {e}. Continuing with available data...")
            
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
    
    def _fallback_to_mock_data(self) -> bool:
        """Fallback to mock data provider when real exchange connection fails."""
        try:
            logger.info("Initializing mock data provider as fallback...")
            
            # Stop current WebSocket client
            if hasattr(self, 'websocket_client') and self.websocket_client:
                try:
                    self.websocket_client.stop()
                except Exception:
                    pass
            
            # Import mock data provider
            try:
                from .data.mock_data_provider import MockDataProvider
            except ImportError:
                from ai_trading_bot.data.mock_data_provider import MockDataProvider
            
            # Get symbols from config
            data_config = self.config.get("data", {})
            symbols = data_config.get("symbols", ["BTCUSDT"])
            
            # Initialize mock data provider
            self.websocket_client = MockDataProvider(symbols, update_interval=1.0)
            
            # Update data manager to use mock URL
            self.data_manager = DataManager(
                "mock://localhost",
                symbols,
                data_config.get("kline_interval", "5m"),
                data_config.get("kline_limit", 200),
                exchange="mock"
            )
            
            # Set up mock data callbacks
            self.websocket_client.on_kline(self._on_kline_update)
            self.websocket_client.on_ticker(self._on_price_update)
            
            # Start mock data provider
            self.websocket_client.start()
            
            logger.info("Mock data provider initialized and started")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing mock data fallback: {e}", exc_info=True)
            return False
    
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
        """Monitor open positions every 5 seconds with improved error handling."""
        while self.is_running:
            try:
                # Get snapshot of open positions (thread-safe)
                open_positions = self.risk_manager.get_open_positions().copy()
                
                if not open_positions:
                    time.sleep(5)
                    continue
                
                for symbol, position in list(open_positions.items()):  # Create list to avoid modification during iteration
                    try:
                        # Validate position data
                        if not position or not isinstance(position, dict):
                            logger.warning(f"Invalid position data for {symbol}, skipping")
                            continue
                        
                        # Get current price with validation
                        current_price = self.websocket_client.get_price(symbol)
                        
                        # Validate price
                        if current_price is None or current_price <= 0 or not isinstance(current_price, (int, float)):
                            # Try fallback: get from market data
                            try:
                                market_data = self._get_market_data(symbol)
                                if market_data and "current_price" in market_data:
                                    current_price = market_data["current_price"]
                                else:
                                    logger.warning(f"Unable to get valid price for {symbol}, skipping check")
                                    continue
                            except Exception:
                                logger.warning(f"Error getting fallback price for {symbol}")
                                continue
                        
                        # Additional price validation (prevent extreme values)
                        entry_price = position.get("entry_price", 0)
                        if entry_price > 0:
                            # Price change should not exceed 50% in single check (likely data error)
                            price_change_pct = abs((current_price - entry_price) / entry_price)
                            if price_change_pct > 0.5:
                                logger.warning(f"Suspicious price change for {symbol}: {price_change_pct*100:.2f}%, skipping check")
                                continue
                        
                        # Check stop loss and take profit
                        trigger = self.risk_manager.check_stop_loss_take_profit(symbol, current_price)
                        
                        if trigger:
                            # Close position (thread-safe operation)
                            try:
                                execution = self.order_executor.close_order(symbol, position, current_price)
                                if execution:
                                    trade = self.risk_manager.close_position(
                                        symbol,
                                        execution["executed_price"],
                                        trigger
                                    )
                                    
                                    # Save trade to storage
                                    if trade and hasattr(self, 'trade_storage'):
                                        try:
                                            self.trade_storage.add_trade(trade)
                                        except Exception as e:
                                            logger.error(f"Error saving trade to storage: {e}", exc_info=True)
                                    
                                    # Update allocator capital
                                    self.position_allocator.update_capital(self.risk_manager.get_current_capital())
                            except Exception as e:
                                logger.error(f"Error closing position for {symbol}: {e}", exc_info=True)
                    
                    except KeyError:
                        # Position was closed by another thread, skip
                        continue
                    except Exception as e:
                        logger.error(f"Error monitoring position {symbol}: {e}", exc_info=True)
                        continue
                
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
            # Get current prices for all open positions for accurate equity calculation
            current_prices = {}
            for open_symbol in self.risk_manager.get_open_positions().keys():
                try:
                    price_data = self._get_market_data(open_symbol)
                    if price_data and "current_price" in price_data:
                        current_prices[open_symbol] = price_data["current_price"]
                except Exception:
                    pass  # Skip if can't get price
            
            # Add current symbol price with validation
            current_price = market_data.get("current_price", signal.get("entry_price", 0))
            if current_price and isinstance(current_price, (int, float)) and current_price > 0:
                # Additional validation: price should be reasonable (not NaN, Inf, or extreme)
                if float('inf') > current_price > 0 and current_price < 1e10:  # Reasonable upper bound
                    current_prices[symbol] = float(current_price)
                else:
                    logger.warning(f"Invalid current price for {symbol}: {current_price}")
            
            # Calculate position size first (to estimate cost)
            current_price = market_data.get("current_price", signal.get("entry_price", 0))
            position_size = self.position_allocator.calculate_position_size(signal, current_price)
            
            if position_size is None or position_size <= 0:
                logger.warning(f"Invalid position size for {symbol}")
                return
            
            # Estimate position cost (entry price + fees) to check if we can afford it
            estimated_entry_price = signal.get("entry_price", current_price)
            if estimated_entry_price <= 0:
                estimated_entry_price = current_price
            
            # Calculate estimated cost (position value + entry fee)
            estimated_position_value = position_size * estimated_entry_price
            estimated_entry_fee = estimated_position_value * 0.001  # 0.1% fee
            estimated_total_cost = estimated_position_value + estimated_entry_fee
            
            # Check if we have enough capital
            available_capital = self.risk_manager.get_current_capital()
            if available_capital < estimated_total_cost:
                logger.warning(f"Insufficient capital for {symbol}: ${available_capital:.2f} < ${estimated_total_cost:.4f}")
                return
            
            # Simulate opening position to check if it would exceed drawdown
            # Calculate what equity would be after opening this position
            # Use the internal method to get current equity
            current_equity = self.risk_manager._calculate_current_equity(current_prices)
            simulated_equity_after_position = current_equity - estimated_total_cost  # Deduct position cost
            
            # Check if this would exceed drawdown limit
            peak_capital = self.risk_manager.peak_capital
            if peak_capital > 0:
                simulated_drawdown = ((peak_capital - simulated_equity_after_position) / peak_capital) * 100
                max_drawdown = self.risk_manager.max_drawdown_pct - 0.1  # Use buffer
                
                if simulated_drawdown >= max_drawdown:
                    logger.warning(f"Opening position would exceed drawdown limit: {simulated_drawdown:.2f}% >= {max_drawdown:.2f}% (current equity: ${current_equity:.2f}, after position: ${simulated_equity_after_position:.2f})")
                    return
            
            # Now check risk limits with current prices for accurate equity calculation
            if not self.risk_manager.can_open_position(current_prices):
                logger.warning("Cannot open position - risk limits reached")
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
                    logger.info(f"📈 Position opened: {symbol} {signal['action']} {position_size:.6f} @ ${execution['executed_price']:.2f} | "
                               f"Cost: ${execution.get('total_cost', 0):.4f} (fees: ${execution.get('fees', 0):.4f})")
                    # Note: Trade will be saved when position closes
                else:
                    logger.warning(f"⚠️ Failed to open position for {symbol}")
            else:
                logger.error(f"Order execution failed for {symbol}")
                
        except Exception as e:
            logger.error(f"Error executing signal for {symbol}: {e}", exc_info=True)
    
    def _log_startup_summary(self) -> None:
        """Log startup summary with existing trade history."""
        try:
            if not hasattr(self, 'trade_storage'):
                logger.warning("Trade storage not initialized")
                return
            
            # Load existing trades from storage
            existing_trades = self.trade_storage.get_trades()
            
            if existing_trades:
                stats = self.trade_storage.get_statistics()
                logger.info("=" * 70)
                logger.info("📊 EXISTING TRADE HISTORY:")
                logger.info(f"   Total Trades: {stats['total_trades']}")
                logger.info(f"   Win Rate: {stats['win_rate']:.1f}% ({stats['winning_trades']}W / {stats['losing_trades']}L)")
                logger.info(f"   Total P&L: ${stats['total_pnl']:.4f}")
                logger.info(f"   Average P&L: ${stats['average_pnl']:.4f}")
                if stats['best_trade']:
                    logger.info(f"   Best Trade: ${stats['best_trade'].get('net_pnl', 0):.4f}")
                if stats['worst_trade']:
                    logger.info(f"   Worst Trade: ${stats['worst_trade'].get('net_pnl', 0):.4f}")
                logger.info("=" * 70)
            else:
                logger.info("📊 No existing trades - starting fresh!")
            
            # Current capital status
            capital = self.risk_manager.get_current_capital()
            initial_capital = self.risk_manager.initial_capital
            logger.info(f"💰 Initial Capital: ${initial_capital:.2f} | Current Capital: ${capital:.2f}")
            logger.info(f"📈 Paper Trading: ENABLED | Fees: 0.1% per side (Binance matching)")
            logger.info("")
            
        except Exception as e:
            logger.error(f"Error logging startup summary: {e}", exc_info=True)
    
    def _log_status(self) -> None:
        """Log bot status with detailed PnL information."""
        try:
            # Get current prices for accurate equity calculation
            current_prices = {}
            for symbol in self.risk_manager.get_open_positions().keys():
                try:
                    price_data = self._get_market_data(symbol)
                    if price_data and "current_price" in price_data:
                        current_prices[symbol] = price_data["current_price"]
                except Exception:
                    pass  # Skip if can't get price
            
            capital = self.risk_manager.get_current_capital()
            equity = self.risk_manager.get_current_equity(current_prices)
            pnl = self.risk_manager.get_total_pnl(current_prices)
            drawdown = self.risk_manager.get_drawdown_pct(current_prices)
            open_positions = len(self.risk_manager.get_open_positions())
            total_trades = len(self.risk_manager.get_trade_history())
            
            # Calculate PnL percentage
            initial_capital = self.risk_manager.initial_capital
            pnl_pct = (pnl / initial_capital * 100) if initial_capital > 0 else 0.0
            
            # Get trade statistics
            trade_history = self.risk_manager.get_trade_history()
            winning_trades = [t for t in trade_history if t.get("net_pnl", 0) > 0]
            losing_trades = [t for t in trade_history if t.get("net_pnl", 0) < 0]
            win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0.0
            
            # Show both capital and equity
            unrealized_pnl = equity - capital
            logger.info(f"📊 Status - Capital: ${capital:.2f} | Equity: ${equity:.2f} | "
                       f"PnL: ${pnl:.2f} ({pnl_pct:+.2f}%) | Unrealized: ${unrealized_pnl:+.2f} | "
                       f"Drawdown: {drawdown:.2f}% | Open: {open_positions} | "
                       f"Trades: {total_trades} (Win Rate: {win_rate:.1f}%)")
            
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

