#!/usr/bin/env python3
"""
Simple test of the refresh architecture
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from questionary_extended.page_runtime import Page

def test_refresh_architecture():
    """Test the new refresh architecture."""
    
    # Create a page with mixed structure
    page = Page("Test Page")
    
    # Add a card with assembly
    card1 = page.card("Personal Info")
    assembly1 = card1.assembly("personal")
    comp1 = assembly1.text("name", message="Name:")
    comp2 = assembly1.text("age", message="Age:")
    
    # Add page-level assembly
    assembly2 = page.assembly("config")
    comp3 = assembly2.text("app_name", message="App name:")
    
    # Add another card
    card2 = page.card("Settings")
    assembly3 = card2.assembly("settings")
    comp4 = assembly3.text("theme", message="Theme:")
    
    print("=== Initial State (all visible) ===")
    page.refresh()
    
    print("\n=== Hide card2, show others ===")
    card2.hide()
    page.refresh()
    
    print("\n=== Hide assembly1, show others ===")
    card2.show()
    assembly1.hide()
    page.refresh()
    
    print("\n=== Hide individual component ===")
    assembly1.show()
    comp3.hide()
    page.refresh()
    
    print("\n=== Show all again ===")
    comp3.show()
    page.refresh()
    
    print("\n✅ Refresh architecture test complete!")

if __name__ == "__main__":
    test_refresh_architecture()