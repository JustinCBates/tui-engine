#!/usr/bin/env python3
"""
Minimal reproduction of instruction duplication.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from questionary_extended.core.page_base import PageBase


def test_minimal_duplication():
    """Minimal test to find duplication source."""
    print("=== Minimal Duplication Test ===")
    
    # Create page and add just one instruction
    page = PageBase("Test Page")
    page.text_display("TEST INSTRUCTION LINE")
    
    # Enable incremental mode
    page.enable_safe_incremental()
    
    print("\n--- Before first refresh ---")
    elements = page.get_elements()
    print(f"Elements: {len(elements)}")
    
    print("\n--- Calling refresh() ---")
    page.refresh()
    
    print("\n--- After first refresh ---")
    print("Elements still the same?", len(page.get_elements()))
    
    print("\n--- Direct get_render_lines() output ---")
    lines = page.get_render_lines()
    for i, line in enumerate(lines):
        print(f"  {i+1}: '{line}'")
    
    print("\n--- Testing components property ---")
    components = page.components
    print(f"Components: {len(components)}")
    for i, comp in enumerate(components.values()):
        if hasattr(comp, 'get_render_lines'):
            comp_lines = comp.get_render_lines()
            print(f"  Component {i+1}: {len(comp_lines)} lines")
            for j, line in enumerate(comp_lines):
                print(f"    {j+1}: '{line}'")
    
    print("\n✅ Minimal test complete!")


if __name__ == "__main__":
    test_minimal_duplication()