#!/usr/bin/env python3
"""Test buffer manager allocation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_allocation():
    print("1. Starting allocation test...")
    
    try:
        from questionary_extended.core.buffer_manager import ANSIBufferManager
        from questionary_extended.core.spatial import SpaceRequirement
        
        print("2. Creating buffer manager...")
        buffer_mgr = ANSIBufferManager(terminal_height=20)
        
        print("3. Creating space requirement...")
        space_req = SpaceRequirement(min_lines=3, current_lines=3, max_lines=5, preferred_lines=3)
        
        print("4. About to allocate space...")
        position = buffer_mgr.allocate_space("test_element", space_req)
        print("5. Space allocation successful!")
        print(f"   Position: start={position.start_line}, allocated={position.allocated_lines}")
        
        print("6. Test complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_allocation()