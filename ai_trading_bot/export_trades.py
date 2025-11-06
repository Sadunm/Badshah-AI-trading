"""
Export trades to CSV or JSON format.
"""
import sys
import argparse
from pathlib import Path

# Add parent directory to path
if str(Path(__file__).parent.parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_trading_bot.utils.trade_storage import TradeStorage
from ai_trading_bot.utils.logger import get_logger
from ai_trading_bot.utils.performance_analytics import PerformanceAnalytics

logger = get_logger(__name__)


def export_trades(format: str = "csv", symbol: str = None, output: str = None) -> None:
    """
    Export trades.
    
    Args:
        format: Export format (csv or json)
        symbol: Filter by symbol (optional)
        output: Output file path (optional)
    """
    try:
        storage = TradeStorage("trades.json")
        
        trades = storage.get_trades(symbol=symbol)
        
        if not trades:
            logger.warning("No trades found to export")
            return
        
        # Generate output filename
        if not output:
            symbol_suffix = f"_{symbol}" if symbol else ""
            output = f"trades_export{symbol_suffix}.{format}"
        
        # Export
        if format.lower() == "csv":
            storage.export_csv(output, symbol=symbol)
        elif format.lower() == "json":
            storage.export_json(output, symbol=symbol)
        else:
            logger.error(f"Unsupported format: {format}. Use 'csv' or 'json'")
            return
        
        # Print statistics
        stats = storage.get_statistics()
        logger.info("\n" + "="*60)
        logger.info("Trade Statistics")
        logger.info("="*60)
        logger.info(f"Total Trades: {stats['total_trades']}")
        logger.info(f"Winning Trades: {stats['winning_trades']}")
        logger.info(f"Losing Trades: {stats['losing_trades']}")
        logger.info(f"Win Rate: {stats['win_rate']:.2f}%")
        logger.info(f"Total P&L: ${stats['total_pnl']:.2f}")
        logger.info(f"Average P&L: ${stats['average_pnl']:.2f}")
        
        # Performance analytics
        analytics = PerformanceAnalytics.calculate_metrics(trades, 10.0)  # Default initial capital
        logger.info("\n" + "="*60)
        logger.info("Performance Metrics")
        logger.info("="*60)
        logger.info(f"Total Return: {analytics['total_return']:.2f}%")
        logger.info(f"Profit Factor: {analytics['profit_factor']:.2f}")
        logger.info(f"Sharpe Ratio: {analytics['sharpe_ratio']:.2f}")
        logger.info(f"Max Drawdown: {analytics['max_drawdown']:.2f}%")
        logger.info(f"Average Hold Time: {analytics['average_hold_time']:.2f} seconds")
        
    except Exception as e:
        logger.error(f"Error exporting trades: {e}", exc_info=True)
        raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Export Trades")
    parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Export format")
    parser.add_argument("--symbol", help="Filter by symbol")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    export_trades(
        format=args.format,
        symbol=args.symbol,
        output=args.output
    )


if __name__ == "__main__":
    main()

