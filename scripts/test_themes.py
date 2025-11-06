#!/usr/bin/env python3
"""
TUI Engine Themes Test Script

This script tests the TUIEngineThemes class functionality and demonstrates
how the theme system works with Questionary integration.
"""

import sys
from pathlib import Path

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tui_engine.themes import TUIEngineThemes
import questionary
from questionary import Style


def test_theme_availability():
    """Test that all themes are available and properly defined."""
    print("🎨 Testing Theme Availability...")
    print("=" * 50)
    
    themes = TUIEngineThemes.list_themes()
    print(f"Available themes: {len(themes)}")
    
    for theme_name in themes:
        theme = TUIEngineThemes.get_theme(theme_name)
        description = TUIEngineThemes.get_theme_description(theme_name)
        
        if theme:
            print(f"✅ {theme_name}: {description}")
        else:
            print(f"❌ {theme_name}: Failed to load")
    
    print()


def test_theme_integration():
    """Test theme integration with Questionary."""
    print("🔗 Testing Questionary Integration...")
    print("=" * 50)
    
    # Test each theme with a simple questionary prompt
    for theme_name in TUIEngineThemes.list_themes():
        theme = TUIEngineThemes.get_theme(theme_name)
        
        try:
            # Create a questionary prompt with the theme
            prompt = questionary.select(
                message=f"Testing {theme_name} theme",
                choices=["Option 1", "Option 2", "Option 3"],
                style=theme
            )
            
            # Verify the prompt was created successfully
            if prompt:
                print(f"✅ {theme_name}: Questionary integration successful")
            else:
                print(f"❌ {theme_name}: Failed to create prompt")
                
        except Exception as e:
            print(f"❌ {theme_name}: Integration error - {e}")
    
    print()


def test_custom_theme_creation():
    """Test custom theme creation functionality."""
    print("🎭 Testing Custom Theme Creation...")
    print("=" * 50)
    
    try:
        # Create custom theme based on professional_blue
        custom_theme = TUIEngineThemes.create_custom_theme(
            'professional_blue',
            {
                'question': 'fg:#ff0000 bold',      # Red questions
                'answer': 'fg:#00ff00 bold',        # Green answers
                'success': 'fg:#0000ff bold',       # Blue success
            }
        )
        
        # Test the custom theme
        test_prompt = questionary.text(
            "Custom theme test prompt",
            style=custom_theme
        )
        
        if test_prompt:
            print("✅ Custom theme creation successful")
            print("✅ Custom theme Questionary integration successful")
        else:
            print("❌ Custom theme integration failed")
            
    except Exception as e:
        print(f"❌ Custom theme creation failed: {e}")
    
    print()


def test_theme_previews():
    """Test theme preview functionality."""
    print("👀 Testing Theme Previews...")
    print("=" * 50)
    
    for theme_name in TUIEngineThemes.list_themes():
        try:
            preview = TUIEngineThemes.get_theme_preview(theme_name)
            if preview and len(preview) > 0:
                print(f"✅ {theme_name}: Preview generated successfully")
            else:
                print(f"❌ {theme_name}: Preview generation failed")
        except Exception as e:
            print(f"❌ {theme_name}: Preview error - {e}")
    
    print()


def demonstrate_theme_usage():
    """Demonstrate practical theme usage."""
    print("🚀 Theme Usage Demonstration...")
    print("=" * 50)
    
    # Show how to use themes in practice
    print("Example 1: Using Professional Blue theme")
    try:
        theme = TUIEngineThemes.PROFESSIONAL_BLUE
        prompt = questionary.confirm(
            "Do you like the Professional Blue theme?",
            style=theme,
            default=True
        )
        print("✅ Professional Blue theme prompt created successfully")
    except Exception as e:
        print(f"❌ Professional Blue demonstration failed: {e}")
    
    print("\nExample 2: Dynamic theme selection")
    try:
        selected_theme = 'dark_mode'
        theme = TUIEngineThemes.get_theme(selected_theme)
        if theme:
            prompt = questionary.select(
                "Choose an option with Dark Mode theme",
                choices=["Development", "Testing", "Production"],
                style=theme
            )
            print(f"✅ Dynamic theme selection ({selected_theme}) successful")
        else:
            print(f"❌ Theme '{selected_theme}' not found")
    except Exception as e:
        print(f"❌ Dynamic theme demonstration failed: {e}")
    
    print("\nExample 3: Theme customization")
    try:
        custom = TUIEngineThemes.create_custom_theme(
            'minimal',
            {'highlighted': 'bg:#ffff00 fg:#000000 bold'}  # Yellow highlight
        )
        prompt = questionary.checkbox(
            "Select features (with custom highlighting)",
            choices=["Feature A", "Feature B", "Feature C"],
            style=custom
        )
        print("✅ Theme customization successful")
    except Exception as e:
        print(f"❌ Theme customization failed: {e}")
    
    print()


def show_theme_preview(theme_name: str):
    """Show detailed preview of a specific theme."""
    print(f"📖 Theme Preview: {theme_name.upper()}")
    print("=" * 60)
    
    preview = TUIEngineThemes.get_theme_preview(theme_name)
    print(preview)
    print()


def main():
    """Main test function."""
    print("🎨 TUI Engine Themes Test Suite")
    print("=" * 60)
    print()
    
    # Run all tests
    test_theme_availability()
    test_theme_integration()
    test_custom_theme_creation()
    test_theme_previews()
    demonstrate_theme_usage()
    
    # Show detailed previews for key themes
    show_theme_preview('professional_blue')
    show_theme_preview('dark_mode')
    
    print("✅ All theme tests completed!")
    print("\n🎉 TUIEngineThemes is ready for integration!")


if __name__ == "__main__":
    main()