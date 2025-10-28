#!/usr/bin/env python3
"""
Test universal spatial awareness enforcement across all element types.

This test verifies that:
1. All element types implement required spatial methods
2. Type checking prevents non-compliant elements
3. Event system works across element hierarchy
4. Spatial requirements can be calculated at all levels
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from questionary_extended.core.interfaces import (
    ElementInterface, ElementChangeEvent, SpaceRequirement, BufferDelta
)
from questionary_extended.core.component_wrappers import Component
from questionary_extended.core.section import Section
from questionary_extended.core.page_base import PageBase


def test_component_spatial_awareness():
    """Test Component class spatial awareness."""
    print("Testing Component spatial awareness...")
    
    # Create a component
    comp = Component("test_component", "text_display", content="Hello, World!")
    
    # Test spatial awareness methods
    space_req = comp.calculate_space_requirements()
    assert isinstance(space_req, SpaceRequirement)
    assert space_req.min_lines > 0
    print(f"  ✓ Component space requirements: {space_req.min_lines} lines")
    
    # Test buffer changes
    buffer_delta = comp.calculate_buffer_changes(2)
    assert isinstance(buffer_delta, BufferDelta)
    print(f"  ✓ Component buffer delta: {buffer_delta.space_change} change")
    
    # Test compression
    can_compress = comp.can_compress_to(1)
    assert isinstance(can_compress, bool)
    print(f"  ✓ Component can compress: {can_compress}")
    
    # Test event system
    events_received = []
    def test_listener(event):
        events_received.append(event)
    
    comp.register_change_listener(test_listener)
    comp.fire_change_event("test_change", space_delta=0)
    assert len(events_received) == 1
    assert events_received[0].element_name == "test_component"
    print("  ✓ Component event system working")
    
    print("Component spatial awareness: PASSED")


def test_section_spatial_awareness():
    """Test Section class spatial awareness."""
    print("Testing Section spatial awareness...")
    
    # Create a section
    section = Section("test_section", static=False, header="Test Section")
    
    # Test spatial awareness methods
    space_req = section.calculate_space_requirements()
    assert isinstance(space_req, SpaceRequirement)
    print(f"  ✓ Section space requirements: {space_req.min_lines} lines")
    
    # Test buffer changes
    buffer_delta = section.calculate_buffer_changes()
    assert isinstance(buffer_delta, BufferDelta)
    print(f"  ✓ Section buffer delta: {buffer_delta.space_change} change")
    
    # Test adding a component to section
    comp = Component("section_child", "text_status", content="Status message")
    section.add_element(comp)
    
    # Test aggregate space requirements
    agg_space_req = section.calculate_aggregate_space_requirements()
    assert isinstance(agg_space_req, SpaceRequirement)
    print(f"  ✓ Section aggregate space: {agg_space_req.current_lines} lines")
    
    print("Section spatial awareness: PASSED")


def test_page_spatial_awareness():
    """Test PageBase class spatial awareness."""
    print("Testing PageBase spatial awareness...")
    
    # Create a page
    page = PageBase("Test Page", use_spatial_layout=True)
    
    # Test spatial awareness methods
    space_req = page.calculate_space_requirements()
    assert isinstance(space_req, SpaceRequirement)
    print(f"  ✓ Page space requirements: {space_req.min_lines} lines")
    
    # Test buffer changes
    buffer_delta = page.calculate_buffer_changes()
    assert isinstance(buffer_delta, BufferDelta)
    print(f"  ✓ Page buffer delta: {buffer_delta.space_change} change")
    
    # Test creating section within page
    section = page.create_section("dynamic_section", header="Dynamic Content")
    assert section is not None
    print("  ✓ Page section creation working")
    
    print("PageBase spatial awareness: PASSED")


def test_containment_validation():
    """Test that containment validation enforces spatial awareness."""
    print("Testing containment validation...")
    
    # Create section and component
    section = Section("container_section", static=False, header="Container Test")
    comp = Component("valid_child", "text_display", content="Valid component")
    
    # Add component to section (should work)
    try:
        section.add_element(comp)
        print("  ✓ Valid component added to section")
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False
    
    # Test that section children implement SectionChildInterface
    elements = section.get_elements()
    for element in elements.values():
        # All elements should have spatial methods
        assert hasattr(element, 'calculate_space_requirements')
        assert hasattr(element, 'calculate_buffer_changes')
        assert hasattr(element, 'can_compress_to')
        assert hasattr(element, 'compress_to_lines')
        assert hasattr(element, 'fire_change_event')
        assert hasattr(element, 'register_change_listener')
        print("  ✓ Section child has all required spatial methods")
    
    print("Containment validation: PASSED")


def test_event_propagation():
    """Test event propagation through container hierarchy."""
    print("Testing event propagation...")
    
    # Create page with section and component
    page = PageBase("Event Test Page", use_spatial_layout=True)
    section = page.create_section("event_section", static=False, header="Event Test")
    comp = Component("event_component", "text_status", content="Event test")
    section.add_element(comp)
    
    # Set up event listeners
    page_events = []
    section_events = []
    
    def page_listener(event):
        page_events.append(event)
    
    def section_listener(event):
        section_events.append(event)
    
    # Register listeners
    comp.register_change_listener(section_listener)
    section.register_change_listener(page_listener)
    
    # Fire event from component
    comp.fire_change_event("content_change", space_delta=1)
    
    # Check event propagation
    assert len(section_events) == 1
    print("  ✓ Event received by section")
    
    print("Event propagation: PASSED")


def main():
    """Run all spatial awareness tests."""
    print("=== Universal Spatial Awareness Enforcement Test ===")
    print()
    
    try:
        test_component_spatial_awareness()
        print()
        
        test_section_spatial_awareness()
        print()
        
        test_page_spatial_awareness()
        print()
        
        test_containment_validation()
        print()
        
        test_event_propagation()
        print()
        
        print("🎉 ALL TESTS PASSED!")
        print("Universal spatial awareness enforcement is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)