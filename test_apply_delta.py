#!/usr/bin/env python3
"""Test buffer delta application."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_apply_delta():
    print("1. Starting apply delta test...")
    
    try:
        from questionary_extended.core.buffer_manager import ANSIBufferManager
        from questionary_extended.core.spatial import SpaceRequirement, BufferDelta
        
        print("2. Creating buffer manager...")
        buffer_mgr = ANSIBufferManager(terminal_height=20)
        
        print("3. Allocating space...")
        space_req = SpaceRequirement(min_lines=3, current_lines=3, max_lines=5, preferred_lines=3)
        position = buffer_mgr.allocate_space("test_element", space_req)
        
        print("4. Creating buffer delta...")
        delta = BufferDelta(
            line_updates=[(0, "Line 1: Test content"), (1, "Line 2: More content")],
            space_change=0,
            clear_lines=[]
        )
        
        print("5. About to apply buffer delta...")
        buffer_mgr.apply_buffer_delta(position, delta)
        print("6. Buffer delta applied successfully!")
        
        print("7. Test complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_apply_delta()