#!/usr/bin/env python3
"""Simple buffer manager test."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from questionary_extended.core.buffer_manager import ANSIBufferManager
from questionary_extended.core.spatial import SpaceRequirement, BufferDelta

def test_buffer_manager():
    """Test buffer manager directly."""
    
    print("=== Testing Buffer Manager ===")
    
    try:
        # Create buffer manager
        buffer_mgr = ANSIBufferManager(terminal_height=20)
        print("Buffer manager created")
        
        # Allocate space
        space_req = SpaceRequirement(min_lines=3, current_lines=3, max_lines=5, preferred_lines=3)
        position = buffer_mgr.allocate_space("test_element", space_req)
        print(f"Space allocated: start={position.start_line}, lines={position.allocated_lines}")
        
        # Apply some content
        delta = BufferDelta(
            line_updates=[(0, "Line 1: Test content"), (1, "Line 2: More content"), (2, "Line 3: Final content")],
            space_change=0,
            clear_lines=[]
        )
        buffer_mgr.apply_buffer_delta(position, delta)
        print("Content applied")
        
        print("✅ Buffer manager test complete")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_buffer_manager()