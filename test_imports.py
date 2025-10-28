#!/usr/bin/env python3
"""Step by step import test."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def step_by_step():
    print("1. Starting import test...")
    
    try:
        print("2. Importing spatial...")
        from questionary_extended.core import spatial
        print("3. Spatial imported OK")
        
        print("4. Creating SpaceRequirement...")
        space_req = spatial.SpaceRequirement(min_lines=3, current_lines=3, max_lines=5, preferred_lines=3)
        print("5. SpaceRequirement created OK")
        
        print("6. Importing buffer_manager...")
        from questionary_extended.core import buffer_manager
        print("7. buffer_manager imported OK")
        
        print("8. All imports successful!")
        
    except Exception as e:
        print(f"Error at step: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    step_by_step()