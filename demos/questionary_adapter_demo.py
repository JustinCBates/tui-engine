#!/usr/bin/env python3
"""
Questionary Style Adapter Integration Demo

This demo shows how the QuestionaryStyleAdapter seamlessly bridges
TUI Engine's existing styling system with Questionary's professional themes.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tui_engine.questionary_adapter import QuestionaryStyleAdapter
from tui_engine.themes import TUIEngineThemes
import questionary


def demo_basic_integration():
    """Demonstrate basic adapter integration."""
    print("🎨 Basic Questionary Style Adapter Integration")
    print("=" * 60)
    
    # Create adapter with Professional Blue theme
    adapter = QuestionaryStyleAdapter('professional_blue')
    
    print(f"Current theme: {adapter.get_theme_name()}")
    print("Creating prompts with enhanced TUI Engine styling...\n")
    
    # Create prompts using the adapter's Questionary style
    style = adapter.get_questionary_style()
    
    # Text input with TUI Engine variant styling
    name = questionary.text(
        "Enter your name:",
        style=style,
        validate=lambda x: len(x) > 0 or "Name cannot be empty"
    ).ask()
    
    if name:
        print(f"✓ Welcome, {name}!\n")
    
    # Select with enhanced styling
    environment = questionary.select(
        "Choose development environment:",
        choices=[
            "Production",
            "Staging", 
            "Development",
            "Testing"
        ],
        style=style
    ).ask()
    
    if environment:
        print(f"✓ Selected environment: {environment}\n")
    
    # Checkbox with TUI Engine theming
    features = questionary.checkbox(
        "Select TUI Engine features to use:",
        choices=[
            "Professional Themes",
            "Style Adapter",
            "Validation Integration",
            "Custom Components",
            "Legacy Migration"
        ],
        style=style
    ).ask()
    
    if features:
        print(f"✓ Selected features: {', '.join(features)}\n")


def demo_component_specific_styling():
    """Demonstrate component-specific styling."""
    print("🎯 Component-Specific Styling Demo")
    print("=" * 45)
    
    adapter = QuestionaryStyleAdapter('dark_mode')
    
    # Create input-specific style
    input_style = adapter.create_component_style('input', {
        'input_focused': 'fg:#00ff00 bold',  # Custom green focus
        'placeholder': 'fg:#666666 italic'   # Custom placeholder
    })
    
    print("Using custom input styling (green focus)...")
    user_input = questionary.text(
        "Custom styled input:",
        style=input_style
    ).ask()
    
    # Create button-specific style
    button_style = adapter.create_component_style('button', {
        'button': 'fg:#ffffff bg:#ff6600',
        'button_focused': 'fg:#ffffff bg:#cc5500 bold'
    })
    
    print("\nUsing custom button styling (orange buttons)...")
    confirm = questionary.confirm(
        "Do you like the custom styling?",
        style=button_style
    ).ask()
    
    if confirm is not None:
        result = "Great!" if confirm else "We can adjust it."
        print(f"✓ {result}\n")


def demo_theme_switching():
    """Demonstrate dynamic theme switching."""
    print("🔄 Dynamic Theme Switching Demo")
    print("=" * 40)
    
    adapter = QuestionaryStyleAdapter('minimal')
    
    themes_to_try = ['professional_blue', 'dark_mode', 'high_contrast']
    
    for theme_name in themes_to_try:
        print(f"\nSwitching to {theme_name.replace('_', ' ').title()} theme...")
        adapter.set_theme(theme_name)
        
        style = adapter.get_questionary_style()
        
        rating = questionary.select(
            f"How does the {theme_name.replace('_', ' ').title()} theme look?",
            choices=["Excellent", "Good", "Fair", "Poor"],
            style=style
        ).ask()
        
        if rating:
            print(f"✓ Theme rating: {rating}")


def demo_legacy_migration():
    """Demonstrate legacy style migration."""
    print("📦 Legacy Style Migration Demo")
    print("=" * 35)
    
    adapter = QuestionaryStyleAdapter('professional_blue')
    
    # Simulate legacy TUI Engine styles
    legacy_styles = {
        'card_title': 'fg:#0066cc bold',
        'input_text': 'fg:#333333',
        'button_primary': 'fg:#ffffff bg:#0066cc',
        'error_text': 'fg:#cc0000 bold'
    }
    
    print("Migrating legacy styles to Questionary format...")
    migrated_style = adapter.migrate_legacy_style(legacy_styles)
    
    # Test migrated style
    test_input = questionary.text(
        "Testing migrated legacy styles:",
        style=migrated_style
    ).ask()
    
    print("✓ Legacy styles successfully migrated and applied!\n")


def demo_validation_integration():
    """Demonstrate validation styling integration."""
    print("✅ Validation Styling Integration Demo") 
    print("=" * 45)
    
    adapter = QuestionaryStyleAdapter('high_contrast')
    
    # Get validation-specific styles
    validation_styles = adapter.get_validation_styles()
    print("Available validation styles:")
    for state, style in validation_styles.items():
        print(f"  {state:10} → {style}")
    
    # Create style with enhanced validation
    validation_style = adapter.create_component_style('validation')
    
    # Demo validation with custom styling
    email = questionary.text(
        "Enter your email address:",
        style=validation_style,
        validate=lambda x: '@' in x or "Please enter a valid email address"
    ).ask()
    
    if email:
        print(f"✓ Valid email: {email}\n")


def demo_style_preview():
    """Demonstrate style preview functionality."""
    print("👀 Style Preview Demo")
    print("=" * 25)
    
    adapter = QuestionaryStyleAdapter('classic_terminal')
    
    # Show complete style mapping
    preview = adapter.preview_style_mapping()
    print(preview)
    print()


def demo_practical_application():
    """Demonstrate a practical application using the adapter."""
    print("🚀 Practical Application Demo")
    print("=" * 35)
    
    print("Building a deployment configuration interface...")
    
    # Initialize adapter
    adapter = QuestionaryStyleAdapter('professional_blue')
    style = adapter.get_questionary_style()
    
    # Application configuration
    app_name = questionary.text(
        "Application name:",
        style=style,
        validate=lambda x: len(x) > 0 or "Application name required"
    ).ask()
    
    if not app_name:
        return
    
    # Environment selection
    environment = questionary.select(
        "Target environment:",
        choices=[
            {"name": "🏭 Production", "value": "prod"},
            {"name": "🔧 Staging", "value": "staging"},
            {"name": "💻 Development", "value": "dev"}
        ],
        style=style
    ).ask()
    
    # Features selection
    features = questionary.checkbox(
        "Enable features:",
        choices=[
            {"name": "🔒 Security scanning", "value": "security"},
            {"name": "📊 Monitoring", "value": "monitoring"},
            {"name": "🔄 Auto-scaling", "value": "autoscale"},
            {"name": "💾 Database backup", "value": "backup"}
        ],
        style=style
    ).ask()
    
    # Confirmation
    confirm = questionary.confirm(
        f"Deploy '{app_name}' to {environment} with {len(features)} features?",
        style=style,
        default=True
    ).ask()
    
    if confirm:
        print(f"\n✅ Deployment configured successfully!")
        print(f"   App: {app_name}")
        print(f"   Environment: {environment}")
        print(f"   Features: {', '.join(features) if features else 'None'}")
    else:
        print("\n❌ Deployment cancelled.")


def main():
    """Main demo function."""
    try:
        print("🎨 Questionary Style Adapter Integration Demos")
        print("=" * 70)
        print()
        
        # Run demos
        demo_basic_integration()
        print()
        
        demo_component_specific_styling()
        print()
        
        demo_theme_switching()
        print()
        
        demo_legacy_migration()
        print()
        
        demo_validation_integration()
        print()
        
        demo_style_preview()
        print()
        
        # Ask if user wants to see practical demo
        practical_demo = questionary.confirm(
            "Would you like to see a practical application demo?",
            default=True
        ).ask()
        
        if practical_demo:
            print()
            demo_practical_application()
        
        print("\n🎉 Style adapter integration demos completed!")
        print("The QuestionaryStyleAdapter is ready for production use.")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Thanks for trying the Style Adapter!")
    except Exception as e:
        print(f"\nDemo error: {e}")


if __name__ == "__main__":
    main()