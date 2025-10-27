#!/usr/bin/env python3
"""
Card Shuffling Navigation Demo

The definitive test for card-based navigation with incremental refresh.
Incorporates all latest fixes:
- [PAGE] and [CARD] header labels for clarity
- Safe incremental refresh mode for smooth transitions
- Universal visibility system
- Clean card navigation controls

Use this demo to test and refine the card shuffling functionality.
"""

import os
import sys
import time

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

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
        self.page = PageBase("🎴 Card Shuffling Navigation")
        self.current_card = 0
        self.cards = []
        self.status_component = None  # Track current status component
        self._setup_cards()
        
        # Enable safe incremental refresh for smooth transitions
        self.page.enable_safe_incremental()
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update the status message, replacing any existing status."""
        # Remove existing status component if it exists
        if self.status_component is not None:
            try:
                self.page.components.remove(self.status_component)
            except ValueError:
                pass  # Component already removed
        
        # Create and add new status component
        from src.questionary_extended.core.component_wrappers import text_status
        self.status_component = text_status(message, status_type=status_type)
        self.page.components.append(self.status_component)
    
    def _setup_cards(self):
        """Create the 5 demo cards."""
        
        self.cards = [
            self.page.card("🏠 Personal Information"),
            self.page.card("💼 Professional Details"), 
            self.page.card("🎓 Education Level"),
            self.page.card("🌟 Preferences"),
            self.page.card("🎯 Goals & Targets")
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
        
        # Add instructions using page display components instead of print
        self.page.text_display("🎴 Card Shuffling Navigation Demo")
        self.page.text_display("=" * 50)
        self.page.text_status("Testing: Incremental refresh with [PAGE]/[CARD] labels", "info")
        self.page.text_display("Commands: [n]ext | [p]revious | [1-5] jump | [a]ll | [q]uit")
        self.page.text_display("=" * 50)
        
        # Initial display - show only first card
        self.show_only_current_card()
        
        while True:
            # Update current status (replaces previous status)
            self.update_status(f"Currently viewing Card {self.current_card + 1}/5: {self.cards[self.current_card].title}", "info")
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
        
        # Add animation intro using page display components
        self.page.text_display("🎬 Automated Animation Demo")
        self.page.text_display("=" * 30)
        self.update_status("Watch the smooth card transitions...", "info")
        self.page.text_display("=" * 30)
        self.page.refresh()
        
        # Cycle through cards automatically
        for cycle in range(2):
            for i in range(len(self.cards)):
                self.current_card = i
                self.update_status(f"Showing card {i+1}/5 (cycle {cycle+1}/2)", "info")
                self.show_only_current_card()
                time.sleep(1.2)
        
        # Show all cards at the end
        self.show_all_cards()
        self.update_status("Animation complete!", "success")
        self.page.refresh()
        time.sleep(1)


def run_quick_test():
    """Quick test to verify basic functionality."""
    
    page = PageBase("🧪 Quick Test")
    page.enable_safe_incremental()
    
    # Add status components instead of print statements
    page.text_status("Testing visibility system with 4 scenarios...", "info")
    
    card1 = page.card("🔴 Test Card 1")
    card2 = page.card("🔵 Test Card 2")
    
    # Test 1: Both cards visible
    page.refresh()
    time.sleep(1.5)
    
    # Test 2: Hide card 1
    card1.hide()
    page.refresh()
    time.sleep(1.5)
    
    # Test 3: Hide card 2, show card 1
    card2.hide()
    card1.show()
    page.refresh()
    time.sleep(1.5)
    
    # Test 4: Show both cards
    card2.show()
    page.refresh()
    time.sleep(1.5)
    
    # Add completion status
    page.text_status("Quick test completed!", "success")
    page.text_display("🎯 Did you see smooth card visibility changes?")
    page.refresh()


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
                demo.run_animation_demo()
            
            input("\n✨ All demos completed! Press Enter to return to menu...")
            
        elif "Exit" in choice:
            print("👋 Thank you for trying the TUI Engine demos!")
            break


if __name__ == "__main__":
    try:
        run_main_menu()
        
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Demo error: {e}")
        import traceback
        traceback.print_exc()