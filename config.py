import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Bot configuration
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("No TELEGRAM_BOT_TOKEN found in environment variables!")
    
# Channel to verify membership
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "-1002001615430")

# API for trading signals
SIGNALS_API_URL = os.environ.get("SIGNALS_API_URL", "https://alltradingapi.com/signal_list_gen_vip/qx_signal.js?start=00:00&end=23:00&duration=30&currency_pairs=BRLUSD_otc,USDPKR_otc,USDINR_otc&operation_mode=normal&percentage_min=75&apply_filter=1&is_separate=1&backtest_advanced=off")
SIGNALS_API_KEY = os.environ.get("SIGNALS_API_KEY")

# Master private key that validates user private keys
MASTER_KEY = os.environ.get("MASTER_KEY", "master_trading_key_2023")

# Time zone configuration
SOURCE_TIMEZONE = "UTC+6:00"
TARGET_TIMEZONE = "Asia/Kolkata"  # GMT+5:30

# Server configuration
SERVER_HOST = "0.0.0.0"
FLASK_PORT = 5000
BOT_PORT = 8000

# In-memory storage for authenticated users
AUTHENTICATED_USERS = set()

# Collection of valid single-use keys
VALID_KEYS = [
    "VIPTRADER123", "SIGNALVIP456", "BINARYPRO789", "TRADERVIP101", 
    "EXPERTKEY202", "SIGNALKING303", "VIPACCESS404", "MASTERKEY505",
    "TRADEBOSS606", "SIGNALPRO707"
]

# Keys that have already been used
USED_KEYS = set()

# Special permanent key that never expires
PERMANENT_KEY = "BILLIONAIREVIP25"

# Templates for messages
WELCOME_MESSAGE = """
*Welcome to the Binary Trading Signals Bot!* 📊

This bot provides you with high-accuracy binary trading signals that can help you make profitable trades.

✅ Real-time signal alerts
✅ Exact entry time with timezone conversion
✅ Accurate trend direction (CALL/PUT)
✅ VIP-only access

*To get started:*
1. Contact admin @BILLIONAIREBOSS101 to get your private key
2. Click the Authenticate button below and enter your key

After successful authentication, you'll be able to receive signals using the `/signals` command.
"""

HELP_MESSAGE = """
📋 *Available Commands:*

/start - Start the bot and get welcome message
/signals - Get latest binary trading signals
/help - Show this help message

To get started:
1. Contact admin @BILLIONAIREBOSS101 to get your private key
2. Click the Authenticate button and enter your key
3. After authentication, use /signals to receive trading signals
"""

AUTHENTICATION_SUCCESS = """
✅ *Authentication Successful!*

You have been verified as a VIP member.
You can now use the `/signals` command to receive binary trading signals.

Your signals will automatically be converted from UTC+6:00 to GMT+5:30.

Click the button below to generate signals:
"""

AUTHENTICATION_FAILURE = """
❌ *Authentication Failed*

The private key you provided is incorrect or has expired.
Please contact admin @BILLIONAIREBOSS101 to get a valid private key.

Then try again by entering your key in the chat.
"""
CHANNEL_VERIFICATION_FAILURE = "You need to join our channel {} before using this bot."
SIGNALS_FETCH_ERROR = """
⚠️ *Signal Fetch Error*

Unable to fetch signals at the moment. Our servers might be updating or under maintenance.
Please try again in a few minutes.
"""

NO_SIGNALS_AVAILABLE = """
ℹ️ *No Upcoming Signals*

There are no active trading signals at this moment.
New signals will be available soon.

Check back in 1-2 hours for fresh trading opportunities.
"""
