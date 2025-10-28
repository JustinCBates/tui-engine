#!/usr/bin/env python3
"""
Simple ANSI test to verify terminal capability.
"""

import sys
import time

def test_basic_ansi():
    """Test if basic ANSI escape sequences work"""
    print("Testing basic ANSI support...")
    print("Line 1: Initial content")
    print("Line 2: Initial content")
    print("Line 3: Initial content")
    
    # Flush to ensure output
    sys.stdout.flush()
    time.sleep(1)
    
    # Try to move cursor up and overwrite line 2
    print("\x1b[2A", end="")  # Move up 2 lines
    print("\x1b[2K", end="")  # Clear line
    print("Line 2: UPDATED!", end="")  # Write new content
    print("\x1b[2B", end="")  # Move down 2 lines
    
    sys.stdout.flush()
    print("\nDid line 2 get updated in place? (y/n)")

def test_absolute_positioning():
    """Test absolute cursor positioning"""
    print("\nTesting absolute positioning...")
    for i in range(5):
        print(f"Line {i+1}: Original content")
    
    sys.stdout.flush()
    time.sleep(1)
    
    # Try to update line 3 using absolute positioning
    print("\x1b[3;1H", end="")  # Go to line 3, column 1
    print("\x1b[2K", end="")    # Clear line
    print("Line 3: ABSOLUTELY POSITIONED!", end="")
    print("\x1b[6;1H", end="")  # Go to line 6
    
    sys.stdout.flush()
    print("Did line 3 get updated using absolute positioning? (y/n)")

if __name__ == "__main__":
    print("=== ANSI Terminal Capability Test ===")
    print("Watch carefully to see if text updates in place...")
    print()
    
    test_basic_ansi()
    test_absolute_positioning()
    
    print("\nIf you saw text updating in place, ANSI works!")
    print("If you just saw linear output, ANSI is not working properly.")