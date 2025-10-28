#!/usr/bin/env python3
"""
Test different buffer manipulation techniques for flicker analysis.
"""

import time
import sys

def test_line_by_line_update():
    """Test smooth line-by-line updates"""
    print("=== Testing Line-by-Line Updates (Should be smooth) ===")
    
    # Setup initial content
    initial_lines = [
        "Header: Navigation Instructions",
        "Line 2: Some content here", 
        "Line 3: More content",
        "Line 4: Footer content"
    ]
    
    for line in initial_lines:
        print(line)
    
    time.sleep(1)
    
    # Update middle lines without flicker
    updates = [
        (2, "Line 2: UPDATED CONTENT <<<"),
        (3, "Line 3: ALSO UPDATED <<<"), 
        (4, "Line 4: CHANGED FOOTER <<<")
    ]
    
    for line_num, new_content in updates:
        # Direct line positioning + clear + write
        print(f"\x1b[{line_num};1H\x1b[2K{new_content}", end="")
        time.sleep(0.5)  # Slow for visibility
    
    print(f"\x1b[{len(initial_lines) + 2};1H")  # Move cursor to end

def test_space_expansion():
    """Test space expansion with line insertion"""
    print("\n=== Testing Space Expansion (Minimal flicker) ===")
    
    # Setup initial content
    initial_lines = [
        "Header Section",
        "Body Section Line 1",
        "Body Section Line 2", 
        "Footer Section"
    ]
    
    for line in initial_lines:
        print(line)
        
    time.sleep(1)
    
    # Insert 2 lines after header (line 1)
    print(f"\x1b[2;1H\x1b[2L", end="")  # Insert 2 lines at position 2
    
    # Fill the new space
    print(f"\x1b[2;1H\x1b[2KNew Header Line 1", end="")
    print(f"\x1b[3;1H\x1b[2KNew Header Line 2", end="")
    
    print(f"\x1b[{len(initial_lines) + 4};1H")  # Move cursor to end

def test_full_screen_clear():
    """Test full screen clear (Will flicker badly)"""
    print("\n=== Testing Full Screen Clear (Will flicker) ===")
    
    # Setup content
    for i in range(10):
        print(f"Line {i+1}: Some content here")
    
    time.sleep(1)
    
    # Clear and redraw - FLICKER ALERT
    print("\x1b[2J\x1b[H", end="")  # Clear screen + home
    
    for i in range(10):
        print(f"Line {i+1}: UPDATED content here")

if __name__ == "__main__":
    print("Buffer Flicker Analysis")
    print("Watch carefully for screen flicker during each test...")
    print()
    
    try:
        test_line_by_line_update()
        time.sleep(2)
        
        test_space_expansion() 
        time.sleep(2)
        
        test_full_screen_clear()
        
    except KeyboardInterrupt:
        print("\nTest interrupted")
        sys.exit(0)