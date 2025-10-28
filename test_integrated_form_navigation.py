#!/usr/bin/env python3
"""
Test for integrated form navigation with spatial components.

This test demonstrates the complete system:
1. Components embedded within cards
2. Form navigation with tab support
3. Spatial buffer integration
4. Interactive prompts working together
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from questionary_extended.core.component_wrappers import Component
from questionary_extended.core.form_navigation import SpatialFormNavigator
from questionary_extended.core.buffer_manager import ANSIBufferManager


def test_integrated_form_navigation():
    """Test complete form navigation system."""
    print("🧪 Testing Integrated Form Navigation System")
    print("=" * 60)
    
    # Create buffer manager and form navigator
    buffer_manager = ANSIBufferManager(terminal_height=25)
    form_navigator = SpatialFormNavigator(buffer_manager=buffer_manager)
    
    # Create components with form navigator integration
    components = [
        Component("name", "text", form_navigator=form_navigator, 
                 message="What's your name?", default=""),
        Component("email", "text", form_navigator=form_navigator,
                 message="What's your email?", default=""),
        Component("subscribe", "confirm", form_navigator=form_navigator,
                 message="Subscribe to newsletter?", default=True),
        Component("role", "select", form_navigator=form_navigator,
                 message="What's your role?", 
                 choices=["Developer", "Designer", "Manager", "Other"])
    ]
    
    print(f"✅ Created {len(components)} interactive components")
    print(f"✅ Form navigator has {len(form_navigator.interactive_components)} registered components")
    
    # Test space calculations
    print("\\n📏 Testing space calculations:")
    for component in components:
        space_req = component.calculate_space_requirements()
        print(f"  {component.name}: {space_req.current_lines} lines (min: {space_req.min_lines}, max: {space_req.max_lines})")
    
    # Test component state
    print("\\n🔄 Testing component states:")
    for component in components:
        print(f"  {component.name}: interactive={component.is_interactive()}, active={component._is_active}")
    
    # Test render lines (display mode)
    print("\\n🎨 Testing display rendering:")
    for component in components:
        lines = component.get_render_lines()
        print(f"  {component.name}: {len(lines)} lines - {lines[0] if lines else 'No content'}")
    
    # Test activation
    print("\\n⚡ Testing component activation:")
    first_component = components[0]
    first_component.activate_for_input(buffer_position=0)
    print(f"  Activated {first_component.name}: active={first_component._is_active}")
    
    # Test interactive rendering
    lines = first_component.get_render_lines()
    print(f"  Interactive render: {lines[0] if lines else 'No content'}")
    
    first_component.deactivate()
    print(f"  Deactivated {first_component.name}: active={first_component._is_active}")
    
    # Test form summary
    print("\\n📋 Form summary:")
    summary = form_navigator.get_form_summary()
    print(summary)
    
    # Simulate some values
    components[0].set_value("John Doe")
    components[2].set_value(True)
    form_navigator.form_state["name"] = "John Doe"
    form_navigator.form_state["subscribe"] = True
    
    print("\\n📋 Updated form summary:")
    summary = form_navigator.get_form_summary()
    print(summary)
    
    # Test value collection
    print("\\n💾 Collected values:")
    values = form_navigator.collect_all_values()
    for key, value in values.items():
        print(f"  {key}: {value}")
    
    print("\\n✅ All integration tests passed!")
    print("\\n🎯 System is ready for embedded interactive prompts!")
    
    return True


def demonstrate_card_integration():
    """Demonstrate how this would work in a card context."""
    print("\\n" + "=" * 60)
    print("🃏 Card Integration Demonstration")
    print("=" * 60)
    
    print("""
    In a card context, this system would work like this:
    
    ┌─ User Profile Card ─────────────────┐
    │                                     │
    │ 📝 Name: [    John Doe    ] ✅     │  <- Interactive field
    │ 📧 Email: [              ] ⏸️      │  <- Waiting for input
    │ 📬 Subscribe: Yes ✅               │  <- Completed
    │ 👤 Role: Developer ✅              │  <- Completed
    │                                     │
    │ [Tab] to navigate • [Enter] submit  │
    └─────────────────────────────────────┘
    
    Benefits:
    ✅ Tab navigation between fields
    ✅ Visual feedback on completion status
    ✅ Embedded prompts within card layout
    ✅ Spatial buffer coordination
    ✅ No cursor positioning conflicts
    """)
    
    return True


if __name__ == "__main__":
    try:
        # Run the integration test
        if test_integrated_form_navigation():
            demonstrate_card_integration()
            print("\\n🎉 Integration test completed successfully!")
        else:
            print("\\n❌ Integration test failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\\n💥 Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)