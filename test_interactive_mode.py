#!/usr/bin/env python3
"""Test interactive prompt positioning."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from questionary_extended.core.page_base import PageBase

def test_interactive_simulation():
    """Simulate what happens with interactive prompts."""
    
    print("=== Testing Interactive Mode ===")
    
    # Test 1: Spatial mode (should work for non-interactive)
    print("\n1. Testing spatial mode (non-interactive):")
    page1 = PageBase("🎴 Card Shuffling Navigation", use_spatial_layout=True)
    page1.text_display("Navigation: ← → (arrow keys) or A/D to move between cards")
    page1.text_display("Space: Toggle current card visibility")
    page1.refresh()
    print("After spatial refresh - cursor should be here")
    
    # Test 2: Legacy mode (should work for interactive)
    print("\n2. Testing legacy mode (interactive-safe):")
    page2 = PageBase("🎴 Card Shuffling Navigation", use_spatial_layout=False)
    page2.text_display("Navigation: ← → (arrow keys) or A/D to move between cards")
    page2.text_display("Space: Toggle current card visibility")
    page2.refresh()
    print("After legacy refresh - cursor should be here")
    print("? 📥 Your choice: (simulated prompt would appear here)")
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    test_interactive_simulation()