import hashlib
import logging
import pytz
from datetime import datetime, timedelta
import requests
from config import (
    SOURCE_TIMEZONE,
    TARGET_TIMEZONE,
    SIGNALS_API_URL,
    SIGNALS_API_KEY,
    MASTER_KEY,
    VALID_KEYS,
    USED_KEYS,
    PERMANENT_KEY
)

logger = logging.getLogger(__name__)

def verify_private_key(private_key):
    """
    Verify if a private key is valid and check if it's a single-use key.
    
    Args:
        private_key (str): The private key to verify
    
    Returns:
        bool: True if the key is valid, False otherwise
    """
    if not private_key:
        return False
    
    # Accept the permanent VIP key that never expires
    if private_key == PERMANENT_KEY:
        return True
    
    # Check if key is in the valid keys list and not previously used
    if private_key in VALID_KEYS and private_key not in USED_KEYS:
        # Mark the key as used so it can't be used again
        USED_KEYS.add(private_key)
        logger.info(f"Single-use key '{private_key}' verified and marked as used")
        return True
    
    # Check if key was already used
    if private_key in USED_KEYS:
        logger.warning(f"Attempt to use already used key: {private_key}")
        return False
        
    try:
        # Legacy method - using hash validation as a fallback
        # Create a hash of the private key with the master key
        key_hash = hashlib.sha256((private_key + MASTER_KEY).encode()).hexdigest()
        
        # Simple validation - checking if the hash starts with '0'
        return key_hash.startswith('0')
    except Exception as e:
        logger.error(f"Error verifying private key: {e}")
        return False

def convert_timezone(timestamp, from_tz=SOURCE_TIMEZONE, to_tz=TARGET_TIMEZONE):
    """
    Convert a timestamp from one timezone to another.
    
    Args:
        timestamp (str or datetime): The timestamp to convert
        from_tz (str): Source timezone
        to_tz (str): Target timezone
    
    Returns:
        datetime: The converted timestamp
    """
    try:
        # Parse the timestamp if it's a string
        if isinstance(timestamp, str):
            try:
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S%z")
            except ValueError:
                dt = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                # Handle UTC+6:00 format
                if from_tz == "UTC+6:00":
                    from_tz = pytz.FixedOffset(6 * 60)
                    dt = from_tz.localize(dt)
        else:
            dt = timestamp
            
        # If timestamp doesn't have timezone info and from_tz is specified
        if dt.tzinfo is None and from_tz:
            if isinstance(from_tz, str):
                if from_tz.startswith("UTC+"):
                    offset_hours = int(from_tz.replace("UTC+", "").split(":")[0])
                    from_tz = pytz.FixedOffset(offset_hours * 60)
                else:
                    from_tz = pytz.timezone(from_tz)
            dt = from_tz.localize(dt)
            
        # Convert to target timezone
        if isinstance(to_tz, str):
            to_timezone = pytz.timezone(to_tz)
        else:
            to_timezone = to_tz
            
        return dt.astimezone(to_timezone)
    except Exception as e:
        logger.error(f"Error converting timezone: {e}")
        return timestamp

def fetch_trading_signals():
    """
    Fetch trading signals from the API.
    
    Returns:
        list: List of signal dictionaries or empty list if failed
    """
    try:
        headers = {"Authorization": f"Bearer {SIGNALS_API_KEY}"} if SIGNALS_API_KEY else {}
        
        response = requests.get(SIGNALS_API_URL, headers=headers, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"API Response: {data}")
        
        # The API returns a dictionary with 'signals', 'data', or directly an array of signals
        if isinstance(data, dict):
            if 'signals' in data:
                signals = data['signals']
            elif 'data' in data:
                signals = data['data']
            else:
                # Try to find a key that might contain signals
                potential_signal_keys = [k for k, v in data.items() if isinstance(v, list) and len(v) > 0]
                if potential_signal_keys:
                    signals = data[potential_signal_keys[0]]
                else:
                    signals = []
            logger.info(f"Successfully extracted {len(signals)} signals from API response")
        else:
            signals = data if isinstance(data, list) else []
            logger.info(f"Using full response as signals list with {len(signals)} items")
        
        # Get current date in UTC+6 (SOURCE_TIMEZONE)
        source_tz = pytz.FixedOffset(6 * 60)  # UTC+6:00
        current_date = datetime.now(source_tz).strftime("%Y-%m-%d")
        
        # Filter and process signals
        current_time = datetime.now(pytz.timezone(TARGET_TIMEZONE))
        processed_signals = []
        
        logger.info(f"Current time in {TARGET_TIMEZONE}: {current_time}")
        
        for signal in signals:
            try:
                # Adapt to different possible field names based on API changes
                entry_time = None
                
                # Try different field names for time
                time_fields = ["entrada", "time", "entry", "entry_time", "hora", "horario", "time_entry"]
                for field in time_fields:
                    if field in signal and signal[field]:
                        entry_time = signal[field]
                        break
                
                if not entry_time:
                    logger.warning(f"Signal missing entry time: {signal}")
                    continue
                
                # Handle different time formats
                time_format = "%H:%M"
                if ":" not in entry_time:
                    # Handle numeric format (e.g., 1430 for 14:30)
                    if len(entry_time) == 4 and entry_time.isdigit():
                        entry_time = f"{entry_time[:2]}:{entry_time[2:]}"
                
                # Create a full datetime string with today's date and the entry time
                # The API provides time in HH:MM format in UTC+6:00 timezone
                full_time_str = f"{current_date} {entry_time}"
                logger.debug(f"Created full time string: {full_time_str}")
                
                # Parse the time and set the timezone to UTC+6:00
                dt = datetime.strptime(full_time_str, "%Y-%m-%d %H:%M")
                signal_time = source_tz.localize(dt)
                logger.debug(f"Original signal time (UTC+6:00): {signal_time}")
                
                # Convert to target timezone (GMT+5:30)
                target_tz = pytz.timezone(TARGET_TIMEZONE)
                signal_time_converted = signal_time.astimezone(target_tz)
                logger.debug(f"Converted signal time ({TARGET_TIMEZONE}): {signal_time_converted}")
                
                # Skip expired signals
                if signal_time_converted < current_time:
                    logger.info(f"Skipping expired signal: {entry_time}, current time: {current_time}")
                    continue
                
                # Try to find asset and direction with different possible field names
                asset = None
                asset_fields = ["ativos", "asset", "currency", "par", "pair", "symbol", "moeda"]
                for field in asset_fields:
                    if field in signal and signal[field]:
                        asset = signal[field]
                        break
                
                if not asset:
                    asset = "Unknown"
                
                direction = None
                direction_fields = ["direcao_principal", "direction", "direcao", "operation", "tipo", "type"]
                for field in direction_fields:
                    if field in signal and signal[field]:
                        direction = signal[field]
                        break
                
                if not direction:
                    direction = "Unknown"
                
                # Create a clean processed signal object
                processed_signal = {
                    "asset": asset,
                    "direction": direction,
                    "original_time": entry_time,
                    "converted_time": signal_time_converted.strftime("%Y-%m-%d %H:%M:%S %Z")
                }
                
                processed_signals.append(processed_signal)
                logger.info(f"Added signal: {processed_signal}")
            except Exception as e:
                logger.error(f"Error processing signal: {e}")
                logger.error(f"Problematic signal: {signal}")
                continue
        
        logger.info(f"Total processed signals: {len(processed_signals)}")
        return processed_signals
    except requests.RequestException as e:
        logger.error(f"Error fetching signals from API: {e}")
        return []
    except ValueError as e:
        logger.error(f"Error parsing API response: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching signals: {e}")
        return []

