"""
Health check endpoint for Render free tier.
Keeps service awake and allows bot to run.
"""
from flask import Flask
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

app = Flask(__name__)

# Bot running flag
bot_running = False
bot_thread = None
bot_error = None

def start_bot():
    """Start trading bot in background thread."""
    global bot_running, bot_error
    try:
        # Import after path setup
        from ai_trading_bot.main import main
        bot_running = True
        bot_error = None
        main()
    except Exception as e:
        import traceback
        bot_error = str(e)
        print(f"Bot error: {e}")
        traceback.print_exc()
        bot_running = False

@app.route('/')
def index():
    """Root endpoint - health check."""
    status = "running" if bot_running else "starting"
    response = {
        'status': 'ok',
        'bot': status,
        'service': 'Badshah AI Trading Bot'
    }
    if bot_error:
        response['error'] = bot_error
    return response, 200

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

if __name__ == '__main__':
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 10000))
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=False)

