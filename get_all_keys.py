#!/usr/bin/env python3
"""
Script to show all available keys for use with the trading signal bot.
"""

from config import VALID_KEYS, USED_KEYS, PERMANENT_KEY
from utils import get_all_valid_keys

def main():
    """Display all keys in a formatted way"""
    # Get unused keys
    unused_keys = get_all_valid_keys()
    
    print("\n=== AVAILABLE SINGLE-USE KEYS ===")
    print("These keys will expire after one use\n")
    
    # Print all unused keys
    for i, key in enumerate(unused_keys, 1):
        print(f"{i}. {key}")
    
    print("\n=== PERMANENT KEY ===")
    print("This key never expires and can be used multiple times\n")
    print(f"PERMANENT: {PERMANENT_KEY}")
    
    # Print summary
    print(f"\nTotal valid single-use keys: {len(VALID_KEYS)}")
    print(f"Total used keys: {len(USED_KEYS)}")
    print(f"Total unused keys: {len(unused_keys)}")
    print("\nThese single-use keys can only be used once. After use, they will expire.")
    print("The permanent key can be used multiple times and never expires.")

if __name__ == "__main__":
    main()