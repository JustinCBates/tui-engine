#!/usr/bin/env python3
"""
Test the new spatial section architecture.

Demonstrates header/body section separation with independent refresh capabilities.
"""

import sys
import time
from src.questionary_extended.core.page_base import PageBase


def test_spatial_sections():
    """Test spatial sections with header/body separation."""
    print("=== Spatial Section Architecture Test ===")
    print("Testing header/body section separation...")
    print()
    
    # Create page with spatial layout enabled
    page = PageBase("🏗️ Spatial Layout Demo", use_spatial_layout=True)
    
    # Create header section (static)
    header = page.header_section()
    header.add_text("📋 Navigation Instructions:")
    header.add_text("→ Use arrow keys to navigate")
    header.add_text("→ Press Space to toggle options")
    header.add_text("→ Press Q to quit")
    
    # Create body section (dynamic)
    body = page.body_section()
    body.add_text("🎯 Current Selection: Card 1")
    body.add_text("📊 Status: Ready")
    
    # Test space requirements calculation
    page_req = page.calculate_space_requirements()
    print(f"Page space requirements:")
    print(f"  Min lines: {page_req.min_lines}")
    print(f"  Current lines: {page_req.current_lines}")
    print(f"  Max lines: {page_req.max_lines}")
    print(f"  Preferred lines: {page_req.preferred_lines}")
    print()
    
    # Test section requirements
    header_req = header.calculate_space_requirements()
    body_req = body.calculate_space_requirements()
    
    print(f"Header section requirements:")
    print(f"  Static: {header.is_static_section()}")
    print(f"  Lines: {header_req.current_lines}")
    print()
    
    print(f"Body section requirements:")
    print(f"  Static: {body.is_static_section()}")
    print(f"  Lines: {body_req.current_lines}")
    print()
    
    # Test buffer delta calculation
    page_delta = page.calculate_buffer_changes()
    print(f"Page buffer delta:")
    print(f"  Line updates: {len(page_delta.line_updates)}")
    print(f"  Space change: {page_delta.space_change}")
    print(f"  Clear lines: {len(page_delta.clear_lines)}")
    print()
    
    # Test rendering
    print("=== Rendered Output ===")
    lines = page.get_render_lines()
    for i, line in enumerate(lines):
        print(f"{i+1:2d}: {line}")
    
    # Debug: Check section content directly
    print("\n=== Debug: Section Content ===")
    header_lines = header.get_render_lines()
    body_lines = body.get_render_lines()
    print(f"Header lines ({len(header_lines)}):")
    for i, line in enumerate(header_lines):
        print(f"  H{i+1}: {line}")
    print(f"Body lines ({len(body_lines)}):")
    for i, line in enumerate(body_lines):
        print(f"  B{i+1}: {line}")
    
    print()
    print("✅ Spatial section test complete!")


def test_section_updates():
    """Test updating sections independently."""
    print("\n=== Section Update Test ===")
    print("Testing independent section updates...")
    print()
    
    # Create page
    page = PageBase("🔄 Update Test", use_spatial_layout=True)
    
    # Setup sections
    header = page.header_section()
    header.add_text("Static header content")
    
    body = page.body_section()
    body.add_text("Initial body content")
    
    # Get initial state
    initial_lines = page.get_render_lines()
    print("Initial state:")
    for line in initial_lines:
        print(f"  {line}")
    print()
    
    # Update body section only
    body.clear_content()
    body.add_text("UPDATED body content")
    body.add_status("Status changed!", "info")
    
    # Calculate what changed
    delta = page.calculate_buffer_changes()
    print(f"After body update:")
    print(f"  Line updates: {len(delta.line_updates)}")
    print(f"  Space change: {delta.space_change}")
    
    # Show updated rendering
    updated_lines = page.get_render_lines()
    print("\nUpdated state:")
    for line in updated_lines:
        print(f"  {line}")
    
    print("\n✅ Section update test complete!")


if __name__ == "__main__":
    try:
        test_spatial_sections()
        test_section_updates()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)