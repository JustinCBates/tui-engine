#!/usr/bin/env python3
"""Test cursor positioning after spatial refresh."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from questionary_extended.core.page_base import PageBase

def test_cursor_positioning():
    """Test that cursor is positioned correctly after spatial refresh."""
    
    print("=== Testing Cursor Positioning ===")
    
    # Create a page with spatial layout enabled
    page = PageBase("🎴 Test Page", use_spatial_layout=True)
    
    # Add some content
    page.text_display("Line 1: Navigation instructions")
    page.text_display("Line 2: More instructions")
    page.text_display("Line 3: Even more instructions")
    
    # Call refresh which should use spatial refresh
    print("Calling refresh()...")
    page.refresh()
    
    # This print should appear immediately after the content
    print("📍 This line should appear right after the page content")
    print("📍 And this one should be on the next line")
    
    print("\n✅ Test complete - check cursor positioning above")

if __name__ == "__main__":
    test_cursor_positioning()