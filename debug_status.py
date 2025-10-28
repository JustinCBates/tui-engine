#!/usr/bin/env python3
"""
Debug test to understand text_status interference with card visibility.
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.questionary_extended.core.page_base import PageBase


def debug_status_interference():
    """Debug how text_status affects card visibility."""
    
    page = PageBase("🔍 Debug Status")
    
    print("=== Initial State ===")
    card1 = page.card("🔴 Test Card 1")
    card2 = page.card("🔵 Test Card 2")
    
    print(f"Page elements: {len(page.get_elements())}")
    for key, element in page.get_elements().items():
        print(f"  {key}: {element.name} - Visible: {element.visible}")
    print()
    
    print("=== After first text_status ===")
    page.text_status("Status message 1", "info")
    print(f"Page elements: {len(page.get_elements())}")
    for key, element in page.get_elements().items():
        print(f"  {key}: {element.name} - Visible: {element.visible}")
    print()
    
    print("=== After hiding card1 ===")
    card1.hide()
    print(f"Card1 visible: {card1.visible}")
    print(f"Card2 visible: {card2.visible}")
    print(f"Page elements: {len(page.get_elements())}")
    for key, element in page.get_elements().items():
        print(f"  {key}: {element.name} - Visible: {element.visible}")
    print()
    
    print("=== After second text_status ===")
    page.text_status("Status message 2", "info")
    print(f"Card1 visible: {card1.visible}")
    print(f"Card2 visible: {card2.visible}")
    print(f"Page elements: {len(page.get_elements())}")
    for key, element in page.get_elements().items():
        print(f"  {key}: {element.name} - Visible: {element.visible}")
    print()
    
    print("=== Rendering result ===")
    page.refresh()


if __name__ == "__main__":
    try:
        debug_status_interference()
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()