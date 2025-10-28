#!/usr/bin/env python3
"""
Debug version of quick test to identify duplicate card issue.
"""

import sys
import os
import time

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.questionary_extended.core.page_base import PageBase


def debug_quick_test():
    """Debug version of quick test with detailed logging."""
    
    page = PageBase("🧪 Debug Quick Test")
    page.enable_safe_incremental()
    
    print("Creating cards...")
    card1 = page.card("🔴 Test Card 1")
    card2 = page.card("🔵 Test Card 2")
    
    print(f"Card1 ID: {id(card1)}, Visible: {card1.visible}")
    print(f"Card2 ID: {id(card2)}, Visible: {card2.visible}")
    print(f"Page elements count: {len(page.get_elements())}")
    print("Page elements:")
    for key, element in page.get_elements().items():
        print(f"  {key}: {element.name} ({type(element).__name__}) - Visible: {element.visible}")
    
    # Test 1: Both cards visible
    page.text_status("Test 1/4: Both cards visible", "info")
    page.refresh()
    print("\n--- After Test 1 ---")
    print(f"Card1 Visible: {card1.visible}, Card2 Visible: {card2.visible}")
    print(f"Page elements count: {len(page.get_elements())}")
    
    time.sleep(1.5)
    
    # Test 2: Hide card 1
    page.text_status("Test 2/4: Hiding red card...", "info")
    print("\n--- Hiding Card1 ---")
    card1.hide()
    print(f"Card1 Visible: {card1.visible}, Card2 Visible: {card2.visible}")
    page.refresh()
    print(f"Page elements count: {len(page.get_elements())}")
    
    time.sleep(1.5)
    
    # Test 3: Hide card 2, show card 1
    page.text_status("Test 3/4: Hiding blue, showing red...", "info")
    print("\n--- Hiding Card2, Showing Card1 ---")
    card2.hide()
    card1.show()
    print(f"Card1 Visible: {card1.visible}, Card2 Visible: {card2.visible}")
    page.refresh()
    print(f"Page elements count: {len(page.get_elements())}")
    
    time.sleep(1.5)
    
    # Test 4: Show both cards
    page.text_status("Test 4/4: Showing both cards...", "info")
    print("\n--- Showing both cards ---")
    card2.show()
    print(f"Card1 Visible: {card1.visible}, Card2 Visible: {card2.visible}")
    page.refresh()
    print(f"Page elements count: {len(page.get_elements())}")
    
    time.sleep(1.5)
    
    # Final completion message
    page.text_status("Debug test completed!", "success")
    page.text_display("🎯 Check console for debug info")
    page.refresh()
    
    print("\n--- Final State ---")
    print(f"Page elements count: {len(page.get_elements())}")
    for key, element in page.get_elements().items():
        print(f"  {key}: {element.name} ({type(element).__name__}) - Visible: {element.visible}")


if __name__ == "__main__":
    try:
        debug_quick_test()
    except KeyboardInterrupt:
        print("\n👋 Debug interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()