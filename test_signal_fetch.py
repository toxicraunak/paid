"""
Test script to verify signal fetching, timezone conversion and formatting.
"""
import logging
import datetime
import pytz
from utils import format_signal_message, convert_timezone

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_test_signals():
    """Create test signals for demonstration"""
    # Current time in IST (TARGET_TIMEZONE)
    from config import TARGET_TIMEZONE
    target_tz = pytz.timezone(TARGET_TIMEZONE)
    now_in_target = datetime.datetime.now(target_tz)
    
    # Remove timezone information for easier manipulation
    now = now_in_target.replace(tzinfo=None)
    
    # Create timestamps in UTC+6:00 timezone
    source_tz = pytz.FixedOffset(6 * 60)  # UTC+6:00
    
    # Create a signal for 30 minutes ago (expired)
    time1 = source_tz.localize(now - datetime.timedelta(minutes=30))
    
    # Create a signal for 30 minutes from now
    time2 = source_tz.localize(now + datetime.timedelta(minutes=30))
    
    # Create a signal for 1 hour from now
    time3 = source_tz.localize(now + datetime.timedelta(hours=1))
    
    # Create a signal for 2 hours from now
    time4 = source_tz.localize(now + datetime.timedelta(hours=2))
    
    # Create test signals
    signals = [
        {
            "asset": "AAPL",
            "direction": "PUT",
            "time": time1.strftime("%Y-%m-%d %H:%M:%S"),
            "expiry": "5m",
            "status": "expired"  # This should be filtered out
        },
        {
            "asset": "EUR/USD",
            "direction": "CALL",
            "time": time2.strftime("%Y-%m-%d %H:%M:%S"),
            "expiry": "5m",
            "status": "active"
        },
        {
            "asset": "BTC/USD",
            "direction": "PUT",
            "time": time3.strftime("%Y-%m-%d %H:%M:%S"),
            "expiry": "15m",
            "status": "upcoming"
        },
        {
            "asset": "GOLD",
            "direction": "CALL",
            "time": time4.strftime("%Y-%m-%d %H:%M:%S"),
            "expiry": "1h",
            "status": "upcoming"
        }
    ]
    
    return signals

if __name__ == "__main__":
    print("Testing timezone conversion, filtering, and signal formatting...")
    
    # Create test signals
    signals = create_test_signals()
    print(f"Total signals created: {len(signals)}")
    
    # Process signals with timezone conversion
    from config import SOURCE_TIMEZONE, TARGET_TIMEZONE
    processed_signals = []
    filtered_signals = []
    
    # Get current time in target timezone for filtering
    current_time = datetime.datetime.now(pytz.timezone(TARGET_TIMEZONE))
    print(f"Current time in {TARGET_TIMEZONE}: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    for signal in signals:
        # Convert the signal time from UTC+6:00 to GMT+5:30
        original_time = signal["time"]
        converted_time = convert_timezone(original_time, SOURCE_TIMEZONE, TARGET_TIMEZONE)
        
        # Add the original and converted times to the signal
        signal["original_time"] = original_time
        signal["converted_time"] = converted_time.strftime("%Y-%m-%d %H:%M:%S %Z")
        
        processed_signals.append(signal)
        
        # Filter out expired signals
        if converted_time > current_time:
            filtered_signals.append(signal)
    
    # Display all processed signals
    print(f"\nSuccessfully processed {len(processed_signals)} signals.")
    print(f"After filtering out expired signals: {len(filtered_signals)} signals remaining.")
    
    print("\n=== ALL SIGNALS (INCLUDING EXPIRED) ===")
    for i, signal in enumerate(processed_signals, 1):
        print(f"\n--- Signal {i} ---")
        print(f"Asset: {signal['asset']}")
        print(f"Direction: {signal['direction']}")
        print(f"Status: {signal['status']}")
        print(f"Original Time (UTC+6:00): {signal['original_time']}")
        print(f"Converted Time (GMT+5:30): {signal['converted_time']}")
    
    print("\n=== FILTERED SIGNALS (UPCOMING ONLY) ===")
    for i, signal in enumerate(filtered_signals, 1):
        print(f"\n--- Signal {i} ---")
        print(f"Asset: {signal['asset']}")
        print(f"Direction: {signal['direction']}")
        print(f"Status: {signal['status']}")
        print(f"Original Time (UTC+6:00): {signal['original_time']}")
        print(f"Converted Time (GMT+5:30): {signal['converted_time']}")
        
        # Format the signal message
        formatted = format_signal_message(signal)
        print(f"\nFormatted message:\n{formatted}")
        
    print("\nTimezone conversion and filtering test completed!")