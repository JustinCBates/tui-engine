#!/usr/bin/env python3
"""
Test without incremental refresh to isolate the issue.
"""

import sys
import os
import time

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.questionary_extended.core.page_base import PageBase


def simple_test():
    """Simple test without incremental refresh."""
    
    page = PageBase("🧪 Simple Test")
    # Don't enable incremental refresh
    
    print("Creating cards...")
    card1 = page.card("🔴 Test Card 1")
    card2 = page.card("🔵 Test Card 2")
    
    print("Test 1: Both cards visible")
    page.text_status("Test 1: Both cards visible", "info")
    page.refresh()
    
    print("\nTest 2: Hiding card1")
    card1.hide()
    page.text_status("Test 2: Card1 hidden", "info")
    page.refresh()
    
    print("\nTest 3: Hiding card2, showing card1")
    card2.hide()
    card1.show()
    page.text_status("Test 3: Card2 hidden, Card1 shown", "info")
    page.refresh()
    
    print("\nTest 4: Both cards visible")
    card2.show()
    page.text_status("Test 4: Both cards visible again", "info")
    page.refresh()
    
    print("\nElements in page:")
    for key, element in page.get_elements().items():
        print(f"  {key}: {element.name} - Visible: {element.visible}")


if __name__ == "__main__":
    try:
        simple_test()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted.")
    except Exception as e:
        print(f"❌ Test error: {e}")
        import traceback
        traceback.print_exc()