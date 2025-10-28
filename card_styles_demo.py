#!/usr/bin/env python3
"""
Card Styles Demonstration
Shows all available card styling options.
"""

import sys
import os
import time

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.questionary_extended.core.page_base import PageBase


def demonstrate_card_styles():
    """Show all available card styles."""
    
    page = PageBase("🎨 Card Styles Showcase")
    
    # Add title and description
    page.text_status("Demonstrating all available card styling options", "info")
    
    # Create cards with different styles
    styles = ["minimal", "bordered", "highlighted"]
    
    for style in styles:
        card = page.card(f"🎴 {style.title()} Style Card", style=style)
        card.text_status(f"This is a {style} style card.", "info")
        card.text_status("It demonstrates the visual appearance and formatting.", "info")
        card.text_status("You can use this style by setting style='{}'".format(style), "info")
    
    # Show the page
    page.refresh()
    
    # Keep display for a moment
    print("\n" + "="*60)
    print("✨ Card styles demonstration complete!")
    print("Available styles: minimal, bordered, highlighted")
    print("="*60)


if __name__ == "__main__":
    try:
        demonstrate_card_styles()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()