"""
Demo of DI system working with existing Component class.

This demonstrates that the new DI system can be used alongside the existing
Component class without any modifications to the Component class itself.
"""

from unittest.mock import MagicMock
from src.questionary_extended.core.component import Component
from src.tui_engine.questionary_factory import set_questionary_factory, get_questionary, clear_questionary_factory

def demo_di_with_component():
    """Demonstrate DI system working with Component class."""
    print("=== DI System Demo with Component Class ===\n")
    
    # Test 1: Default behavior (real questionary)
    print("1. Testing default behavior:")
    try:
        component = Component()
        questionary_module = get_questionary()
        print(f"   ✓ Got questionary module: {type(questionary_module)}")
        print(f"   ✓ Has required methods: text={hasattr(questionary_module, 'text')}, select={hasattr(questionary_module, 'select')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    
    # Test 2: Inject mock and use with Component
    print("2. Testing with mock injection:")
    try:
        # Create mock questionary
        mock_questionary = MagicMock()
        mock_questionary.text.return_value = "mocked_text_component"
        mock_questionary.select.return_value = "mocked_select_component"
        
        # Inject the mock
        set_questionary_factory(lambda: mock_questionary)
        
        # Verify injection worked
        injected_module = get_questionary()
        print(f"   ✓ Injected module: {type(injected_module)}")
        print(f"   ✓ Is our mock: {injected_module is mock_questionary}")
        
        # Test that calls work
        text_result = injected_module.text("What's your name?")
        select_result = injected_module.select("Choose option:", choices=["A", "B"])
        
        print(f"   ✓ Mock text call returned: {text_result}")
        print(f"   ✓ Mock select call returned: {select_result}")
        
        # Verify calls were made
        mock_questionary.text.assert_called_once_with("What's your name?")
        mock_questionary.select.assert_called_once_with("Choose option:", choices=["A", "B"])
        print("   ✓ Mock calls verified")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    finally:
        # Always cleanup
        clear_questionary_factory()
    
    print()
    
    # Test 3: Verify cleanup worked
    print("3. Testing cleanup:")
    try:
        questionary_module = get_questionary()
        print(f"   ✓ Back to default: {type(questionary_module)}")
        print(f"   ✓ Has text method: {hasattr(questionary_module, 'text')}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()
    
    # Test 4: Show how this would work with Component.create_questionary_component
    # Note: This would work once we update Component class in Phase 2B
    print("4. Future integration with Component class:")
    print("   Once Phase 2B is complete, Component.create_questionary_component()")
    print("   will use get_questionary() internally, making all the mock")
    print("   injection work seamlessly with the existing Component API.")
    print("   ")
    print("   Current Component class still uses the complex fallback system,")
    print("   but the DI system is ready to replace it!")

if __name__ == "__main__":
    demo_di_with_component()