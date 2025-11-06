#!/usr/bin/env python3
"""
TUI Engine Themes Integration Demo

This demo shows how to use the new TUIEngineThemes system with existing
TUI Engine components and how it integrates with Questionary styling.
"""

import questionary
from questionary import Style
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tui_engine.themes import TUIEngineThemes


def demo_theme_selection():
    """Demo: Let user select a theme and see it applied."""
    print("🎨 TUI Engine Themes Integration Demo")
    print("=" * 50)
    
    # Show available themes
    themes = TUIEngineThemes.list_themes()
    theme_choices = []
    
    for theme_name in themes:
        description = TUIEngineThemes.get_theme_description(theme_name)
        theme_choices.append({
            'name': f"{theme_name.replace('_', ' ').title()} - {description}",
            'value': theme_name
        })
    
    # Use default styling for theme selection
    selected_theme = questionary.select(
        "Choose a theme to demonstrate:",
        choices=theme_choices
    ).ask()
    
    if not selected_theme:
        print("Demo cancelled.")
        return
    
    print(f"\n🎯 Demonstrating: {selected_theme.replace('_', ' ').title()}")
    print("=" * 50)
    
    # Get the selected theme
    theme = TUIEngineThemes.get_theme(selected_theme)
    
    # Demo different prompt types with the selected theme
    demo_prompts_with_theme(theme, selected_theme)


def demo_prompts_with_theme(theme: Style, theme_name: str):
    """Demonstrate various prompt types with the selected theme."""
    
    print(f"Using {theme_name.replace('_', ' ').title()} theme for all prompts:\n")
    
    # Text input demo
    print("📝 Text Input Example:")
    name = questionary.text(
        "What's your name?",
        style=theme,
        validate=lambda x: len(x) > 0 or "Name cannot be empty"
    ).ask()
    
    if name:
        print(f"✓ Hello, {name}!\n")
    
    # Select demo
    print("📋 Select Example:")
    choice = questionary.select(
        "Choose your favorite development environment:",
        choices=[
            "VS Code",
            "PyCharm", 
            "Vim/Neovim",
            "Sublime Text",
            "Other"
        ],
        style=theme
    ).ask()
    
    if choice:
        print(f"✓ Great choice: {choice}!\n")
    
    # Checkbox demo
    print("☑️  Checkbox Example:")
    features = questionary.checkbox(
        "Select TUI Engine features you're interested in:",
        choices=[
            "Professional Themes",
            "Validation System", 
            "Custom Components",
            "Questionary Integration",
            "Performance Optimization"
        ],
        style=theme
    ).ask()
    
    if features:
        print(f"✓ Selected features: {', '.join(features)}\n")
    
    # Confirm demo
    print("❓ Confirmation Example:")
    satisfied = questionary.confirm(
        f"Are you satisfied with the {theme_name.replace('_', ' ').title()} theme?",
        style=theme,
        default=True
    ).ask()
    
    if satisfied is not None:
        result = "Yes" if satisfied else "No"
        print(f"✓ Theme satisfaction: {result}\n")


def demo_custom_theme_creation():
    """Demo: Create and use a custom theme."""
    print("🎭 Custom Theme Creation Demo")
    print("=" * 40)
    
    # Let user choose base theme
    base_theme = questionary.select(
        "Choose a base theme for customization:",
        choices=TUIEngineThemes.list_themes()
    ).ask()
    
    if not base_theme:
        return
    
    print(f"\n🎨 Creating custom theme based on {base_theme}...")
    
    # Create custom theme with user's favorite color
    color = questionary.text(
        "Enter your favorite color (hex format, e.g., #ff0000):",
        validate=lambda x: x.startswith('#') and len(x) == 7 or "Enter hex color like #ff0000"
    ).ask()
    
    if not color:
        return
    
    # Create custom theme
    custom_theme = TUIEngineThemes.create_custom_theme(
        base_theme,
        {
            'question': f'fg:{color} bold',
            'highlighted': f'bg:{color} fg:#ffffff bold',
            'selected': f'fg:{color} bold'
        }
    )
    
    print(f"\n✨ Custom theme created with {color} accents!")
    print("Testing custom theme...")
    
    # Test the custom theme
    test_custom = questionary.confirm(
        "Does this custom theme look good?",
        style=custom_theme
    ).ask()
    
    if test_custom is not None:
        result = "Excellent!" if test_custom else "We can adjust it further."
        print(f"✓ Custom theme feedback: {result}")


def demo_theme_comparison():
    """Demo: Compare themes side by side."""
    print("\n🔄 Theme Comparison Demo")
    print("=" * 30)
    
    themes_to_compare = ['professional_blue', 'dark_mode', 'high_contrast']
    
    for theme_name in themes_to_compare:
        theme = TUIEngineThemes.get_theme(theme_name)
        print(f"\n--- {theme_name.replace('_', ' ').title()} Theme ---")
        
        choice = questionary.select(
            "How does this theme look?",
            choices=["Excellent", "Good", "Fair", "Poor"],
            style=theme
        ).ask()
        
        if choice:
            print(f"Rating: {choice}")


def show_theme_documentation():
    """Show theme documentation and usage examples."""
    print("\n📚 Theme System Documentation")
    print("=" * 40)
    
    print("""
Theme Usage Examples:

1. Basic Usage:
   from tui_engine.themes import TUIEngineThemes
   theme = TUIEngineThemes.PROFESSIONAL_BLUE
   prompt = questionary.text("Question", style=theme)

2. Dynamic Theme Selection:
   theme_name = 'dark_mode'
   theme = TUIEngineThemes.get_theme(theme_name)
   prompt = questionary.select("Choose", choices=options, style=theme)

3. Custom Theme Creation:
   custom = TUIEngineThemes.create_custom_theme(
       'professional_blue',
       {'question': 'fg:#ff0000 bold'}
   )

4. List Available Themes:
   themes = TUIEngineThemes.list_themes()
   for theme_name in themes:
       description = TUIEngineThemes.get_theme_description(theme_name)
       print(f"{theme_name}: {description}")
    """)


def main():
    """Main demo function."""
    try:
        # Run the main theme demo
        demo_theme_selection()
        
        # Ask if user wants to see more demos
        more_demos = questionary.confirm(
            "Would you like to see additional theme demos?",
            default=True
        ).ask()
        
        if more_demos:
            demo_custom_theme_creation()
            demo_theme_comparison()
            show_theme_documentation()
        
        print("\n🎉 Theme integration demo completed!")
        print("TUI Engine themes are ready for use in your applications.")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Thanks for trying TUI Engine themes!")
    except Exception as e:
        print(f"\nDemo error: {e}")


if __name__ == "__main__":
    main()