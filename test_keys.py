#!/usr/bin/env python3
"""
Test script to verify the single-use key system functionality.
"""

import logging
import sys
from config import VALID_KEYS, USED_KEYS, PERMANENT_KEY
from utils import verify_private_key, generate_new_key, get_all_valid_keys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def test_key_system():
    """Test the single-use key system"""
    logger.info("=== TESTING SINGLE-USE KEY SYSTEM ===")
    
    # Display initial state
    logger.info(f"Valid keys: {VALID_KEYS}")
    logger.info(f"Used keys: {USED_KEYS}")
    logger.info(f"Permanent key: {PERMANENT_KEY}")
    
    # Test generating new keys
    logger.info("\n=== GENERATING NEW KEYS ===")
    new_keys = []
    for i in range(3):
        key = generate_new_key()
        new_keys.append(key)
        logger.info(f"Generated key {i+1}: {key}")
    
    # Display valid keys after generation
    logger.info(f"\nValid keys after generation: {VALID_KEYS}")
    logger.info(f"Unused keys: {get_all_valid_keys()}")
    
    # Test key verification (single-use keys)
    logger.info("\n=== TESTING SINGLE-USE KEYS ===")
    for i, key in enumerate(new_keys):
        result1 = verify_private_key(key)
        logger.info(f"Key {i+1} first verification: {result1}")
        
        result2 = verify_private_key(key)
        logger.info(f"Key {i+1} second verification: {result2}")
        
        # Should be False because the key is already used
        assert result1 == True, f"First verification of key {key} should succeed"
        assert result2 == False, f"Second verification of key {key} should fail (key already used)"
    
    # Show used keys
    logger.info(f"\nUsed keys after verification: {USED_KEYS}")
    
    # Test permanent key (should always work)
    logger.info("\n=== TESTING PERMANENT KEY ===")
    result1 = verify_private_key(PERMANENT_KEY)
    logger.info(f"Permanent key first verification: {result1}")
    
    result2 = verify_private_key(PERMANENT_KEY)
    logger.info(f"Permanent key second verification: {result2}")
    
    # Should always be True
    assert result1 == True, "Permanent key first verification should succeed"
    assert result2 == True, "Permanent key second verification should succeed"
    
    logger.info("\n=== KEY SYSTEM TEST COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_key_system()