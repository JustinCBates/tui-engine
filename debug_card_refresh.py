#!/usr/bin/env python3
"""
Debug the card shuffling refresh issue
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from questionary_extended.core.page_base import PageBase
from questionary_extended.core.debug_mode import DebugMode

def debug_card_shuffling():
    """Debug the card shuffling refresh issue."""
    DebugMode.enable()
    
    print("🧪 Debugging Card Shuffling Refresh")
    print("=" * 50)
    
    # Create page exactly like the demo
    page = PageBase("🎴 Card Shuffling Navigation", use_spatial_layout=True)
    
    print(f"✅ Page created")
    print(f"  - Spatial layout: {page.use_spatial_layout}")
    print(f"  - Buffer manager: {page._buffer_manager is not None}")
    print(f"  - Buffer manager type: {type(page._buffer_manager)}")
    
    # Add some instructions
    page.text_display("Navigation: ← → (arrow keys) or A/D to move between cards")
    page.text_display("Space: Toggle current card visibility")
    page.text_display("Q: Quit demo")
    page.text_display("")
    
    # Add a card
    card = page.card("🏠 Personal Information", style="bordered")
    
    print("\\n🔄 First refresh (initial):")
    page.refresh()
    
    print("\\n🔄 Second refresh (should not duplicate):")
    page.refresh()
    
    print("\\n✅ Debug complete - check output above for duplication")

if __name__ == "__main__":
    debug_card_shuffling()