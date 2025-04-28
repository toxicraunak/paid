#!/usr/bin/env python3
"""
Test script to simulate user authentication and verify persistent authentication.
"""

import logging
import sys
from config import AUTHENTICATED_USERS, VALID_KEYS, USED_KEYS, PERMANENT_KEY
from utils import verify_private_key

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def test_authentication():
    """Test bot authentication with various user IDs"""
    logger.info("=== TESTING BOT AUTHENTICATION SYSTEM ===")
    
    # Initial state
    logger.info(f"Initial authenticated users: {AUTHENTICATED_USERS}")
    
    # Test users
    test_users = [
        {"id": 123456, "name": "User 1", "key": VALID_KEYS[0]},
        {"id": 789012, "name": "User 2", "key": VALID_KEYS[1]},
        {"id": 345678, "name": "User 3", "key": PERMANENT_KEY},
        {"id": 901234, "name": "User 4", "key": "invalid_key"},
    ]
    
    # Simulate authentication for each user
    for user in test_users:
        logger.info(f"\nAttempting authentication for {user['name']} (ID: {user['id']})")
        
        # Check if user is already authenticated (should be False initially)
        is_authenticated = user['id'] in AUTHENTICATED_USERS
        logger.info(f"Already authenticated: {is_authenticated}")
        
        # Try to authenticate with the key
        if verify_private_key(user['key']):
            # Add user to authenticated users
            AUTHENTICATED_USERS.add(user['id'])
            logger.info(f"Authentication successful for {user['name']} with key: {user['key']}")
        else:
            logger.info(f"Authentication failed for {user['name']} with key: {user['key']}")
        
        # Verify authentication status after attempt
        is_authenticated = user['id'] in AUTHENTICATED_USERS
        logger.info(f"Authenticated after attempt: {is_authenticated}")
    
    # Show final state
    logger.info(f"\nFinal authenticated users: {AUTHENTICATED_USERS}")
    logger.info(f"Used keys: {USED_KEYS}")
    
    # Simulation of user coming back to the bot later
    logger.info("\n=== SIMULATING RETURN VISITS ===")
    for user in test_users:
        is_authenticated = user['id'] in AUTHENTICATED_USERS
        if is_authenticated:
            logger.info(f"{user['name']} (ID: {user['id']}) returns to the bot - Already authenticated")
            # The bot would not ask for a key again
            logger.info("Command: /signals - Access granted without asking for key")
        else:
            logger.info(f"{user['name']} (ID: {user['id']}) returns to the bot - Not authenticated")
            logger.info("Command: /signals - Bot asks for authentication")
    
    logger.info("\n=== AUTHENTICATION TEST COMPLETED ===")

if __name__ == "__main__":
    test_authentication()