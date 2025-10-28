#!/usr/bin/env python3
"""
Test Card class spatial awareness implementation.

Verifies that the Card class now implements all required spatial methods.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from questionary_extended.core.interfaces import SpaceRequirement, BufferDelta, ElementChangeEvent
from questionary_extended.core.page_base import PageBase
from questionary_extended.core.component_wrappers import Component


def test_card_spatial_awareness():
    """Test Card class spatial awareness."""
    print("=== Testing Card Spatial Awareness ===")
    
    # Create page and card
    page = PageBase("Card Test", use_spatial_layout=True)
    card = page.card("Test Card", style="bordered")
    
    # Add some components to the card
    card.text_display("First line of content")
    card.text_display("Second line of content")
    
    # Test spatial awareness methods
    print("Testing spatial methods...")
    
    # Test space requirements
    space_req = card.calculate_space_requirements()
    assert isinstance(space_req, SpaceRequirement)
    assert space_req.min_lines > 0
    print(f"  ✓ Card space requirements: {space_req.current_lines} lines")
    
    # Test buffer changes
    buffer_delta = card.calculate_buffer_changes()
    assert isinstance(buffer_delta, BufferDelta)
    print(f"  ✓ Card buffer delta: {buffer_delta.space_change} change")
    
    # Test compression
    can_compress = card.can_compress_to(5)
    assert isinstance(can_compress, bool)
    print(f"  ✓ Card can compress to 5 lines: {can_compress}")
    
    # Test event system
    events_received = []
    def test_listener(event):
        events_received.append(event)
    
    card.register_change_listener(test_listener)
    card.fire_change_event("test_change", space_delta=0)
    assert len(events_received) == 1
    assert events_received[0].element_name == "Test Card"
    print("  ✓ Card event system working")
    
    # Test container methods
    print("Testing container methods...")
    
    # Test aggregate space requirements
    agg_space_req = card.calculate_aggregate_space_requirements()
    assert isinstance(agg_space_req, SpaceRequirement)
    print(f"  ✓ Card aggregate space: {agg_space_req.current_lines} lines")
    
    # Test child space allocation
    can_allocate = card.allocate_child_space("nonexistent", space_req)
    assert can_allocate == False  # Child doesn't exist
    print("  ✓ Card child space allocation working")
    
    # Test rendering
    print("Testing rendering...")
    lines = card.get_render_lines()
    assert isinstance(lines, list)
    assert len(lines) > 0
    print(f"  ✓ Card renders {len(lines)} lines")
    
    # Show the rendered output
    print("\nRendered card:")
    for i, line in enumerate(lines):
        print(f"  {i+1:2d}: {line}")
    
    print("\n✅ Card spatial awareness: PASSED")
    return True


if __name__ == "__main__":
    try:
        success = test_card_spatial_awareness()
        print("\n🎉 Card spatial awareness test completed successfully!")
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)