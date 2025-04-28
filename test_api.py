"""
Test script to verify API connection and field mappings.
"""
import logging
import json
import requests
from utils import fetch_trading_signals, format_signal_message
from config import SIGNALS_API_URL, SIGNALS_API_KEY

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_api_connection():
    """Test direct API connection and print response"""
    try:
        headers = {"Authorization": f"Bearer {SIGNALS_API_KEY}"} if SIGNALS_API_KEY else {}
        
        logger.info(f"Connecting to API: {SIGNALS_API_URL}")
        response = requests.get(SIGNALS_API_URL, headers=headers, timeout=10)
        
        # Print status code
        logger.info(f"API Response Status: {response.status_code}")
        
        # Try to parse as JSON
        try:
            data = response.json()
            logger.info(f"Successfully parsed JSON response")
            
            # Check if it's a list or dictionary
            if isinstance(data, list):
                logger.info(f"Response is a list with {len(data)} items")
                
                # Check the first few items
                for i, item in enumerate(data[:3]):
                    logger.info(f"Item {i+1} keys: {item.keys()}")
                    logger.info(f"Item {i+1} data: {json.dumps(item, indent=2)}")
            else:
                logger.info(f"Response is a dictionary with keys: {data.keys()}")
                logger.info(f"Response data: {json.dumps(data, indent=2)}")
                
        except ValueError:
            logger.error("Failed to parse response as JSON")
            logger.info(f"Response content: {response.text[:500]}...")
            
    except Exception as e:
        logger.error(f"Error testing API connection: {e}")

def test_signal_processing():
    """Test signal processing with fetch_trading_signals function"""
    logger.info("Testing signal processing...")
    
    # Fetch signals using the utility function
    signals = fetch_trading_signals()
    
    if signals:
        logger.info(f"Successfully fetched {len(signals)} signals")
        
        # Display the first few signals
        for i, signal in enumerate(signals[:3]):
            logger.info(f"\nSignal {i+1}:")
            logger.info(f"Raw signal: {signal}")
            
            # Format the signal
            formatted = format_signal_message(signal)
            logger.info(f"Formatted message:\n{formatted}")
    else:
        logger.warning("No signals were fetched or processed")

if __name__ == "__main__":
    print("=== TESTING API CONNECTION ===")
    test_api_connection()
    
    print("\n=== TESTING SIGNAL PROCESSING ===")
    test_signal_processing()