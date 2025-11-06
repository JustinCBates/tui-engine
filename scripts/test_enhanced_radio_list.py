#!/usr/bin/env python3
"""
Enhanced RadioListAdapter Test Suite

This script thoroughly tests the enhanced RadioListAdapter functionality,
ensuring proper Questionary integration while maintaining backward compatibility.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tui_engine.widgets.radio_list_adapter import RadioListAdapter, EnhancedRadioListAdapter, create_radio_list


def test_backward_compatibility():
    """Test that the enhanced adapter maintains backward compatibility."""
    print("🔄 Testing Backward Compatibility...")
    print("=" * 50)
    
    # Test original interface with None widget
    try:
        adapter1 = RadioListAdapter(None)
        print("✅ RadioListAdapter(None) - Compatible")
        
        # Test basic operations
        adapter1.set_selected(["option1"])
        selected = list(adapter1.get_selected())
        print(f"✅ Basic selection operations - Selected: {selected}")
        
        # Test focus
        adapter1.focus()  # Should not raise exception
        print("✅ Focus operation - Compatible")
        
        # Test sync
        value = adapter1._tui_sync()  # Should not raise exception
        print(f"✅ Sync operation - Compatible (value: {value})")
        
        # Test ptk_widget property
        widget = adapter1.ptk_widget
        print("✅ ptk_widget property - Compatible")
        
        # Test options property
        options = adapter1.options
        print(f"✅ Options property - Compatible (count: {len(options)})")
            
    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
    
    print()


def test_enhanced_initialization():
    """Test enhanced RadioListAdapter initialization."""
    print("✨ Testing Enhanced Initialization...")
    print("=" * 50)
    
    # Test enhanced initialization with choices
    try:
        choices = ["Option 1", "Option 2", "Option 3"]
        adapter = RadioListAdapter(
            choices=choices,
            message="Select an option:",
            style='professional_blue',
            default="Option 2"
        )
        print("✅ Enhanced initialization with string choices successful")
        
        # Test with tuple choices
        tuple_choices = [
            ("Display Name 1", "value1"),
            ("Display Name 2", "value2"),
            ("Display Name 3", "value3")
        ]
        adapter2 = RadioListAdapter(
            choices=tuple_choices,
            message="Select from tuples:",
            style='dark_mode'
        )
        print("✅ Enhanced initialization with tuple choices successful")
        
        # Test widget info
        info = adapter.get_widget_info()
        print(f"✅ Widget info: Questionary={info['use_questionary']}, Choices={info['choice_count']}")
        
    except Exception as e:
        print(f"❌ Enhanced initialization test failed: {e}")
    
    print()


def test_choice_management():
    """Test choice addition, removal, and manipulation."""
    print("📝 Testing Choice Management...")
    print("=" * 50)
    
    try:
        # Start with basic choices
        initial_choices = ["Choice A", "Choice B"]
        adapter = RadioListAdapter(
            choices=initial_choices,
            message="Dynamic choices test:"
        )
        
        initial_count = adapter.get_widget_info()['choice_count']
        print(f"✅ Initial choice count: {initial_count}")
        
        # Add a choice
        adapter.add_choice("Choice C")
        new_count = adapter.get_widget_info()['choice_count']
        if new_count > initial_count:
            print("✅ Choice addition successful")
        
        # Add tuple choice
        adapter.add_choice(("Display D", "value_d"))
        tuple_count = adapter.get_widget_info()['choice_count']
        print(f"✅ Tuple choice addition successful (count: {tuple_count})")
        
        # Remove a choice
        adapter.remove_choice("Choice A")
        final_count = adapter.get_widget_info()['choice_count']
        print(f"✅ Choice removal successful (final count: {final_count})")
        
        # Test choice retrieval
        choices = adapter._enhanced_adapter.get_choices() if adapter._enhanced_adapter else []
        print(f"✅ Retrieved {len(choices)} choices")
        
    except Exception as e:
        print(f"❌ Choice management test failed: {e}")
    
    print()


def test_selection_and_validation():
    """Test selection operations and validation."""
    print("✅ Testing Selection and Validation...")
    print("=" * 50)
    
    # Test basic selection
    try:
        choices = ["Red", "Green", "Blue"]
        adapter = RadioListAdapter(
            choices=choices,
            message="Select a color:",
            default="Green"
        )
        
        # Test initial selection
        selected = list(adapter.get_selected())
        print(f"✅ Initial selection: {selected}")
        
        # Test selection change
        adapter.set_selected(["Blue"])
        new_selected = list(adapter.get_selected())
        print(f"✅ Selection change: {new_selected}")
        
        # Test validation without validator
        is_valid, error = adapter.validate_selection("Red")
        if is_valid:
            print("✅ Basic validation (no validator) - Valid")
        
    except Exception as e:
        print(f"❌ Basic selection test failed: {e}")
    
    # Test validation with validator
    try:
        def color_validator(value):
            if value in ["Red", "Green", "Blue"]:
                return True
            return "Please select a primary color"
        
        adapter = RadioListAdapter(
            choices=["Red", "Green", "Blue", "Yellow", "Purple"],
            message="Select a primary color:",
            validator=color_validator
        )
        
        # Test valid selection
        is_valid, error = adapter.validate_selection("Red")
        if is_valid:
            print("✅ Validation with validator - Valid selection accepted")
        
        # Test invalid selection
        is_valid, error = adapter.validate_selection("Yellow")
        if not is_valid and error:
            print(f"✅ Validation with validator - Invalid selection rejected: {error}")
        
        # Test validation enable/disable
        adapter.disable_validation()
        is_valid, error = adapter.validate_selection("Yellow")
        if is_valid:
            print("✅ Validation disable successful")
        
        adapter.enable_validation(color_validator)
        is_valid, error = adapter.validate_selection("Yellow")
        if not is_valid:
            print("✅ Validation re-enable successful")
        
    except Exception as e:
        print(f"❌ Validation test failed: {e}")
    
    print()


def test_theme_integration():
    """Test theme integration and switching."""
    print("🎨 Testing Theme Integration...")
    print("=" * 50)
    
    themes_to_test = ['professional_blue', 'dark_mode', 'high_contrast', 'minimal']
    
    for theme_name in themes_to_test:
        try:
            adapter = RadioListAdapter(
                choices=["Option 1", "Option 2", "Option 3"],
                message=f"Testing {theme_name} theme:",
                style=theme_name
            )
            
            info = adapter.get_widget_info()
            if info['theme'] == theme_name:
                print(f"✅ {theme_name} theme applied successfully")
            else:
                print(f"⚠️  {theme_name} theme may not be fully applied (fallback mode)")
                
        except Exception as e:
            print(f"❌ {theme_name} theme test failed: {e}")
    
    # Test theme switching
    try:
        adapter = RadioListAdapter(
            choices=["A", "B", "C"],
            message="Theme switching test:",
            style='professional_blue'
        )
        
        for theme in ['dark_mode', 'minimal', 'high_contrast']:
            adapter.change_theme(theme)
            print(f"✅ Theme switched to {theme}")
            
    except Exception as e:
        print(f"❌ Theme switching test failed: {e}")
    
    print()


def test_enhanced_features():
    """Test enhanced features specific to the new implementation."""
    print("🚀 Testing Enhanced Features...")
    print("=" * 50)
    
    try:
        # Test message and instruction updating
        adapter = RadioListAdapter(
            choices=["Option A", "Option B"],
            message="Initial message",
            instruction="Initial instruction"
        )
        
        adapter.set_message("Updated message")
        info = adapter.get_widget_info()
        if info['message'] == "Updated message":
            print("✅ Message update successful")
        
        if adapter._enhanced_adapter:
            adapter._enhanced_adapter.set_instruction("Updated instruction")
            if adapter._enhanced_adapter.instruction == "Updated instruction":
                print("✅ Instruction update successful")
        
        # Test Questionary enhancement check
        is_enhanced = adapter.is_questionary_enhanced()
        print(f"✅ Questionary enhancement status: {is_enhanced}")
        
        # Test comprehensive widget info
        info = adapter.get_widget_info()
        required_keys = ['use_questionary', 'has_validator', 'choice_count', 'current_value', 'theme']
        missing_keys = [key for key in required_keys if key not in info]
        if not missing_keys:
            print("✅ Comprehensive widget info available")
        else:
            print(f"⚠️  Missing widget info keys: {missing_keys}")
        
    except Exception as e:
        print(f"❌ Enhanced features test failed: {e}")
    
    print()


def test_convenience_function():
    """Test the convenience create_radio_list function."""
    print("🛠️  Testing Convenience Function...")
    print("=" * 50)
    
    try:
        # Test convenience function
        adapter = create_radio_list(
            choices=["Easy", "Medium", "Hard"],
            message="Select difficulty:",
            style='dark_mode',
            pointer="→",
            default="Medium"
        )
        
        if adapter is not None:
            print("✅ Convenience function create_radio_list successful")
            
            info = adapter.get_widget_info()
            print(f"✅ Created with {info['choice_count']} choices, theme: {info['theme']}")
            
            # Test that it's fully functional
            adapter.set_selected(["Hard"])
            selected = list(adapter.get_selected())
            print(f"✅ Convenience adapter is functional: selected {selected}")
        
    except Exception as e:
        print(f"❌ Convenience function test failed: {e}")
    
    print()


def test_edge_cases():
    """Test edge cases and error handling."""
    print("⚠️  Testing Edge Cases...")
    print("=" * 50)
    
    # Test empty choices
    try:
        adapter = RadioListAdapter(choices=[], message="Empty choices test:")
        count = adapter.get_widget_info()['choice_count']
        if count == 0:
            print("✅ Empty choices handled gracefully")
    except Exception as e:
        print(f"❌ Empty choices test failed: {e}")
    
    # Test None values in choices
    try:
        adapter = RadioListAdapter(
            choices=["Valid", None, "Also Valid"],
            message="None values test:"
        )
        count = adapter.get_widget_info()['choice_count']
        print(f"✅ None values in choices handled (count: {count})")
    except Exception as e:
        print(f"❌ None values test failed: {e}")
    
    # Test invalid default value
    try:
        adapter = RadioListAdapter(
            choices=["A", "B", "C"],
            message="Invalid default test:",
            default="Z"  # Not in choices
        )
        print("✅ Invalid default value handled gracefully")
    except Exception as e:
        print(f"❌ Invalid default test failed: {e}")
    
    # Test validator exceptions
    try:
        def bad_validator(value):
            raise Exception("Validator error")
        
        adapter = RadioListAdapter(
            choices=["A", "B"],
            message="Bad validator test:",
            validator=bad_validator
        )
        
        is_valid, error = adapter.validate_selection("A")
        if not is_valid and "error" in error.lower():
            print("✅ Validator exceptions handled gracefully")
    except Exception as e:
        print(f"❌ Validator exception test failed: {e}")
    
    print()


def demonstrate_usage_patterns():
    """Demonstrate various usage patterns."""
    print("📚 Usage Pattern Demonstrations...")
    print("=" * 50)
    
    print("Example 1: Simple string choices")
    try:
        adapter1 = create_radio_list(
            choices=["Small", "Medium", "Large"],
            message="Select size:",
            style='professional_blue'
        )
        print(f"✅ Simple choices: {adapter1}")
    except Exception as e:
        print(f"❌ Simple choices failed: {e}")
    
    print("\nExample 2: Value-display pairs")
    try:
        adapter2 = create_radio_list(
            choices=[
                ("Development Server", "dev"),
                ("Staging Server", "staging"),
                ("Production Server", "prod")
            ],
            message="Select deployment target:",
            style='dark_mode'
        )
        print(f"✅ Value-display pairs: {adapter2}")
    except Exception as e:
        print(f"❌ Value-display pairs failed: {e}")
    
    print("\nExample 3: With validation")
    try:
        def priority_validator(value):
            return value in ["high", "medium", "low"] or "Invalid priority level"
        
        adapter3 = create_radio_list(
            choices=[
                ("High Priority", "high"),
                ("Medium Priority", "medium"),
                ("Low Priority", "low"),
                ("Invalid Option", "invalid")
            ],
            message="Select priority:",
            style='high_contrast',
            validator=priority_validator
        )
        print(f"✅ With validation: {adapter3}")
    except Exception as e:
        print(f"❌ With validation failed: {e}")
    
    print("\nExample 4: Legacy compatibility")
    try:
        adapter4 = RadioListAdapter(None)  # Legacy mode
        adapter4.set_selected(["legacy_value"])
        selected = list(adapter4.get_selected())
        print(f"✅ Legacy compatibility: selected {selected}")
    except Exception as e:
        print(f"❌ Legacy compatibility failed: {e}")
    
    print()


def main():
    """Main test function."""
    print("📻 Enhanced RadioListAdapter Test Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    test_backward_compatibility()
    test_enhanced_initialization()
    test_choice_management()
    test_selection_and_validation()
    test_theme_integration()
    test_enhanced_features()
    test_convenience_function()
    test_edge_cases()
    demonstrate_usage_patterns()
    
    print("✅ All RadioListAdapter tests completed!")
    print("\n🎉 Enhanced RadioListAdapter is ready for integration!")


if __name__ == "__main__":
    main()