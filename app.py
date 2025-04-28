import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify
from config import SERVER_HOST, FLASK_PORT
from bot import setup_bot
import threading

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "binary_trading_signals_bot_secret")

# In-memory storage for bot status
bot_status = {
    "running": False,
    "authenticated_users": 0,
    "signals_sent": 0,
    "last_updated": None
}

@app.route("/")
def index():
    """Main page route"""
    from config import AUTHENTICATED_USERS
    # Update the status from the config
    bot_status["authenticated_users"] = len(AUTHENTICATED_USERS)
    bot_status["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return render_template("index.html", bot_status=bot_status)

@app.route("/status")
def status():
    """API endpoint to get bot status"""
    from config import AUTHENTICATED_USERS
    # Update the status from the config
    bot_status["authenticated_users"] = len(AUTHENTICATED_USERS)
    bot_status["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return jsonify({
        "status": "online" if bot_status["running"] else "offline",
        "authenticated_users": bot_status["authenticated_users"],
        "signals_sent": bot_status["signals_sent"],
        "last_updated": bot_status["last_updated"]
    })

@app.route("/test-signals")
def test_signals():
    """Test endpoint to check signal processing"""
    from utils import fetch_trading_signals, format_signal_message
    
    # Create some sample signals to test with, in case the API doesn't return any
    sample_signals = [
        {
            "asset": "EUR/USD",
            "direction": "CALL",
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "original_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "converted_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        },
        {
            "asset": "BTC/USD",
            "direction": "PUT",
            "time": (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "original_time": (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S"),
            "converted_time": (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        }
    ]
    
    # First try to get real signals
    real_signals = fetch_trading_signals()
    
    # Use real signals if available, otherwise use samples
    signals = real_signals if real_signals else sample_signals
    
    # Format the signals
    formatted_signals = [format_signal_message(signal) for signal in signals]
    
    # Return both raw and formatted signals for testing
    return jsonify({
        "raw_signals": signals,
        "formatted_signals": formatted_signals
    })

def run_flask_app():
    """Run the Flask app"""
    app.run(host=SERVER_HOST, port=FLASK_PORT, debug=True, use_reloader=False)

def start_bot_thread():
    """Start the Telegram bot in a separate thread"""
    updater = setup_bot()
    if updater:
        bot_status["running"] = True
        logger.info("Starting bot in background thread...")
        updater.start_polling()
    else:
        logger.error("Bot setup failed!")
