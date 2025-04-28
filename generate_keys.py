#!/usr/bin/env python3
"""
Script to generate a batch of single-use keys for the trading bot.
"""

import sys
from utils import generate_new_key, get_all_valid_keys
from config import VALID_KEYS, USED_KEYS

def main():
    """Generate a batch of single-use keys"""
    # Get the count from command line args or default to 20
    count = 20
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("Please provide a valid number of keys to generate.")
            return
    
    # Generate the specified number of keys
    generated_keys = []
    for _ in range(count):
        key = generate_new_key()
        if key:
            generated_keys.append(key)
    
    # Print all keys
    print(f"\n=== GENERATED {len(generated_keys)} SINGLE-USE KEYS ===\n")
    for i, key in enumerate(generated_keys, 1):
        print(f"{i}. {key}")
    
    # Print summary
    print(f"\nTotal valid keys: {len(VALID_KEYS)}")
    print(f"Total used keys: {len(USED_KEYS)}")
    print(f"Total unused keys: {len(get_all_valid_keys())}")
    print("\nThese keys can only be used once. After use, they will expire.")

if __name__ == "__main__":
    main()