def generate_new_key():
    """
    Generate a new unique single-use key and add it to the valid keys list.
    
    Returns:
        str: The newly generated key
    """
    try:
        import random
        import string
        
        # Generate a random key with prefix
        prefix = random.choice(["VIP", "SIGNAL", "TRADE", "BINARY", "FOREX", "CRYPTO"])
        numbers = ''.join(random.choices(string.digits, k=3))
        letters = ''.join(random.choices(string.ascii_uppercase, k=3))
        
        # Combine the parts to create a unique key
        new_key = f"{prefix}{letters}{numbers}"
        
        # Add the key to valid keys if it's not already there
        if new_key not in VALID_KEYS and new_key not in USED_KEYS:
            VALID_KEYS.append(new_key)
            logger.info(f"Added new single-use key: {new_key}")
            return new_key
        else:
            # Try again if there's a collision (very unlikely but possible)
            return generate_new_key()
    except Exception as e:
        logger.error(f"Error generating new key: {e}")
        return None

def get_all_valid_keys():
    """
    Get a list of all valid keys that haven't been used yet.
    
    Returns:
        list: List of valid unused keys
    """
    unused_keys = [key for key in VALID_KEYS if key not in USED_KEYS]
    return unused_keys

def format_signal_message(signal, is_expiry=False):
    """
    Format a trading signal into a readable message.
    
    Args:
        signal (dict): The signal data
        is_expiry (bool): Whether this is an expiry message
        
    Returns:
        str: Formatted message
    """
    try:
        # Log the signal being processed to debug
        logger.info(f"Formatting signal: {signal}")
        
        # Get asset from "ativos" or fallback to "asset" field
        asset = signal.get("asset", "Unknown")
        
        # Get direction from "direcao_principal" or fallback to "direction" field
        direction = signal.get("direction", "Unknown")
        
        # Get the converted time
        signal_time = signal.get("converted_time", "Unknown")
        
        # Format the direction - handle both uppercase and lowercase variants
        direction_lower = direction.lower() if isinstance(direction, str) else "unknown"
        
        if "call" in direction_lower or "compra" in direction_lower or "alta" in direction_lower:
            direction_emoji = "📈"
            direction_text = "CALL"
        elif "put" in direction_lower or "venda" in direction_lower or "baixa" in direction_lower:
            direction_emoji = "📉"
            direction_text = "PUT"
        else:
            direction_emoji = "❓"
            direction_text = direction.upper() if isinstance(direction, str) else "UNKNOWN"
            
        if is_expiry:
            message = f"""
⚠️ *SIGNAL EXPIRED* ⚠️

Asset: *{asset}*
Direction: *{direction_text}* {direction_emoji}
Entry Time: *{signal_time}*

⏳ Please wait for the next signal alert.
⚡ New signals are posted regularly.

_Contact @BILLIONAIREBOSS101 for VIP access._
            """
        else:
            # Generate an MTG 1-step value
            mtg_value = 85  # Fixed value for 1-step system
            
            message = f"""
🔔 *NEW TRADING SIGNAL* 🔔

Asset: *{asset}*
Direction: *{direction_text}* {direction_emoji}
Entry Time: *{signal_time}*
MTG 1-Step System: *{mtg_value}%* 📊

_Trade responsibly and manage your risk!_
            """
        
        return message
    except Exception as e:
        logger.error(f"Error formatting signal message: {e}")
        return "Error formatting signal"
