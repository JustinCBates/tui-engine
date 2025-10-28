#!/usr/bin/env python3
"""Test buffer manager instantiation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_instantiation():
    print("1. Starting instantiation test...")
    
    try:
        from questionary_extended.core.buffer_manager import ANSIBufferManager
        print("2. Imported ANSIBufferManager")
        
        print("3. About to instantiate...")
        buffer_mgr = ANSIBufferManager()
        print("4. Default instantiation successful")
        
        print("5. About to instantiate with terminal_height...")
        buffer_mgr2 = ANSIBufferManager(terminal_height=20)
        print("6. Instantiation with terminal_height successful")
        
        print("7. All instantiations successful!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_instantiation()