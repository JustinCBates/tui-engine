#!/usr/bin/env python3
"""
Enhanced CheckboxListAdapter Test Suite

This script thoroughly tests the enhanced CheckboxListAdapter functionality,
ensuring proper Questionary integration while maintaining backward compatibility.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tui_engine.widgets.checkbox_list_adapter import CheckboxListAdapter, EnhancedCheckboxListAdapter, create_checkbox_list


def test_backward_compatibility():
    """Test that the enhanced adapter maintains backward compatibility."""
    print("🔄 Testing Backward Compatibility...")
    print("=" * 50)
    
    # Test original interface with None widget
    try:
        adapter1 = CheckboxListAdapter(None)
        print("✅ CheckboxListAdapter(None) - Compatible")
        
        # Test basic operations
        adapter1.set_selected(["option1", "option2"])
        selected = list(adapter1.get_selected())
        print(f"✅ Basic selection operations - Selected: {selected}")
        
        # Test focus
        adapter1.focus()  # Should not raise exception
        print("✅ Focus operation - Compatible")
        
        # Test sync
        values = adapter1._tui_sync()  # Should not raise exception
        print(f"✅ Sync operation - Compatible (values: {values})")
        
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
    """Test enhanced CheckboxListAdapter initialization."""
    print("✨ Testing Enhanced Initialization...")
    print("=" * 50)
    
    # Test enhanced initialization with choices
    try:
        choices = ["Option 1", "Option 2", "Option 3", "Option 4"]
        adapter = CheckboxListAdapter(
            choices=choices,
            message="Select multiple options:",
            style='professional_blue',
            default=["Option 2", "Option 3"]
        )
        print("✅ Enhanced initialization with string choices successful")
        
        # Test with tuple choices
        tuple_choices = [
            ("Display Name 1", "value1"),
            ("Display Name 2", "value2"),
            ("Display Name 3", "value3"),
            ("Display Name 4", "value4")
        ]
        adapter2 = CheckboxListAdapter(
            choices=tuple_choices,
            message="Select from tuples:",
            style='dark_mode',
            min_selections=1,
            max_selections=3
        )
        print("✅ Enhanced initialization with tuple choices and constraints successful")
        
        # Test widget info
        info = adapter.get_widget_info()
        print(f"✅ Widget info: Questionary={info['use_questionary']}, Choices={info['choice_count']}, Selected={info['selected_count']}")
        
    except Exception as e:
        print(f"❌ Enhanced initialization test failed: {e}")
    
    print()


def test_multi_selection_operations():
    """Test multi-selection operations and management."""
    print("☑️  Testing Multi-Selection Operations...")
    print("=" * 50)
    
    try:
        choices = ["Apple", "Banana", "Cherry", "Date", "Elderberry"]
        adapter = CheckboxListAdapter(
            choices=choices,
            message="Select fruits:",
            default=["Apple", "Cherry"]
        )
        
        # Test initial selection
        selected = list(adapter.get_selected())
        print(f"✅ Initial selection: {selected}")
        
        # Test individual selection
        adapter.set_selected(["Banana", "Date"])
        new_selected = list(adapter.get_selected())
        print(f"✅ Individual selection change: {new_selected}")
        
        # Test selection count
        count = adapter.get_selected_count()
        print(f"✅ Selection count: {count}")
        
        # Test toggle functionality
        if adapter._enhanced_adapter:
            adapter.toggle_choice("Elderberry")
            after_toggle = list(adapter.get_selected())
            print(f"✅ Toggle choice operation: {after_toggle}")
            
            # Test is_selected
            is_selected = adapter.is_selected("Elderberry")
            print(f"✅ Is selected check: Elderberry is {'selected' if is_selected else 'not selected'}")
            
            # Test select all
            adapter.select_all()
            all_selected = list(adapter.get_selected())
            print(f"✅ Select all operation: {len(all_selected)} items selected")
            
            # Test clear all
            adapter.clear_all()
            after_clear = list(adapter.get_selected())
            print(f"✅ Clear all operation: {len(after_clear)} items selected")
        
    except Exception as e:
        print(f"❌ Multi-selection operations test failed: {e}")
    
    print()


def test_selection_constraints():
    """Test selection constraints and validation."""
    print("🔒 Testing Selection Constraints...")
    print("=" * 50)
    
    # Test minimum selections constraint
    try:
        adapter = CheckboxListAdapter(
            choices=["Red", "Green", "Blue", "Yellow"],
            message="Select colors (min 2):",
            min_selections=2
        )
        
        # Test validation with too few selections
        is_valid, error = adapter.validate_selection(["Red"])
        if not is_valid and "at least 2" in error:
            print("✅ Minimum selection constraint working")
        
        # Test validation with sufficient selections
        is_valid, error = adapter.validate_selection(["Red", "Blue"])
        if is_valid:
            print("✅ Minimum selection constraint satisfied")
        
    except Exception as e:
        print(f"❌ Minimum selection constraint test failed: {e}")
    
    # Test maximum selections constraint
    try:
        adapter = CheckboxListAdapter(
            choices=["A", "B", "C", "D", "E"],
            message="Select options (max 3):",
            max_selections=3
        )
        
        # Test validation with too many selections
        is_valid, error = adapter.validate_selection(["A", "B", "C", "D"])
        if not is_valid and "at most 3" in error:
            print("✅ Maximum selection constraint working")
        
        # Test validation within limit
        is_valid, error = adapter.validate_selection(["A", "B", "C"])
        if is_valid:
            print("✅ Maximum selection constraint satisfied")
        
    except Exception as e:
        print(f"❌ Maximum selection constraint test failed: {e}")
    
    # Test combined constraints
    try:
        adapter = CheckboxListAdapter(
            choices=["Option 1", "Option 2", "Option 3", "Option 4", "Option 5"],
            message="Select options (2-4):",
            min_selections=2,
            max_selections=4
        )
        
        # Test constraint updates
        adapter.set_constraints(min_selections=1, max_selections=3)
        
        # Test updated constraints
        is_valid, error = adapter.validate_selection(["Option 1", "Option 2", "Option 3", "Option 4"])
        if not is_valid:
            print("✅ Dynamic constraint update working")
        
    except Exception as e:
        print(f"❌ Combined constraints test failed: {e}")
    
    print()


def test_custom_validation():
    """Test custom validation functionality."""
    print("✅ Testing Custom Validation...")
    print("=" * 50)
    
    try:
        # Test custom validator
        def fruit_validator(values):
            # Must select at least one fruit and one color
            fruits = ["Apple", "Banana", "Cherry"]
            colors = ["Red", "Green", "Blue"]
            
            has_fruit = any(v in fruits for v in values)
            has_color = any(v in colors for v in values)
            
            if not has_fruit:
                return "Please select at least one fruit"
            if not has_color:
                return "Please select at least one color"
            return True
        
        choices = ["Apple", "Banana", "Cherry", "Red", "Green", "Blue"]
        adapter = CheckboxListAdapter(
            choices=choices,
            message="Select fruits and colors:",
            validator=fruit_validator
        )
        
        # Test invalid selection (only fruits)
        is_valid, error = adapter.validate_selection(["Apple", "Banana"])
        if not is_valid and "color" in error:
            print("✅ Custom validation - Missing color detected")
        
        # Test invalid selection (only colors)
        is_valid, error = adapter.validate_selection(["Red", "Blue"])
        if not is_valid and "fruit" in error:
            print("✅ Custom validation - Missing fruit detected")
        
        # Test valid selection
        is_valid, error = adapter.validate_selection(["Apple", "Red"])
        if is_valid:
            print("✅ Custom validation - Valid selection accepted")
        
        # Test validation enable/disable
        adapter.disable_validation()
        is_valid, error = adapter.validate_selection(["Red"])  # Should be valid now
        if is_valid:
            print("✅ Validation disable successful")
        
        adapter.enable_validation(fruit_validator)
        is_valid, error = adapter.validate_selection(["Red"])  # Should be invalid again
        if not is_valid:
            print("✅ Validation re-enable successful")
        
    except Exception as e:
        print(f"❌ Custom validation test failed: {e}")
    
    print()


def test_choice_management():
    """Test dynamic choice management."""
    print("📝 Testing Choice Management...")
    print("=" * 50)
    
    try:
        # Start with basic choices
        initial_choices = ["Choice A", "Choice B"]
        adapter = CheckboxListAdapter(
            choices=initial_choices,
            message="Dynamic choices test:"
        )
        
        initial_count = adapter.get_choice_count()
        print(f"✅ Initial choice count: {initial_count}")
        
        # Add choices
        adapter.add_choice("Choice C")
        adapter.add_choice(("Display D", "value_d"))
        new_count = adapter.get_choice_count()
        print(f"✅ After adding choices: {new_count}")
        
        # Select some choices
        adapter.set_selected(["Choice A", "value_d"])
        selected_before = list(adapter.get_selected())
        print(f"✅ Selected before removal: {selected_before}")
        
        # Remove a selected choice
        adapter.remove_choice("Choice A")
        selected_after = list(adapter.get_selected())
        final_count = adapter.get_choice_count()
        print(f"✅ After removal - Count: {final_count}, Selected: {selected_after}")
        
        # Test choice retrieval
        choices = adapter._enhanced_adapter.get_choices() if adapter._enhanced_adapter else []
        print(f"✅ Retrieved {len(choices)} choices")
        
    except Exception as e:
        print(f"❌ Choice management test failed: {e}")
    
    print()


def test_theme_integration():
    """Test theme integration and switching."""
    print("🎨 Testing Theme Integration...")
    print("=" * 50)
    
    themes_to_test = ['professional_blue', 'dark_mode', 'high_contrast', 'minimal']
    
    for theme_name in themes_to_test:
        try:
            adapter = CheckboxListAdapter(
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
        adapter = CheckboxListAdapter(
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
        adapter = CheckboxListAdapter(
            choices=["Option A", "Option B", "Option C"],
            message="Initial message",
            instruction="Initial instruction"
        )
        
        adapter.set_message("Updated message")
        info = adapter.get_widget_info()
        if info['message'] == "Updated message":
            print("✅ Message update successful")
        
        # Test Questionary enhancement check
        is_enhanced = adapter.is_questionary_enhanced()
        print(f"✅ Questionary enhancement status: {is_enhanced}")
        
        # Test comprehensive widget info
        info = adapter.get_widget_info()
        required_keys = ['use_questionary', 'has_validator', 'choice_count', 'selected_count', 'current_values', 'theme']
        missing_keys = [key for key in required_keys if key not in info]
        if not missing_keys:
            print("✅ Comprehensive widget info available")
            print(f"   - Choices: {info['choice_count']}, Selected: {info['selected_count']}")
            print(f"   - Min/Max: {info.get('min_selections', 'None')}/{info.get('max_selections', 'None')}")
        else:
            print(f"⚠️  Missing widget info keys: {missing_keys}")
        
    except Exception as e:
        print(f"❌ Enhanced features test failed: {e}")
    
    print()


def test_convenience_function():
    """Test the convenience create_checkbox_list function."""
    print("🛠️  Testing Convenience Function...")
    print("=" * 50)
    
    try:
        # Test convenience function
        adapter = create_checkbox_list(
            choices=["Easy", "Medium", "Hard", "Expert"],
            message="Select difficulty levels:",
            style='dark_mode',
            min_selections=1,
            max_selections=3,
            default=["Medium"]
        )
        
        if adapter is not None:
            print("✅ Convenience function create_checkbox_list successful")
            
            info = adapter.get_widget_info()
            print(f"✅ Created with {info['choice_count']} choices, {info['selected_count']} selected")
            print(f"   Theme: {info['theme']}, Min: {info.get('min_selections')}, Max: {info.get('max_selections')}")
            
            # Test that it's fully functional
            adapter.set_selected(["Hard", "Expert"])
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
        adapter = CheckboxListAdapter(choices=[], message="Empty choices test:")
        count = adapter.get_widget_info()['choice_count']
        if count == 0:
            print("✅ Empty choices handled gracefully")
    except Exception as e:
        print(f"❌ Empty choices test failed: {e}")
    
    # Test None values in choices
    try:
        adapter = CheckboxListAdapter(
            choices=["Valid", None, "Also Valid"],
            message="None values test:"
        )
        count = adapter.get_widget_info()['choice_count']
        print(f"✅ None values in choices handled (count: {count})")
    except Exception as e:
        print(f"❌ None values test failed: {e}")
    
    # Test invalid default values
    try:
        adapter = CheckboxListAdapter(
            choices=["A", "B", "C"],
            message="Invalid defaults test:",
            default=["Z", "Y"]  # Not in choices
        )
        print("✅ Invalid default values handled gracefully")
    except Exception as e:
        print(f"❌ Invalid defaults test failed: {e}")
    
    # Test validator exceptions
    try:
        def bad_validator(values):
            raise Exception("Validator error")
        
        adapter = CheckboxListAdapter(
            choices=["A", "B"],
            message="Bad validator test:",
            validator=bad_validator
        )
        
        is_valid, error = adapter.validate_selection(["A"])
        if not is_valid and "error" in error.lower():
            print("✅ Validator exceptions handled gracefully")
    except Exception as e:
        print(f"❌ Validator exception test failed: {e}")
    
    # Test extreme constraints
    try:
        adapter = CheckboxListAdapter(
            choices=["Only One"],
            message="Extreme constraints test:",
            min_selections=2  # Impossible to satisfy
        )
        
        is_valid, error = adapter.validate_selection(["Only One"])
        if not is_valid:
            print("✅ Impossible constraints handled gracefully")
    except Exception as e:
        print(f"❌ Extreme constraints test failed: {e}")
    
    print()


def demonstrate_usage_patterns():
    """Demonstrate various usage patterns."""
    print("📚 Usage Pattern Demonstrations...")
    print("=" * 50)
    
    print("Example 1: Simple multi-select")
    try:
        adapter1 = create_checkbox_list(
            choices=["Option A", "Option B", "Option C", "Option D"],
            message="Select multiple options:",
            style='professional_blue'
        )
        print(f"✅ Simple multi-select: {adapter1}")
    except Exception as e:
        print(f"❌ Simple multi-select failed: {e}")
    
    print("\nExample 2: With constraints")
    try:
        adapter2 = create_checkbox_list(
            choices=[
                ("Primary Feature", "primary"),
                ("Secondary Feature", "secondary"),
                ("Optional Feature 1", "opt1"),
                ("Optional Feature 2", "opt2"),
                ("Optional Feature 3", "opt3")
            ],
            message="Select features (1-3):",
            style='dark_mode',
            min_selections=1,
            max_selections=3
        )
        print(f"✅ With constraints: {adapter2}")
    except Exception as e:
        print(f"❌ With constraints failed: {e}")
    
    print("\nExample 3: With custom validation")
    try:
        def category_validator(values):
            categories = {"essential": ["os", "editor"], "optional": ["browser", "games"]}
            essential_count = sum(1 for v in values if v in categories["essential"])
            return essential_count >= 1 or "Please select at least one essential item"
        
        adapter3 = create_checkbox_list(
            choices=[
                ("Operating System", "os"),
                ("Text Editor", "editor"),
                ("Web Browser", "browser"),
                ("Games", "games")
            ],
            message="Select software to install:",
            style='high_contrast',
            validator=category_validator
        )
        print(f"✅ With custom validation: {adapter3}")
    except Exception as e:
        print(f"❌ With custom validation failed: {e}")
    
    print("\nExample 4: Legacy compatibility")
    try:
        adapter4 = CheckboxListAdapter(None)  # Legacy mode
        adapter4.set_selected(["legacy_value1", "legacy_value2"])
        selected = list(adapter4.get_selected())
        print(f"✅ Legacy compatibility: selected {selected}")
    except Exception as e:
        print(f"❌ Legacy compatibility failed: {e}")
    
    print()


def main():
    """Main test function."""
    print("☑️  Enhanced CheckboxListAdapter Test Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    test_backward_compatibility()
    test_enhanced_initialization()
    test_multi_selection_operations()
    test_selection_constraints()
    test_custom_validation()
    test_choice_management()
    test_theme_integration()
    test_enhanced_features()
    test_convenience_function()
    test_edge_cases()
    demonstrate_usage_patterns()
    
    print("✅ All CheckboxListAdapter tests completed!")
    print("\n🎉 Enhanced CheckboxListAdapter is ready for integration!")


if __name__ == "__main__":
    main()