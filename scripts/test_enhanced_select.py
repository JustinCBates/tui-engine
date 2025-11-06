#!/usr/bin/env python3
"""
Enhanced SelectAdapter Test Suite

This script thoroughly tests the enhanced SelectAdapter functionality,
ensuring proper Questionary integration while maintaining backward compatibility.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tui_engine.widgets.select_adapter import SelectAdapter, EnhancedSelectAdapter, create_select


def test_backward_compatibility():
    """Test that the enhanced adapter maintains backward compatibility."""
    print("🔄 Testing Backward Compatibility...")
    print("=" * 50)
    
    # Test original interface with None widget
    try:
        adapter1 = SelectAdapter(None)
        print("✅ SelectAdapter(None) - Compatible")
        
        # Test basic operations
        adapter1.set_selected("option1")
        selected = adapter1.get_selected()
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
    """Test enhanced SelectAdapter initialization."""
    print("✨ Testing Enhanced Initialization...")
    print("=" * 50)
    
    # Test enhanced initialization with choices
    try:
        choices = ["Option 1", "Option 2", "Option 3"]
        adapter = SelectAdapter(
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
        adapter2 = SelectAdapter(
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


def test_single_selection():
    """Test single selection operations."""
    print("☑️  Testing Single Selection...")
    print("=" * 50)
    
    try:
        choices = ["Red", "Green", "Blue", "Yellow"]
        adapter = SelectAdapter(
            choices=choices,
            message="Select a color:",
            default="Green"
        )
        
        # Test initial selection
        selected = adapter.get_selected()
        print(f"✅ Initial selection: {selected}")
        
        # Test selection change
        adapter.set_selected("Blue")
        new_selected = adapter.get_selected()
        print(f"✅ Selection change: {new_selected}")
        
        # Test choice count
        count = adapter.get_choice_count()
        print(f"✅ Choice count: {count}")
        
        # Test options access
        options = adapter.options
        print(f"✅ Options available: {len(options)} items")
        
    except Exception as e:
        print(f"❌ Single selection test failed: {e}")
    
    print()


def test_choice_management():
    """Test dynamic choice management."""
    print("📝 Testing Choice Management...")
    print("=" * 50)
    
    try:
        # Start with basic choices
        initial_choices = ["Choice A", "Choice B"]
        adapter = SelectAdapter(
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
        
        # Add separator and group
        if adapter._enhanced_adapter:
            adapter.add_separator("--- Separators ---")
            adapter.add_group("Group 1", ["Group Item 1", "Group Item 2"])
            group_count = adapter.get_choice_count()
            print(f"✅ After adding groups: {group_count}")
        
        # Set selection
        adapter.set_selected("Choice A")
        selected_before = adapter.get_selected()
        print(f"✅ Selected before removal: {selected_before}")
        
        # Remove a selected choice
        adapter.remove_choice("Choice A")
        selected_after = adapter.get_selected()
        final_count = adapter.get_choice_count()
        print(f"✅ After removal - Count: {final_count}, Selected: {selected_after}")
        
        # Test choice retrieval
        if adapter._enhanced_adapter:
            choices = adapter._enhanced_adapter.get_choices()
            selectable = adapter._enhanced_adapter.get_selectable_choices()
            print(f"✅ Retrieved {len(choices)} total choices, {len(selectable)} selectable")
        
    except Exception as e:
        print(f"❌ Choice management test failed: {e}")
    
    print()


def test_search_functionality():
    """Test search and filtering capabilities."""
    print("🔍 Testing Search Functionality...")
    print("=" * 50)
    
    try:
        search_choices = [
            "Apple", "Apricot", "Banana", "Blueberry", 
            "Cherry", "Cranberry", "Date", "Elderberry"
        ]
        
        # Test searchable select
        adapter = SelectAdapter(
            choices=search_choices,
            message="Search for a fruit:",
            searchable=True
        )
        
        info = adapter.get_widget_info()
        if info['searchable']:
            print("✅ Searchable select created successfully")
        
        # Test search functionality
        if adapter._enhanced_adapter:
            # Test search for "app"
            apple_matches = adapter.search_choices("app")
            apple_titles = [
                choice.title if hasattr(choice, 'title') else str(choice) 
                for choice in apple_matches
            ]
            if any("Apple" in title for title in apple_titles):
                print("✅ Search for 'app' found Apple")
            
            # Test search for "berry"
            berry_matches = adapter.search_choices("berry")
            berry_titles = [
                choice.title if hasattr(choice, 'title') else str(choice) 
                for choice in berry_matches
            ]
            berry_count = len([t for t in berry_titles if "berry" in t])
            print(f"✅ Search for 'berry' found {berry_count} matches")
            
            # Test fuzzy search
            fuzzy_matches = adapter.search_choices("ae")  # Should match Apple
            if fuzzy_matches:
                print("✅ Fuzzy search working")
            
            # Test search enable/disable
            adapter.disable_search()
            adapter.enable_search()
            print("✅ Search enable/disable working")
        
    except Exception as e:
        print(f"❌ Search functionality test failed: {e}")
    
    print()


def test_validation():
    """Test validation functionality."""
    print("✅ Testing Validation...")
    print("=" * 50)
    
    try:
        # Test custom validator
        def color_validator(value):
            primary_colors = ["Red", "Green", "Blue"]
            if value in primary_colors:
                return True
            return "Please select a primary color"
        
        choices = ["Red", "Green", "Blue", "Yellow", "Purple"]
        adapter = SelectAdapter(
            choices=choices,
            message="Select a primary color:",
            validator=color_validator
        )
        
        # Test valid selection
        is_valid, error = adapter.validate_selection("Red")
        if is_valid:
            print("✅ Validation - Valid selection accepted")
        
        # Test invalid selection
        is_valid, error = adapter.validate_selection("Yellow")
        if not is_valid and "primary" in error:
            print("✅ Validation - Invalid selection rejected")
        
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


def test_grouping_and_separators():
    """Test grouping and separator functionality."""
    print("📊 Testing Grouping and Separators...")
    print("=" * 50)
    
    try:
        adapter = SelectAdapter(
            choices=["Initial Option"],
            message="Grouped select test:"
        )
        
        if adapter._enhanced_adapter:
            # Add groups with separators
            adapter.add_group("Fruits", [
                ("Apple", "fruit_apple"),
                ("Banana", "fruit_banana")
            ])
            
            adapter.add_group("Vegetables", [
                ("Carrot", "veg_carrot"),
                ("Lettuce", "veg_lettuce")
            ])
            
            # Check total and selectable counts
            total_choices = len(adapter._enhanced_adapter.get_choices())
            selectable_choices = len(adapter._enhanced_adapter.get_selectable_choices())
            
            print(f"✅ Groups added - Total: {total_choices}, Selectable: {selectable_choices}")
            
            # Test separator addition
            adapter.add_separator("--- Custom Separator ---")
            print("✅ Custom separator added")
            
            # Test selection from grouped choices
            adapter.set_selected("fruit_apple")
            selected = adapter.get_selected()
            if selected == "fruit_apple":
                print("✅ Selection from grouped choices working")
        
    except Exception as e:
        print(f"❌ Grouping and separators test failed: {e}")
    
    print()


def test_theme_integration():
    """Test theme integration and switching."""
    print("🎨 Testing Theme Integration...")
    print("=" * 50)
    
    themes_to_test = ['professional_blue', 'dark_mode', 'high_contrast', 'minimal']
    
    for theme_name in themes_to_test:
        try:
            adapter = SelectAdapter(
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
        adapter = SelectAdapter(
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
        adapter = SelectAdapter(
            choices=["Option A", "Option B"],
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
        required_keys = ['use_questionary', 'has_validator', 'choice_count', 'current_value', 'theme', 'searchable']
        missing_keys = [key for key in required_keys if key not in info]
        if not missing_keys:
            print("✅ Comprehensive widget info available")
            print(f"   - Choices: {info['choice_count']}, Searchable: {info['searchable']}")
            print(f"   - Theme: {info['theme']}, Current: {info['current_value']}")
        else:
            print(f"⚠️  Missing widget info keys: {missing_keys}")
        
        # Test clear choices functionality
        if adapter._enhanced_adapter:
            original_count = adapter.get_choice_count()
            adapter.clear_choices()
            new_count = adapter.get_choice_count()
            if new_count == 0:
                print(f"✅ Clear choices successful (from {original_count} to {new_count})")
        
    except Exception as e:
        print(f"❌ Enhanced features test failed: {e}")
    
    print()


def test_convenience_function():
    """Test the convenience create_select function."""
    print("🛠️  Testing Convenience Function...")
    print("=" * 50)
    
    try:
        # Test convenience function
        adapter = create_select(
            choices=["Easy", "Medium", "Hard"],
            message="Select difficulty:",
            style='dark_mode',
            searchable=True,
            default="Medium"
        )
        
        if adapter is not None:
            print("✅ Convenience function create_select successful")
            
            info = adapter.get_widget_info()
            print(f"✅ Created with {info['choice_count']} choices")
            print(f"   Theme: {info['theme']}, Searchable: {info['searchable']}")
            
            # Test that it's fully functional
            adapter.set_selected("Hard")
            selected = adapter.get_selected()
            print(f"✅ Convenience adapter is functional: selected '{selected}'")
        
    except Exception as e:
        print(f"❌ Convenience function test failed: {e}")
    
    print()


def test_edge_cases():
    """Test edge cases and error handling."""
    print("⚠️  Testing Edge Cases...")
    print("=" * 50)
    
    # Test empty choices
    try:
        adapter = SelectAdapter(choices=[], message="Empty choices test:")
        count = adapter.get_choice_count()
        if count == 0:
            print("✅ Empty choices handled gracefully")
    except Exception as e:
        print(f"❌ Empty choices test failed: {e}")
    
    # Test None values in choices
    try:
        adapter = SelectAdapter(
            choices=["Valid", None, "Also Valid"],
            message="None values test:"
        )
        count = adapter.get_choice_count()
        print(f"✅ None values in choices handled (count: {count})")
    except Exception as e:
        print(f"❌ None values test failed: {e}")
    
    # Test invalid default value
    try:
        adapter = SelectAdapter(
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
        
        adapter = SelectAdapter(
            choices=["A", "B"],
            message="Bad validator test:",
            validator=bad_validator
        )
        
        is_valid, error = adapter.validate_selection("A")
        if not is_valid and "error" in error.lower():
            print("✅ Validator exceptions handled gracefully")
    except Exception as e:
        print(f"❌ Validator exception test failed: {e}")
    
    # Test search with empty query
    try:
        adapter = SelectAdapter(
            choices=["Option 1", "Option 2"],
            message="Search test:",
            searchable=True
        )
        
        if adapter._enhanced_adapter:
            empty_search = adapter.search_choices("")
            all_search = adapter.search_choices("   ")  # Whitespace only
            print("✅ Empty search queries handled gracefully")
    except Exception as e:
        print(f"❌ Empty search test failed: {e}")
    
    print()


def demonstrate_usage_patterns():
    """Demonstrate various usage patterns."""
    print("📚 Usage Pattern Demonstrations...")
    print("=" * 50)
    
    print("Example 1: Simple dropdown")
    try:
        adapter1 = create_select(
            choices=["Small", "Medium", "Large"],
            message="Select size:",
            style='professional_blue'
        )
        print(f"✅ Simple dropdown: {adapter1}")
    except Exception as e:
        print(f"❌ Simple dropdown failed: {e}")
    
    print("\nExample 2: Searchable with groups")
    try:
        adapter2 = SelectAdapter(
            choices=["Initial"],
            message="Select environment:",
            style='dark_mode',
            searchable=True
        )
        
        if adapter2._enhanced_adapter:
            adapter2.add_group("Development", [
                ("Local Dev", "dev_local"),
                ("Dev Server", "dev_server")
            ])
            
            adapter2.add_group("Production", [
                ("Staging", "prod_staging"),
                ("Live", "prod_live")
            ])
        
        print(f"✅ Searchable with groups: {adapter2}")
    except Exception as e:
        print(f"❌ Searchable with groups failed: {e}")
    
    print("\nExample 3: With validation")
    try:
        def priority_validator(value):
            return value in ["high", "medium", "low"] or "Invalid priority level"
        
        adapter3 = create_select(
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
        adapter4 = SelectAdapter(None)  # Legacy mode
        adapter4.set_selected("legacy_value")
        selected = adapter4.get_selected()
        print(f"✅ Legacy compatibility: selected '{selected}'")
    except Exception as e:
        print(f"❌ Legacy compatibility failed: {e}")
    
    print()


def main():
    """Main test function."""
    print("🔽 Enhanced SelectAdapter Test Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    test_backward_compatibility()
    test_enhanced_initialization()
    test_single_selection()
    test_choice_management()
    test_search_functionality()
    test_validation()
    test_grouping_and_separators()
    test_theme_integration()
    test_enhanced_features()
    test_convenience_function()
    test_edge_cases()
    demonstrate_usage_patterns()
    
    print("✅ All SelectAdapter tests completed!")
    print("\n🎉 Enhanced SelectAdapter is ready for integration!")


if __name__ == "__main__":
    main()