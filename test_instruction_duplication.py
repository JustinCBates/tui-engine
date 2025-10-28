#!/usr/bin/env python3
"""
Quick test to reproduce the instruction duplication issue.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from questionary_extended.core.page_base import PageBase


def test_instruction_duplication():
    """Test if instructions are being duplicated."""
    print("=== Testing Instruction Duplication ===")
    
    # Create page like the demo does
    page = PageBase("🎴 Card Shuffling Navigation")
    
    # Add instructions like the demo does
    instructions = [
        "Navigation: ← → (arrow keys) or A/D to move between cards",
        "Space: Toggle current card visibility", 
        "T: Run animation test (5 cards transition)",
        "Q: Quit demo",
        "",
    ]
    
    print("Adding instructions...")
    for instruction in instructions:
        page.text_display(instruction)
    
    # Create cards like the demo does
    print("Creating cards...")
    cards = [
        page.card("🏠 Personal Information", style="bordered"),
        page.card("💼 Professional Details", style="bordered"),
    ]
    
    # Enable incremental like the demo does
    page.enable_safe_incremental()
    
    # Check how many elements are in the page
    elements = page.get_elements()
    print(f"Page has {len(elements)} elements")
    
    # Show what's in the page
    print("\nPage elements:")
    for i, element in enumerate(elements.values()):
        if hasattr(element, 'name'):
            print(f"  {i+1}: {element.name} ({element.element_type})")
        else:
            print(f"  {i+1}: {type(element)} (no name)")
    
    # Test first refresh
    print("\n=== FIRST REFRESH ===")
    print("Direct get_render_lines before refresh:")
    lines_before = page.get_render_lines()
    for i, line in enumerate(lines_before[:15]):  # Just first 15 lines
        print(f"  {i+1:2d}: {line}")
    
    print("\nCalling page.refresh()...")
    page.refresh()
    
    print("\nDirect get_render_lines after refresh:")
    lines_after = page.get_render_lines()
    for i, line in enumerate(lines_after[:15]):  # Just first 15 lines
        print(f"  {i+1:2d}: {line}")
    
    print("\n--- Element count after first refresh ---")
    elements = page.get_elements()
    print(f"Page has {len(elements)} elements")
    
    # Test second refresh
    print("\n=== SECOND REFRESH ===")
    page.refresh()
    
    print("\n--- Element count after second refresh ---")
    elements = page.get_elements()
    print(f"Page has {len(elements)} elements")
    
    # Test rendering directly
    print("\n=== DIRECT RENDERING TEST ===")
    lines = page.get_render_lines()
    print("Rendered lines:")
    for i, line in enumerate(lines):
        print(f"  {i+1:2d}: {line}")
    
    print("\n✅ Test complete!")


if __name__ == "__main__":
    try:
        test_instruction_duplication()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()