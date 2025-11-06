"""
Backtesting entry point for AI Trading Bot.
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

# Add parent directory to path
if str(Path(__file__).parent.parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_trading_bot.config import load_config
from ai_trading_bot.utils.logger import get_logger
from ai_trading_bot.backtesting.backtest_engine import BacktestEngine
from ai_trading_bot.backtesting.data_fetcher import BacktestDataFetcher

logger = get_logger(__name__)


def run_backtest(symbols: List[str] = None, days: int = 30, 
                 output_file: str = None) -> None:
    """
    Run backtest on specified symbols.
    
    Args:
        symbols: List of symbols to backtest (default: from config)
        days: Number of days of historical data to use
        output_file: Output file for results (optional)
    """
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config()
        
        # Get symbols
        if symbols is None:
            symbols = config.get("data", {}).get("symbols", ["BTCUSDT"])
        
        logger.info(f"Backtesting symbols: {symbols}")
        
        # Fetch historical data
        logger.info(f"Fetching {days} days of historical data...")
        data_fetcher = BacktestDataFetcher(
            config.get("exchange", {}).get("rest_url", "https://testnet.binance.vision/api")
        )
        
        kline_interval = config.get("data", {}).get("kline_interval", "5m")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        historical_data = {}
        for symbol in symbols:
            logger.info(f"Fetching data for {symbol}...")
            candles = data_fetcher.fetch_historical_data(
                symbol,
                kline_interval,
                start_date,
                end_date,
                limit=1000
            )
            
            if candles and len(candles) >= 30:
                historical_data[symbol] = candles
                logger.info(f"✅ {symbol}: {len(candles)} candles")
            else:
                logger.warning(f"⚠️  {symbol}: Insufficient data ({len(candles) if candles else 0} candles)")
        
        if not historical_data:
            logger.error("No historical data available for backtesting")
            return
        
        # Run backtest for each symbol
        all_results = {}
        
        for symbol in historical_data.keys():
            logger.info(f"\n{'='*60}")
            logger.info(f"Running backtest for {symbol}")
            logger.info(f"{'='*60}")
            
            engine = BacktestEngine(config, historical_data)
            results = engine.run(symbol, start_date, end_date)
            
            if results:
                all_results[symbol] = results
                
                # Print summary
                metrics = results.get("metrics", {})
                logger.info(f"\n📊 Backtest Results for {symbol}:")
                logger.info(f"  Total Trades: {metrics.get('total_trades', 0)}")
                logger.info(f"  Winning Trades: {metrics.get('winning_trades', 0)}")
                logger.info(f"  Losing Trades: {metrics.get('losing_trades', 0)}")
                logger.info(f"  Win Rate: {metrics.get('win_rate', 0):.2f}%")
                logger.info(f"  Total P&L: ${metrics.get('total_pnl', 0):.2f}")
                logger.info(f"  Total Return: {metrics.get('total_return', 0):.2f}%")
                logger.info(f"  Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
                logger.info(f"  Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
                logger.info(f"  Initial Capital: ${metrics.get('initial_capital', 0):.2f}")
                logger.info(f"  Final Capital: ${metrics.get('final_capital', 0):.2f}")
            else:
                logger.warning(f"No results for {symbol}")
        
        # Save results if output file specified
        if output_file:
            output_path = Path(output_file)
            with open(output_path, 'w') as f:
                json.dump(all_results, f, indent=2, default=str)
            logger.info(f"\n💾 Results saved to: {output_path}")
        
        # Print overall summary
        if all_results:
            logger.info(f"\n{'='*60}")
            logger.info("Overall Backtest Summary")
            logger.info(f"{'='*60}")
            
            total_trades = sum(r.get("metrics", {}).get("total_trades", 0) for r in all_results.values())
            total_pnl = sum(r.get("metrics", {}).get("total_pnl", 0) for r in all_results.values())
            avg_return = sum(r.get("metrics", {}).get("total_return", 0) for r in all_results.values()) / len(all_results)
            
            logger.info(f"  Total Trades (All Symbols): {total_trades}")
            logger.info(f"  Total P&L (All Symbols): ${total_pnl:.2f}")
            logger.info(f"  Average Return: {avg_return:.2f}%")
        
    except KeyboardInterrupt:
        logger.info("\nBacktest interrupted by user")
    except Exception as e:
        logger.error(f"Error running backtest: {e}", exc_info=True)
        raise


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Trading Bot Backtesting")
    parser.add_argument("--symbols", nargs="+", help="Symbols to backtest (default: from config)")
    parser.add_argument("--days", type=int, default=30, help="Number of days of data (default: 30)")
    parser.add_argument("--output", type=str, help="Output file for results (JSON)")
    
    args = parser.parse_args()
    
    run_backtest(
        symbols=args.symbols,
        days=args.days,
        output_file=args.output
    )


if __name__ == "__main__":
    main()

