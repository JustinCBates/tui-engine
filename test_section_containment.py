#!/usr/bin/env python3
"""
Test section containment validation.

Verifies that sections properly validate their children and prevent
invalid containments like Section-in-Section or Page-in-Section.
"""

from src.questionary_extended.core.page_base import PageBase
from src.questionary_extended.core.section import Section
from src.questionary_extended.core.component_wrappers import Component


def test_valid_containment():
    """Test valid section containment scenarios."""
    print("=== Testing Valid Section Containment ===")
    
    # Create page with sections
    page = PageBase("Containment Test", use_spatial_layout=True)
    section = page.create_section("test_section")
    
    # Test 1: Component in Section (should work)
    try:
        component = Component(
            name="test_component",
            component_type="text_display",
            content="Test content"
        )
        section.add_element(component)
        print("✅ Component → Section: Valid")
    except Exception as e:
        print(f"❌ Component → Section: Failed - {e}")
    
    # Test 2: Card in Section (should work)
    try:
        card = page.card("Test Card")  # Creates a card
        section2 = page.create_section("section_with_card")
        section2.add_element(card)
        print("✅ Card → Section: Valid")
    except Exception as e:
        print(f"❌ Card → Section: Failed - {e}")
    
    print()


def test_invalid_containment():
    """Test invalid section containment scenarios."""
    print("=== Testing Invalid Section Containment ===")
    
    page = PageBase("Invalid Test", use_spatial_layout=True)
    
    # Test 1: Section in Section (should fail)
    try:
        parent_section = page.create_section("parent")
        child_section = Section("child")
        parent_section.add_element(child_section)
        print("❌ Section → Section: Should have failed but didn't!")
    except TypeError as e:
        print(f"✅ Section → Section: Correctly rejected - {str(e)[:60]}...")
    except Exception as e:
        print(f"⚠️ Section → Section: Unexpected error - {e}")
    
    # Test 2: Page in Section (should fail) 
    try:
        section = page.create_section("test")
        nested_page = PageBase("Nested Page")
        section.add_element(nested_page)
        print("❌ Page → Section: Should have failed but didn't!")
    except TypeError as e:
        print(f"✅ Page → Section: Correctly rejected - {str(e)[:60]}...")
    except Exception as e:
        print(f"⚠️ Page → Section: Unexpected error - {e}")
    
    print()


def test_interface_hierarchy():
    """Test the interface hierarchy is working correctly."""
    print("=== Testing Interface Hierarchy ===")
    
    from src.questionary_extended.core.interfaces import (
        SectionChildInterface, ComponentInterface, 
        PageChildInterface, SectionInterface
    )
    
    # Create instances
    component = Component("test", "text_display", content="test")
    section = Section("test_section")
    page = PageBase("Test Page")
    
    # Test interface compliance
    print(f"Component implements SectionChildInterface: {isinstance(component, SectionChildInterface)}")
    print(f"Section implements SectionInterface: {isinstance(section, SectionInterface)}")
    print(f"Section implements PageChildInterface: {isinstance(section, PageChildInterface)}")
    print(f"Page implements SectionChildInterface: {isinstance(page, SectionChildInterface)}")
    
    print()


if __name__ == "__main__":
    test_valid_containment()
    test_invalid_containment()
    test_interface_hierarchy()
    print("✅ Containment validation tests complete!")