"""
Download historical data for backtesting.
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
from ai_trading_bot.backtesting.data_fetcher import BacktestDataFetcher

logger = get_logger(__name__)


def download_historical_data(symbols: List[str] = None, days: int = 30, 
                            output_dir: str = "historical_data") -> None:
    """
    Download historical data for symbols.
    
    Args:
        symbols: List of symbols (default: from config)
        days: Number of days to download
        output_dir: Directory to save data
    """
    try:
        # Load configuration
        config = load_config()
        
        # Get symbols
        if symbols is None:
            symbols = config.get("data", {}).get("symbols", ["BTCUSDT"])
        
        logger.info(f"Downloading historical data for: {symbols}")
        logger.info(f"Days: {days}")
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize data fetcher
        data_fetcher = BacktestDataFetcher(
            config.get("exchange", {}).get("rest_url", "https://testnet.binance.vision/api")
        )
        
        kline_interval = config.get("data", {}).get("kline_interval", "5m")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        all_data = {}
        
        for symbol in symbols:
            logger.info(f"\n{'='*60}")
            logger.info(f"Downloading {symbol}...")
            logger.info(f"{'='*60}")
            
            candles = data_fetcher.fetch_historical_data(
                symbol,
                kline_interval,
                start_date,
                end_date,
                limit=1000
            )
            
            if candles and len(candles) >= 30:
                all_data[symbol] = candles
                
                # Save individual symbol file
                symbol_file = output_path / f"{symbol}_{kline_interval}_{days}d.json"
                with open(symbol_file, 'w') as f:
                    json.dump({
                        "symbol": symbol,
                        "interval": kline_interval,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "candles": candles
                    }, f, indent=2, default=str)
                
                logger.info(f"✅ {symbol}: {len(candles)} candles saved to {symbol_file}")
            else:
                logger.warning(f"⚠️  {symbol}: Insufficient data ({len(candles) if candles else 0} candles)")
        
        # Save combined file
        if all_data:
            combined_file = output_path / f"all_symbols_{kline_interval}_{days}d.json"
            with open(combined_file, 'w') as f:
                json.dump({
                    "metadata": {
                        "interval": kline_interval,
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "days": days
                    },
                    "data": all_data
                }, f, indent=2, default=str)
            
            logger.info(f"\n💾 Combined data saved to: {combined_file}")
            logger.info(f"📊 Total symbols: {len(all_data)}")
            logger.info(f"📊 Total candles: {sum(len(c) for c in all_data.values())}")
        
    except KeyboardInterrupt:
        logger.info("\nDownload interrupted by user")
    except Exception as e:
        logger.error(f"Error downloading data: {e}", exc_info=True)
        raise


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download Historical Data")
    parser.add_argument("--symbols", nargs="+", help="Symbols to download (default: from config)")
    parser.add_argument("--days", type=int, default=30, help="Number of days (default: 30)")
    parser.add_argument("--output", type=str, default="historical_data", help="Output directory")
    
    args = parser.parse_args()
    
    download_historical_data(
        symbols=args.symbols,
        days=args.days,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()

