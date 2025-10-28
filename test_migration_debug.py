#!/usr/bin/env python3
"""Test migration to verify spatial methods are being called."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from questionary_extended.core.page_base import PageBase

# Test the card shuffling functionality
def test_migration():
    print("=== Testing Migration ===")
    
    # Create a simple page with spatial layout DISABLED first to test
    page = PageBase("🎴 Card Test", use_spatial_layout=False)
    
    print(f"Page created with spatial layout: {page.use_spatial_layout}")
    print(f"Buffer manager available: {hasattr(page, '_buffer_manager') and page._buffer_manager is not None}")
    
    # Add some instructions
    page.text_display("Navigation: ← → (arrow keys) or A/D to move between cards")
    page.text_display("Space: Toggle current card visibility")
    
    # Add a card
    card = page.card("🏠 Personal Information")
    
    elements = page.get_elements()
    print(f"Page elements after setup: {len(elements)}")
    
    # First refresh
    print("\n=== CALLING REFRESH (Legacy mode) ===")
    page.refresh()
    
    print("\n✅ Test complete!")

if __name__ == "__main__":
    test_migration()