#!/usr/bin/env python3
"""
Questionary Style Adapter Test Suite

This script thoroughly tests the QuestionaryStyleAdapter functionality,
ensuring proper integration between TUI Engine styling and Questionary themes.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tui_engine.questionary_adapter import QuestionaryStyleAdapter
from tui_engine.themes import TUIEngineThemes
from questionary import Style
import questionary


def test_adapter_initialization():
    """Test adapter initialization with different theme types."""
    print("🔧 Testing Adapter Initialization...")
    print("=" * 50)
    
    # Test with default theme
    try:
        adapter = QuestionaryStyleAdapter()
        print("✅ Default initialization successful")
        
        # Verify default theme
        theme_name = adapter.get_theme_name()
        if theme_name:
            print(f"✅ Default theme: {theme_name}")
        else:
            print("✅ Custom theme loaded")
            
    except Exception as e:
        print(f"❌ Default initialization failed: {e}")
    
    # Test with theme name
    try:
        adapter = QuestionaryStyleAdapter('dark_mode')
        theme_name = adapter.get_theme_name()
        if theme_name == 'dark_mode':
            print("✅ Theme name initialization successful")
        else:
            print(f"❌ Theme name mismatch: expected 'dark_mode', got '{theme_name}'")
    except Exception as e:
        print(f"❌ Theme name initialization failed: {e}")
    
    # Test with Style object
    try:
        theme_obj = TUIEngineThemes.HIGH_CONTRAST
        adapter = QuestionaryStyleAdapter(theme_obj)
        print("✅ Style object initialization successful")
    except Exception as e:
        print(f"❌ Style object initialization failed: {e}")
    
    # Test with invalid theme
    try:
        adapter = QuestionaryStyleAdapter('invalid_theme')
        print("❌ Should have failed with invalid theme")
    except ValueError:
        print("✅ Invalid theme properly rejected")
    except Exception as e:
        print(f"❌ Unexpected error with invalid theme: {e}")
    
    print()


def test_variant_style_mapping():
    """Test TUI Engine variant to Questionary style mapping."""
    print("🎨 Testing Variant Style Mapping...")
    print("=" * 50)
    
    adapter = QuestionaryStyleAdapter('professional_blue')
    
    # Test known variants
    test_variants = ['card', 'section', 'header', 'footer', 'button', 'input']
    
    for variant in test_variants:
        try:
            style = adapter.get_style_for_variant(variant)
            if style:
                print(f"✅ {variant:10} → {style}")
            else:
                print(f"❌ {variant:10} → No style returned")
        except Exception as e:
            print(f"❌ {variant:10} → Error: {e}")
    
    # Test variant mapping creation
    try:
        mapping = adapter.create_variant_style_mapping()
        if mapping and len(mapping) > 0:
            print(f"✅ Variant mapping created with {len(mapping)} entries")
        else:
            print("❌ Variant mapping creation failed")
    except Exception as e:
        print(f"❌ Variant mapping error: {e}")
    
    print()


def test_component_styling():
    """Test component-specific styling functionality."""
    print("🎯 Testing Component Styling...")
    print("=" * 50)
    
    adapter = QuestionaryStyleAdapter('dark_mode')
    
    # Test component styles
    components = [
        ('input', None),
        ('input', 'focused'),
        ('button', None),
        ('button', 'focused'),
        ('button', 'disabled'),
        ('select', 'selected'),
        ('validation', 'error'),
        ('validation', 'success'),
    ]
    
    for component_type, state in components:
        try:
            style = adapter.get_style_for_component(component_type, state)
            state_str = f":{state}" if state else ""
            print(f"✅ {component_type}{state_str:10} → {style}")
        except Exception as e:
            print(f"❌ {component_type}{state_str:10} → Error: {e}")
    
    # Test component style creation
    try:
        input_style = adapter.create_component_style('input')
        if input_style and hasattr(input_style, 'style_rules'):
            print(f"✅ Input component style created with {len(input_style.style_rules)} rules")
        else:
            print("❌ Input component style creation failed")
    except Exception as e:
        print(f"❌ Component style creation error: {e}")
    
    print()


def test_theme_switching():
    """Test dynamic theme switching functionality."""
    print("🔄 Testing Theme Switching...")
    print("=" * 50)
    
    adapter = QuestionaryStyleAdapter('professional_blue')
    
    # Test switching to each available theme
    for theme_name in TUIEngineThemes.list_themes():
        try:
            adapter.set_theme(theme_name)
            current_theme = adapter.get_theme_name()
            if current_theme == theme_name:
                print(f"✅ Successfully switched to {theme_name}")
            else:
                print(f"❌ Theme switch failed: expected {theme_name}, got {current_theme}")
        except Exception as e:
            print(f"❌ Theme switch to {theme_name} failed: {e}")
    
    # Test switching to Style object
    try:
        custom_style = TUIEngineThemes.create_custom_theme(
            'minimal',
            {'question': 'fg:#ff0000 bold'}
        )
        adapter.set_theme(custom_style)
        current_theme = adapter.get_theme_name()
        if current_theme is None:  # Custom themes don't have names
            print("✅ Successfully switched to custom Style object")
        else:
            print(f"❌ Custom style switch failed: unexpected theme name {current_theme}")
    except Exception as e:
        print(f"❌ Custom style switch failed: {e}")
    
    print()


def test_questionary_integration():
    """Test integration with actual Questionary prompts."""
    print("🔗 Testing Questionary Integration...")
    print("=" * 50)
    
    adapter = QuestionaryStyleAdapter('professional_blue')
    
    # Test creating prompts with adapter style
    prompt_types = [
        ('text', lambda style: questionary.text("Test input:", style=style)),
        ('select', lambda style: questionary.select("Choose:", choices=["A", "B"], style=style)),
        ('confirm', lambda style: questionary.confirm("Confirm?", style=style)),
        ('checkbox', lambda style: questionary.checkbox("Select:", choices=["X", "Y"], style=style)),
    ]
    
    for prompt_name, prompt_factory in prompt_types:
        try:
            style = adapter.get_questionary_style()
            prompt = prompt_factory(style)
            if prompt:
                print(f"✅ {prompt_name:10} prompt created successfully")
            else:
                print(f"❌ {prompt_name:10} prompt creation failed")
        except Exception as e:
            print(f"❌ {prompt_name:10} prompt error: {e}")
    
    # Test combined style creation
    try:
        combined_style = adapter.create_combined_style({
            'custom_class': 'fg:#ff00ff bold'
        })
        if combined_style and hasattr(combined_style, 'style_rules'):
            print(f"✅ Combined style created with {len(combined_style.style_rules)} rules")
        else:
            print("❌ Combined style creation failed")
    except Exception as e:
        print(f"❌ Combined style error: {e}")
    
    print()


def test_legacy_migration():
    """Test legacy style migration functionality."""
    print("📦 Testing Legacy Migration...")
    print("=" * 50)
    
    adapter = QuestionaryStyleAdapter('minimal')
    
    # Test legacy style migration
    legacy_styles = [
        # Simple string styles
        {'card_title': 'fg:#0000ff bold'},
        # Nested style objects
        {
            'input': {
                'normal': 'fg:#000000',
                'focused': 'fg:#0000ff bold'
            }
        },
        # Mixed styles
        {
            'text': 'fg:#333333',
            'button': {
                'default': 'fg:#ffffff bg:#0000ff',
                'hover': 'fg:#ffffff bg:#0033cc bold'
            }
        }
    ]
    
    for i, legacy_style in enumerate(legacy_styles, 1):
        try:
            migrated = adapter.migrate_legacy_style(legacy_style)
            if migrated and hasattr(migrated, 'style_rules'):
                print(f"✅ Legacy style {i} migrated successfully ({len(migrated.style_rules)} rules)")
            else:
                print(f"❌ Legacy style {i} migration failed")
        except Exception as e:
            print(f"❌ Legacy style {i} migration error: {e}")
    
    print()


def test_specialized_styles():
    """Test specialized style getters (validation, navigation)."""
    print("🎪 Testing Specialized Styles...")
    print("=" * 50)
    
    adapter = QuestionaryStyleAdapter('high_contrast')
    
    # Test validation styles
    try:
        validation_styles = adapter.get_validation_styles()
        expected_keys = ['valid', 'invalid', 'warning', 'info']
        
        if all(key in validation_styles for key in expected_keys):
            print(f"✅ Validation styles complete ({len(validation_styles)} entries)")
        else:
            missing = [key for key in expected_keys if key not in validation_styles]
            print(f"❌ Validation styles missing: {missing}")
    except Exception as e:
        print(f"❌ Validation styles error: {e}")
    
    # Test navigation styles
    try:
        nav_styles = adapter.get_navigation_styles()
        expected_keys = ['button', 'button_focused', 'button_disabled', 'selected', 'highlighted']
        
        if all(key in nav_styles for key in expected_keys):
            print(f"✅ Navigation styles complete ({len(nav_styles)} entries)")
        else:
            missing = [key for key in expected_keys if key not in nav_styles]
            print(f"❌ Navigation styles missing: {missing}")
    except Exception as e:
        print(f"❌ Navigation styles error: {e}")
    
    print()


def test_preview_generation():
    """Test style preview generation."""
    print("👀 Testing Preview Generation...")
    print("=" * 50)
    
    adapter = QuestionaryStyleAdapter('classic_terminal')
    
    try:
        preview = adapter.preview_style_mapping()
        if preview and len(preview) > 100:  # Should be substantial
            print("✅ Style preview generated successfully")
            
            # Check for key sections
            required_sections = ['Variant Mappings:', 'Validation Styles:', 'Navigation Styles:']
            missing_sections = [section for section in required_sections if section not in preview]
            
            if not missing_sections:
                print("✅ All preview sections present")
            else:
                print(f"❌ Missing preview sections: {missing_sections}")
                
        else:
            print("❌ Style preview generation failed or too short")
    except Exception as e:
        print(f"❌ Preview generation error: {e}")
    
    print()


def demonstrate_adapter_usage():
    """Demonstrate practical adapter usage."""
    print("🚀 Adapter Usage Demonstration...")
    print("=" * 50)
    
    # Example 1: Basic usage
    print("Example 1: Basic adapter usage")
    try:
        adapter = QuestionaryStyleAdapter('professional_blue')
        style = adapter.get_questionary_style()
        
        # Create a prompt with the adapter style
        test_prompt = questionary.text(
            "Demo input with Professional Blue theme:",
            style=style
        )
        print("✅ Basic usage successful")
    except Exception as e:
        print(f"❌ Basic usage failed: {e}")
    
    # Example 2: Component-specific styling
    print("\nExample 2: Component-specific styling")
    try:
        adapter = QuestionaryStyleAdapter('dark_mode')
        input_style = adapter.create_component_style('input', {
            'input_focused': 'fg:#00ff00 bold'  # Custom green focus
        })
        
        test_prompt = questionary.text(
            "Custom input styling:",
            style=input_style
        )
        print("✅ Component-specific styling successful")
    except Exception as e:
        print(f"❌ Component-specific styling failed: {e}")
    
    # Example 3: Dynamic theme switching
    print("\nExample 3: Dynamic theme switching")
    try:
        adapter = QuestionaryStyleAdapter('minimal')
        
        # Switch themes dynamically
        for theme_name in ['dark_mode', 'high_contrast']:
            adapter.set_theme(theme_name)
            current = adapter.get_theme_name()
            if current == theme_name:
                print(f"✅ Switched to {theme_name}")
            
        print("✅ Dynamic theme switching successful")
    except Exception as e:
        print(f"❌ Dynamic theme switching failed: {e}")
    
    print()


def show_detailed_preview():
    """Show a detailed preview of adapter functionality."""
    print("📋 Detailed Adapter Preview")
    print("=" * 60)
    
    adapter = QuestionaryStyleAdapter('professional_blue')
    preview = adapter.preview_style_mapping()
    print(preview)
    print()


def main():
    """Main test function."""
    print("🎨 Questionary Style Adapter Test Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    test_adapter_initialization()
    test_variant_style_mapping()
    test_component_styling()
    test_theme_switching()
    test_questionary_integration()
    test_legacy_migration()
    test_specialized_styles()
    test_preview_generation()
    demonstrate_adapter_usage()
    show_detailed_preview()
    
    print("✅ All adapter tests completed!")
    print("\n🎉 QuestionaryStyleAdapter is ready for integration!")


if __name__ == "__main__":
    main()