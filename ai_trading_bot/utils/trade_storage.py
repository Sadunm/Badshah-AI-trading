"""
Trade storage and persistence for AI Trading Bot.
Saves trades to JSON file for persistence across restarts.
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from .logger import get_logger

logger = get_logger(__name__)


class TradeStorage:
    """Stores and retrieves trade history."""
    
    def __init__(self, storage_file: str = "trades.json"):
        """
        Initialize trade storage.
        
        Args:
            storage_file: Path to JSON file for storage
        """
        self.storage_file = Path(storage_file)
        self.trades: List[Dict] = []
        self._load_trades()
    
    def _load_trades(self) -> None:
        """Load trades from file."""
        try:
            if self.storage_file.exists():
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.trades = data.get("trades", [])
                    logger.info(f"Loaded {len(self.trades)} trades from {self.storage_file}")
            else:
                logger.info(f"No existing trade file found, starting fresh")
                self.trades = []
        except Exception as e:
            logger.error(f"Error loading trades: {e}", exc_info=True)
            self.trades = []
    
    def _save_trades(self) -> None:
        """Save trades to file."""
        try:
            # Create directory if needed
            self.storage_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save with metadata
            data = {
                "last_updated": datetime.now().isoformat(),
                "total_trades": len(self.trades),
                "trades": self.trades
            }
            
            # Write to temporary file first, then rename (atomic write)
            temp_file = self.storage_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            # Atomic rename
            temp_file.replace(self.storage_file)
            logger.debug(f"Saved {len(self.trades)} trades to {self.storage_file}")
            
        except Exception as e:
            logger.error(f"Error saving trades: {e}", exc_info=True)
    
    def add_trade(self, trade: Dict) -> None:
        """
        Add a trade to storage.
        
        Args:
            trade: Trade dictionary
        """
        try:
            # Add timestamp if not present
            if "timestamp" not in trade:
                trade["timestamp"] = datetime.now().isoformat()
            
            self.trades.append(trade)
            self._save_trades()
            
            # Log trade summary for visibility
            symbol = trade.get('symbol', 'UNKNOWN')
            action = trade.get('action', 'UNKNOWN')
            net_pnl = trade.get('net_pnl', 0.0)
            pnl_emoji = "✅" if net_pnl > 0 else "❌" if net_pnl < 0 else "➖"
            
            logger.info(f"💾 {pnl_emoji} Trade saved: {symbol} {action} | P&L: ${net_pnl:.4f} | "
                       f"Total Trades: {len(self.trades)}")
            
        except Exception as e:
            logger.error(f"Error adding trade: {e}", exc_info=True)
    
    def get_trades(self, symbol: Optional[str] = None, 
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None) -> List[Dict]:
        """
        Get trades with optional filtering.
        
        Args:
            symbol: Filter by symbol
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            List of trades
        """
        trades = self.trades.copy()
        
        # Filter by symbol
        if symbol:
            trades = [t for t in trades if t.get("symbol") == symbol]
        
        # Filter by date
        if start_date or end_date:
            filtered = []
            for trade in trades:
                trade_time_str = trade.get("timestamp") or trade.get("close_time", "")
                if trade_time_str:
                    try:
                        if isinstance(trade_time_str, str):
                            trade_time = datetime.fromisoformat(trade_time_str.replace('Z', '+00:00'))
                        else:
                            trade_time = datetime.fromtimestamp(trade_time_str)
                        
                        if start_date and trade_time < start_date:
                            continue
                        if end_date and trade_time > end_date:
                            continue
                        filtered.append(trade)
                    except Exception:
                        continue
            trades = filtered
        
        return trades
    
    def export_csv(self, output_file: str, symbol: Optional[str] = None) -> None:
        """
        Export trades to CSV file.
        
        Args:
            output_file: Output CSV file path
            symbol: Filter by symbol (optional)
        """
        try:
            import csv
            
            trades = self.get_trades(symbol=symbol)
            
            if not trades:
                logger.warning("No trades to export")
                return
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                # Get all unique keys
                fieldnames = set()
                for trade in trades:
                    fieldnames.update(trade.keys())
                fieldnames = sorted(list(fieldnames))
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(trades)
            
            logger.info(f"Exported {len(trades)} trades to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}", exc_info=True)
    
    def export_json(self, output_file: str, symbol: Optional[str] = None) -> None:
        """
        Export trades to JSON file.
        
        Args:
            output_file: Output JSON file path
            symbol: Filter by symbol (optional)
        """
        try:
            trades = self.get_trades(symbol=symbol)
            
            if not trades:
                logger.warning("No trades to export")
                return
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "export_date": datetime.now().isoformat(),
                "total_trades": len(trades),
                "trades": trades
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
            
            logger.info(f"Exported {len(trades)} trades to {output_path}")
            
        except Exception as e:
            logger.error(f"Error exporting JSON: {e}", exc_info=True)
    
    def get_statistics(self) -> Dict:
        """
        Get trade statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self.trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "average_pnl": 0.0,
                "best_trade": None,
                "worst_trade": None
            }
        
        winning = [t for t in self.trades if t.get("net_pnl", 0) > 0]
        losing = [t for t in self.trades if t.get("net_pnl", 0) < 0]
        
        total_pnl = sum(t.get("net_pnl", 0) for t in self.trades)
        
        best_trade = max(self.trades, key=lambda t: t.get("net_pnl", 0), default=None)
        worst_trade = min(self.trades, key=lambda t: t.get("net_pnl", 0), default=None)
        
        return {
            "total_trades": len(self.trades),
            "winning_trades": len(winning),
            "losing_trades": len(losing),
            "win_rate": (len(winning) / len(self.trades) * 100) if self.trades else 0.0,
            "total_pnl": total_pnl,
            "average_pnl": total_pnl / len(self.trades) if self.trades else 0.0,
            "best_trade": best_trade,
            "worst_trade": worst_trade
        }
    
    def clear_trades(self) -> None:
        """Clear all trades (use with caution)."""
        self.trades = []
        self._save_trades()
        logger.warning("All trades cleared")

