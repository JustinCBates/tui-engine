#!/usr/bin/env python3
"""
Test spatial refresh functionality
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from questionary_extended.core.page_base import PageBase
from questionary_extended.core.debug_mode import DebugMode

def test_spatial_refresh():
    """Test if spatial refresh is working correctly."""
    print("🧪 Testing Spatial Refresh")
    print("=" * 50)
    
    # Enable debug mode to see what's happening
    DebugMode.enable()
    
    # Create page with spatial layout enabled
    page = PageBase("Test Page", use_spatial_layout=True)
    
    print(f"✅ Created page with spatial layout: {page.use_spatial_layout}")
    print(f"✅ Buffer manager exists: {page._buffer_manager is not None}")
    
    # Add some content
    page.text_display("Line 1")
    page.text_display("Line 2")
    
    # Test refresh
    print("\\n🔄 First refresh:")
    page.refresh()
    
    print("\\n🔄 Second refresh (should skip if no changes):")
    page.refresh()
    
    # Add more content and refresh
    page.text_display("Line 3")
    print("\\n🔄 Third refresh (with new content):")
    page.refresh()

if __name__ == "__main__":
    test_spatial_refresh()