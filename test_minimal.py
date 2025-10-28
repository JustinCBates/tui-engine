#!/usr/bin/env python3
"""Minimal test."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def minimal_test():
    print("Starting minimal test...")
    
    try:
        from questionary_extended.core.spatial import SpaceRequirement
        print("SpaceRequirement imported")
        
        space_req = SpaceRequirement(min_lines=3, current_lines=3, max_lines=5, preferred_lines=3)
        print("SpaceRequirement created")
        
        from questionary_extended.core.buffer_manager import ANSIBufferManager
        print("ANSIBufferManager imported")
        
        print("About to create buffer manager...")
        buffer_mgr = ANSIBufferManager(terminal_height=20)
        print("Buffer manager created successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    minimal_test()