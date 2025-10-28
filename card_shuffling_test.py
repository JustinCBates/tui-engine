#!/usr/bin/env python3
"""
Card Shuffling Test Demo

This module demonstrates the card navigation and visibility system of the TUI Engine.
It creates multiple cards with different themes and allows users to navigate between them
using keyboard commands or automated animation.

Features demonstrated:
- Card creation and management
- Show/hide card functionality  
- Interactive navigation (next/previous/direct jump)
- Status message updates
- Incremental page refresh system
- Clean terminal-based UI

Usage:
    python card_shuffling_test.py

Commands:
    n - Next card
    p - Previous card  
    1-5 - Jump to specific card
    a - Show all cards
    q - Quit demo
"""

import time
from src.questionary_extended.core.page_base import PageBase


class CardShufflingDemo:
    """
    Interactive card shuffling demonstration.
    
    Features:
    - 5 different themed cards
    - Smooth incremental refresh
    - Keyboard navigation (n/p/1-5/a/q)
    - Clean visual feedback
    """
    
    def __init__(self):
        """Initialize the card shuffling demo."""
        self.page = PageBase("🎴 Card Shuffling Navigation")
        self.current_card = 0
        self.status_message = ""
        
        # Setup instructions FIRST (so they render before cards)
        self._setup_instructions()
        
        # Then setup cards (so they render in body after header)
        self._setup_cards()
        
        # Enable safe incremental refresh for smooth transitions
        self.page.enable_safe_incremental()
    
    def _setup_instructions(self):
        """Setup navigation instructions."""
        instructions = [
            "Navigation: ← → (arrow keys) or A/D to move between cards",
            "Space: Toggle current card visibility", 
            "T: Run animation test (5 cards transition)",
            "Q: Quit demo",
            "",
        ]
        for instruction in instructions:
            self.page.text_display(instruction)
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update the status message.
        
        Uses the page's built-in text_status method for clean display management.
        """
        self.status_message = message
        # Use the page's built-in status method
        self.page.text_status(message, status_type)
    
    def _setup_cards(self):
        """Create the 5 demo cards with bordered style."""
        
        self.cards = [
            self.page.card("🏠 Personal Information", style="bordered"),
            self.page.card("💼 Professional Details", style="bordered"), 
            self.page.card("🎓 Education Level", style="bordered"),
            self.page.card("🌟 Preferences", style="bordered"),
            self.page.card("🎯 Goals & Targets", style="bordered")
        ]
    
    def show_only_current_card(self):
        """Show only the current card, hide all others."""
        for i, card in enumerate(self.cards):
            if i == self.current_card:
                card.show()
            else:
                card.hide()
        self.page.refresh()
    
    def show_all_cards(self):
        """Show all cards."""
        for card in self.cards:
            card.show()
        self.page.refresh()
    
    def run_interactive_demo(self):
        """Run the interactive card shuffling demo."""
        
        # Initial display - show only first card
        self.show_only_current_card()
        
        while True:
            # Update current status (replaces previous status)
            # self.update_status(f"Currently viewing Card {self.current_card + 1}/5: {self.cards[self.current_card].title}", "info")
            self.page.refresh()
            
            # Use questionary for clean input
            from questionary import text
            try:
                choice = text("📥 Your choice: ").ask()
                if choice is None:  # User pressed Ctrl+C
                    break
                choice = choice.strip().lower()
                
                if choice == 'n':
                    self.current_card = (self.current_card + 1) % len(self.cards)
                    self.show_only_current_card()
                    
                elif choice == 'p':
                    self.current_card = (self.current_card - 1) % len(self.cards)
                    self.show_only_current_card()
                    
                elif choice in ['1', '2', '3', '4', '5']:
                    new_card = int(choice) - 1
                    if 0 <= new_card < len(self.cards):
                        self.current_card = new_card
                        self.show_only_current_card()
                        
                elif choice == 'a':
                    self.show_all_cards()
                    
                elif choice == 'q':
                    self.update_status("Demo completed!", "success")
                    self.page.refresh()
                    break
                    
                else:
                    self.update_status("Invalid choice. Use: n/p/1-5/a/q", "error")
                    self.page.refresh()
                    self.page.refresh()
                    
            except KeyboardInterrupt:
                self.page.text_status("Demo interrupted. Goodbye!", "info")
                self.page.refresh()
                break
            except Exception as e:
                self.page.text_status(f"Error: {e}", "error")
                self.page.refresh()
    
    def run_animation_demo(self):
        """Run an automated animation demo."""
        import os
        
        # Show intro message
        print("=" * 60)
        print("📄 [PAGE] 🎴 Card Shuffling Navigation")
        print("=" * 60)
        print("🎬 Animation Demo: Watch the smooth card transitions...")
        time.sleep(2)
        
        # Cycle through cards automatically with clean screen clears
        for cycle in range(2):
            for i in range(len(self.cards)):
                # Clear screen and show header
                os.system('clear' if os.name == 'posix' else 'cls')
                print("=" * 60)
                print("📄 [PAGE] 🎴 Card Shuffling Navigation")
                print("=" * 60)
                
                # Manually render just the current card
                card = self.cards[i]
                card_lines = card.get_render_lines()
                for line in card_lines:
                    print(line)
                
                # Add caption showing current card
                print(f"\nℹ️ 🎬 Animation: Showing card {i+1}/5 (cycle {cycle+1}/2)")
                
                time.sleep(1.2)
        
        # End with clean final state
        os.system('clear' if os.name == 'posix' else 'cls')
        print("=" * 60)
        print("📄 [PAGE] 🎴 Card Shuffling Navigation")
        print("=" * 60)
        print("✅ 🎬 Animation complete! Cards can be shown/hidden dynamically.")


def clear_content_area():
    """Clear screen and re-render header."""
    import os
    os.system('clear' if os.name == 'posix' else 'cls')
    print("=" * 60)
    print("📄 [PAGE] 🧪 Quick Test")
    print("=" * 60)


def run_quick_test():
    """Quick test to verify basic functionality."""
    
    page = PageBase("🧪 Quick Test")
    # page.enable_safe_incremental()  # Disabled due to issues with dynamic content changes
    
    card1 = page.card("🔴 Test Card 1")
    card2 = page.card("🔵 Test Card 2")
    
    # Test 1: Both cards visible
    page.text_status("Test 1/4: Both cards visible", "info")
    page.refresh()
    input("\n🔑 Press Enter to continue to Test 2...")
    
    # Clear and show Test 2
    clear_content_area()
    card1.hide()
    page.text_status("Test 2/4: Hiding red card...", "info")
    page.refresh()
    input("\n🔑 Press Enter to continue to Test 3...")
    
    # Clear and show Test 3
    clear_content_area()
    card2.hide()
    page.text_status("Test 3/4: Hiding blue card (both hidden)...", "info")
    page.refresh()
    input("\n🔑 Press Enter to continue to Test 4...")
    
    # Clear and show Test 4
    clear_content_area()
    card1.show()
    page.text_status("Test 4/4: Showing red card...", "info")
    page.refresh()
    input("\n🔑 Press Enter to complete the test...")
    
    # Clear and show completion
    clear_content_area()
    
    # Final completion message
    page.text_status("Quick test completed!", "success")
    page.text_display("🎯 Did you see smooth card visibility changes?")
    # No refresh needed - the text_status already updates the display


def run_main_menu():
    """Main menu for selecting which demo to run."""
    import os
    from questionary import select, confirm
    
    while True:
        # Clear screen for clean menu presentation
        os.system('clear' if os.name == 'posix' else 'cls')
        
        # Create menu page
        menu_page = PageBase("🎮 TUI Engine Demo Menu")
        menu_page.text_display("Welcome to the TUI Engine demonstration!")
        menu_page.text_display("Choose which demo you'd like to run:")
        menu_page.text_display("")
        menu_page.refresh()
        
        # Show menu options
        choice = select(
            "📋 Select a demo:",
            choices=[
                "🧪 Quick Test - Basic visibility system test",
                "🎴 Card Shuffling - Interactive navigation demo", 
                "🎬 Animation Demo - Automated card transitions",
                "🔄 Run All Demos - Execute all demos in sequence",
                "❌ Exit"
            ]
        ).ask()
        
        if choice is None:  # User pressed Ctrl+C
            break
            
        # Clear screen before running selected demo
        os.system('clear' if os.name == 'posix' else 'cls')
        
        if "Quick Test" in choice:
            run_quick_test()
            input("\n✨ Press Enter to return to menu...")
            
        elif "Card Shuffling" in choice:
            demo = CardShufflingDemo()
            demo.run_interactive_demo()
            input("\n✨ Press Enter to return to menu...")
            
        elif "Animation Demo" in choice:
            demo = CardShufflingDemo() 
            demo.run_animation_demo()
            input("\n✨ Press Enter to return to menu...")
            
        elif "Run All Demos" in choice:
            # Quick test
            run_quick_test()
            input("\n🎬 Press Enter to continue to Card Shuffling Demo...")
            
            # Clear screen and run card shuffling
            os.system('clear' if os.name == 'posix' else 'cls')
            demo = CardShufflingDemo()
            demo.run_interactive_demo()
            
            # Ask about animation demo
            if confirm("\n🎞️ Run animation demo?").ask():
                os.system('clear' if os.name == 'posix' else 'cls')
                # Create a NEW instance for animation demo
                animation_demo = CardShufflingDemo()
                animation_demo.run_animation_demo()
            
            input("\n✨ All demos completed! Press Enter to return to menu...")
            
        elif "Exit" in choice:
            print("👋 Thank you for trying the TUI Engine demos!")
            break


if __name__ == "__main__":
    import sys
    
    try:
        # Check for command line arguments
        if len(sys.argv) > 1:
            arg = sys.argv[1].lower()
            if arg == "interactive":
                demo = CardShufflingDemo()
                demo.run_interactive_demo()
            elif arg == "animation":
                demo = CardShufflingDemo()
                demo.run_animation_demo()
            elif arg == "test":
                run_quick_test()
            else:
                print(f"Unknown argument: {arg}")
                print("Available options: interactive, animation, test")
        else:
            # Run main menu if no arguments
            run_main_menu()
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()