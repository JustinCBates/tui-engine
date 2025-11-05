#!/usr/bin/env python3
"""
Test script to verify the new section-based Page architecture works correctly.
"""

import sys
import os

# Add src to path so we can import tui_engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tui_engine.page import Page
from tui_engine.app import App
from tui_engine.container import ContainerElement
from tui_engine.element import Element

def test_page_sections():
    """Test that page sections work correctly and render in proper order."""
    print("Testing page sections...")
    
    # Create a page
    page = Page(title="Test Page")
    
    # Test initial state
    assert page.title == "Test Page"
    assert page.title_section is None
    assert page.header_section is None
    assert page.body_section is not None
    assert page.footer_section is None
    
    # Add containers to different sections
    title_container = page.title_section_container("page-title")
    title_container.add(Element("title-text", value="Welcome to Test Page"))
    
    header_container = page.header_section_container("nav")
    header_container.add(Element("nav-text", value="Navigation Bar"))
    
    body_container = page.container("main-content")
    body_container.add(Element("content-text", value="Main page content"))
    
    footer_container = page.footer_section_container("status")
    footer_container.add(Element("status-text", value="Status: Ready"))
    
    # Test that sections were created
    assert page.title_section is not None
    assert page.header_section is not None
    assert page.footer_section is not None
    
    # Test rendering
    lines = page.render(width=80)
    
    # Verify structure
    assert "Test Page" in lines[0]  # Page title
    assert "=" in lines[1]  # Title underline
    assert any("Welcome to Test Page" in line for line in lines)  # Title section content
    assert any("Navigation Bar" in line for line in lines)  # Header section content
    assert any("Main page content" in line for line in lines)  # Body section content
    assert any("Status: Ready" in line for line in lines)  # Footer section content
    
    print("✅ Page sections test passed!")
    
    # Print the rendered output for visual inspection
    print("\nRendered page:")
    print("-" * 40)
    for line in lines:
        print(line)
    print("-" * 40)

def test_app_integration():
    """Test that App class works with Page sections."""
    print("\nTesting App integration...")
    
    # Create an app
    app = App(title="Test App")
    
    # Create a page using the app's page() method
    page = app.page("main", title="Main Page")
    
    # Add content to sections
    page.header_section_container("header").add(Element("header-text", value="App Header"))
    page.container("content").add(Element("content-text", value="App Content"))
    page.footer_section_container("footer").add(Element("footer-text", value="App Footer"))
    
    # Test app state
    assert app.current_page == page
    assert app.has_page("main")
    assert "main" in app.list_pages()
    
    # Test that the page can generate a prompt-toolkit layout
    try:
        layout = page.to_prompt_toolkit_layout()
        assert layout is not None
        print("✅ App integration test passed!")
        
        # Test individual container prompt-toolkit conversion
        container = page.body_section
        ptk_widget = container.to_prompt_toolkit()
        assert ptk_widget is not None
        print("✅ ContainerElement prompt-toolkit conversion works!")
        
    except Exception as e:
        print(f"❌ App integration test failed: {e}")
        raise

def test_deprecated_methods():
    """Test that deprecated methods raise appropriate errors."""
    print("\nTesting deprecated methods...")
    
    page = Page(title="Test")
    
    # Test that run_application() is deprecated
    try:
        page.run_application()
        assert False, "run_application() should raise RuntimeError"
    except RuntimeError as e:
        assert "App.run()" in str(e)
        print("✅ run_application() deprecation test passed!")

def main():
    """Run all tests."""
    print("Testing new section-based Page architecture...\n")
    
    try:
        test_page_sections()
        test_app_integration()
        test_deprecated_methods()
        
        print("\n🎉 All tests passed! The section-based architecture is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()