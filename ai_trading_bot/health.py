"""
Health check endpoint for Render free tier.
Keeps service awake and allows bot to run.
"""
from flask import Flask, render_template, jsonify
import threading
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent.absolute()
parent_dir = current_dir.parent.absolute()

if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Change to correct directory
try:
    os.chdir(current_dir)
except Exception:
    # If chdir fails, continue anyway (some environments may not allow it)
    pass

app = Flask(__name__, template_folder=str(current_dir / 'templates'))

# Bot running flag
bot_running = False
bot_thread = None
bot_error = None
bot_started = False
bot_instance = None  # Store bot instance for API access

def start_bot():
    """Start trading bot in background thread."""
    global bot_running, bot_error, bot_instance
    try:
        # Import after path setup
        from ai_trading_bot.main import TradingBot
        bot_running = True
        bot_error = None
        
        # Create bot instance and store it globally for API access
        bot_instance = TradingBot()
        
        # Start bot (this will block, so it runs in a thread)
        bot_instance.start()
    except Exception as e:
        import traceback
        bot_error = str(e)
        print(f"Bot error: {e}")
        traceback.print_exc()
        bot_running = False
        bot_instance = None

# Start bot thread when module is imported (works with gunicorn)
def ensure_bot_started():
    """Ensure bot thread is started (only once)."""
    global bot_thread, bot_started
    if not bot_started:
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        bot_started = True

# Start bot when Flask app is created
ensure_bot_started()

@app.route('/')
def index():
    """Root endpoint - dashboard."""
    return render_template('dashboard.html')

@app.route('/health')
def health():
    """Health check endpoint."""
    response = {
        'status': 'healthy',
        'bot': 'running' if bot_running else 'starting'
    }
    if bot_error:
        response['error'] = bot_error
    return response, 200

@app.route('/status')
def status():
    """Detailed status."""
    return {
        'status': 'ok',
        'bot_running': bot_running,
        'service': 'trading_bot',
        'error': bot_error if bot_error else None
    }, 200

@app.route('/trades')
def get_trades():
    """Get trade history."""
    try:
        from ai_trading_bot.utils.trade_storage import TradeStorage
        storage = TradeStorage("trades.json")
        trades = storage.get_trades()
        stats = storage.get_statistics()
        
        return {
            'status': 'ok',
            'total_trades': len(trades),
            'statistics': stats,
            'recent_trades': trades[-10:] if trades else []  # Last 10 trades
        }, 200
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }, 500

@app.route('/pnl')
def get_pnl():
    """Get current P&L summary."""
    try:
        # Try to get PnL from bot if available
        from ai_trading_bot.utils.trade_storage import TradeStorage
        storage = TradeStorage("trades.json")
        stats = storage.get_statistics()
        
        return {
            'status': 'ok',
            'total_pnl': stats.get('total_pnl', 0.0),
            'total_trades': stats.get('total_trades', 0),
            'win_rate': stats.get('win_rate', 0.0),
            'winning_trades': stats.get('winning_trades', 0),
            'losing_trades': stats.get('losing_trades', 0),
            'average_pnl': stats.get('average_pnl', 0.0),
            'best_trade': stats.get('best_trade', {}),
            'worst_trade': stats.get('worst_trade', {})
        }, 200
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }, 500

@app.route('/api/status')
def api_status():
    """Get bot status with current metrics."""
    try:
        if bot_instance and hasattr(bot_instance, 'risk_manager'):
            # Get current prices for all open positions
            current_prices = {}
            open_positions = bot_instance.risk_manager.get_open_positions()
            for symbol in open_positions.keys():
                try:
                    price_data = bot_instance._get_market_data(symbol)
                    if price_data and "current_price" in price_data:
                        current_prices[symbol] = price_data["current_price"]
                except Exception:
                    pass
            
            capital = bot_instance.risk_manager.get_current_capital()
            equity = bot_instance.risk_manager.get_current_equity(current_prices)
            pnl = bot_instance.risk_manager.get_total_pnl(current_prices)
            drawdown = bot_instance.risk_manager.get_drawdown_pct(current_prices)
            open_positions_count = len(open_positions)
            total_trades = len(bot_instance.risk_manager.get_trade_history())
            
            # Calculate PnL percentage
            initial_capital = bot_instance.risk_manager.initial_capital
            pnl_pct = (pnl / initial_capital * 100) if initial_capital > 0 else 0.0
            
            return {
                'status': 'ok',
                'bot_running': bot_running,
                'capital': capital,
                'equity': equity,
                'pnl': pnl,
                'pnl_pct': pnl_pct,
                'drawdown': drawdown,
                'open_positions_count': open_positions_count,
                'total_trades': total_trades
            }, 200
        else:
            return {
                'status': 'ok',
                'bot_running': bot_running,
                'capital': 0.0,
                'equity': 0.0,
                'pnl': 0.0,
                'pnl_pct': 0.0,
                'drawdown': 0.0,
                'open_positions_count': 0,
                'total_trades': 0
            }, 200
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }, 500

@app.route('/api/positions')
def api_positions():
    """Get open positions with current prices."""
    try:
        if bot_instance and hasattr(bot_instance, 'risk_manager'):
            open_positions = bot_instance.risk_manager.get_open_positions()
            positions_list = []
            
            for symbol, position in open_positions.items():
                try:
                    # Get current price
                    price_data = bot_instance._get_market_data(symbol)
                    current_price = price_data.get("current_price", position.get("entry_price", 0)) if price_data else position.get("entry_price", 0)
                    
                    # Calculate unrealized P&L
                    entry_price = position.get("entry_price", 0)
                    size = position.get("size", 0)
                    action = position.get("action", "LONG")
                    
                    if action == "LONG":
                        unrealized_pnl = (current_price - entry_price) * size
                    elif action == "SHORT":
                        unrealized_pnl = (entry_price - current_price) * size
                    else:
                        unrealized_pnl = 0.0
                    
                    entry_cost = position.get("entry_cost", entry_price * size)
                    unrealized_pnl_pct = (unrealized_pnl / entry_cost * 100) if entry_cost > 0 else 0.0
                    
                    positions_list.append({
                        'symbol': symbol,
                        'action': action,
                        'size': size,
                        'entry_price': entry_price,
                        'current_price': current_price,
                        'unrealized_pnl': unrealized_pnl,
                        'unrealized_pnl_pct': unrealized_pnl_pct,
                        'stop_loss': position.get("stop_loss", 0),
                        'take_profit': position.get("take_profit", 0)
                    })
                except Exception as e:
                    # Skip positions that can't be processed
                    continue
            
            return {
                'status': 'ok',
                'positions': positions_list
            }, 200
        else:
            return {
                'status': 'ok',
                'positions': []
            }, 200
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }, 500

if __name__ == '__main__':
    # Bot already started by ensure_bot_started() above
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 10000))
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)

