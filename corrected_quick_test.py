#!/usr/bin/env python3
"""
Corrected quick test based on working debug pattern.
"""

import sys
import os
import time

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.questionary_extended.core.page_base import PageBase


def corrected_quick_test():
    """Corrected version of quick test."""
    
    page = PageBase("🧪 Corrected Quick Test")
    
    card1 = page.card("🔴 Test Card 1")
    card2 = page.card("🔵 Test Card 2")
    
    # Test 1: Both cards visible
    page.text_status("Test 1/4: Both cards visible", "info")
    page.refresh()
    print(f"DEBUG: Card1={card1.visible}, Card2={card2.visible}")
    time.sleep(1.5)
    
    # Test 2: Hide card 1
    card1.hide()
    page.text_status("Test 2/4: Hiding red card...", "info")
    page.refresh()
    print(f"DEBUG: Card1={card1.visible}, Card2={card2.visible}")
    time.sleep(1.5)
    
    # Test 3: Hide card 2, show card 1
    card2.hide()
    card1.show()
    page.text_status("Test 3/4: Hiding blue, showing red...", "info")
    page.refresh()
    print(f"DEBUG: Card1={card1.visible}, Card2={card2.visible}")
    time.sleep(1.5)
    
    # Test 4: Show both cards
    card2.show()
    page.text_status("Test 4/4: Showing both cards...", "info")
    page.refresh()
    print(f"DEBUG: Card1={card1.visible}, Card2={card2.visible}")
    time.sleep(1.5)
    
    # Final completion message
    page.text_status("Quick test completed!", "success")
    page.text_display("🎯 Did you see smooth card visibility changes?")
    page.refresh()


if __name__ == "__main__":
    try:
        corrected_quick_test()
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()