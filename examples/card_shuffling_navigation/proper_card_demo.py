#!/usr/bin/env python3
"""
Proper Card Shuffling Demo using TUI Engine Architecture

This demo showcases the correct TUI engine architecture:
- Page with Cards containing Assemblies
- Universal visibility system
- Page.refresh() for centralized screen management
- State-driven navigation with Page Up/Down keys
"""

import os
import sys
import termios
import tty

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from questionary_extended.page_runtime import Page


class ProperCardShufflingDemo:
    """
    Card shuffling demo using proper TUI engine architecture.
    
    Architecture:
    - Page contains 5 Cards
    - Each Card contains one Assembly with descriptive text
    - Navigation changes Card visibility
    - Page.refresh() handles all screen management
    """
    
    def __init__(self):
        self.page = self._create_page()
        self.current_card_index = 0
        self.cards = []
        self._collect_cards()
    
    def _create_page(self) -> Page:
        """Create the page with proper card/assembly structure."""
        page = Page("🎴 Card Shuffling Navigation")
        
        # Card 1: Personal Information
        card1 = page.card("🏠 Personal Information", style="highlighted")
        assembly1 = card1.assembly("personal")
        assembly1.text("age", message="What is your age?")
        
        # Card 2: Professional Details
        card2 = page.card("💼 Professional Details", style="highlighted")
        assembly2 = card2.assembly("professional")
        assembly2.text("experience_years", message="How many years of experience do you have?")
        
        # Card 3: Education Level
        card3 = page.card("🎓 Education Level", style="highlighted")
        assembly3 = card3.assembly("education")
        assembly3.text("degrees_count", message="How many degrees do you hold?")
        
        # Card 4: Preferences
        card4 = page.card("🌟 Preferences", style="highlighted")
        assembly4 = card4.assembly("preferences")
        assembly4.text("interest_rating", message="Rate your interest level (1-10):")
        
        # Card 5: Goals & Targets
        card5 = page.card("🎯 Goals & Targets", style="highlighted")
        assembly5 = card5.assembly("goals")
        assembly5.text("goals_count", message="How many goals do you want to achieve this year?")
        
        return page
    
    def _collect_cards(self):
        """Collect all cards from the page for navigation."""
        self.cards = [comp for comp in self.page.components 
                     if hasattr(comp, 'title') and hasattr(comp, 'components')]
    
    def _update_card_visibility(self):
        """Update card visibility based on current_card_index."""
        for i, card in enumerate(self.cards):
            if i == self.current_card_index:
                card.show()
            else:
                card.hide()
    
    def _display_navigation_info(self):
        """Display current navigation information."""
        print(f"\n🎯 Currently viewing: Card {self.current_card_index + 1} of {len(self.cards)}")
        print(f"🎴 {self.cards[self.current_card_index].title}")
        print("💡 Page Up/Down to navigate, 'r' to run current card, 'q' to quit")
    
    def get_key(self):
        """Get a single keypress from the terminal."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            ch = sys.stdin.read(1)
            
            # Handle escape sequences (Page Up/Down)
            if ch == '\x1b':  # ESC sequence
                ch += sys.stdin.read(2)
                if len(ch) == 3:
                    try:
                        import select
                        if select.select([sys.stdin], [], [], 0.01)[0]:
                            ch += sys.stdin.read(3)
                    except:
                        pass
            
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def run_current_card(self):
        """Execute the current card's assembly."""
        try:
            current_card = self.cards[self.current_card_index]
            print(f"\n🚀 Running {current_card.title}")
            print("📋 This would normally collect input from the assembly")
            
            # Show the assembly structure
            for assembly in current_card.components:
                print(f"🔧 Assembly: {assembly.name}")
                for component in assembly.components:
                    print(f"  📝 Component: {component.name} ({component.component_type})")
                    
            input("\n📥 Press Enter to continue...")
            
        except Exception as e:
            print(f"❌ Error running card: {e}")
            input("Press Enter to continue...")
    
    def run_demo(self):
        """Run the card shuffling demo with proper architecture."""
        try:
            print("🎴 Initializing Proper Card Shuffling Demo...")
            print("🏗️ Using TUI Engine Architecture:")
            print("   - Page with Cards containing Assemblies")
            print("   - Universal visibility system")
            print("   - Central Page.refresh() method")
            input("\nPress Enter to start...")
            
            # Initial setup: show only first card
            self._update_card_visibility()
            self.page.refresh()
            self._display_navigation_info()
            
            # Handle navigation
            while True:
                key = self.get_key()
                
                # Page Up: Previous card
                if key == '\x1b[5~':
                    self.current_card_index = (self.current_card_index - 1) % len(self.cards)
                    self._update_card_visibility()
                    self.page.refresh()
                    self._display_navigation_info()
                    print(f"\n🔄 Shuffled to Card {self.current_card_index + 1}")
                
                # Page Down: Next card
                elif key == '\x1b[6~':
                    self.current_card_index = (self.current_card_index + 1) % len(self.cards)
                    self._update_card_visibility()
                    self.page.refresh()
                    self._display_navigation_info()
                    print(f"\n🔄 Shuffled to Card {self.current_card_index + 1}")
                
                # Number keys for direct navigation
                elif key in ['1', '2', '3', '4', '5']:
                    card_num = int(key) - 1
                    if 0 <= card_num < len(self.cards):
                        self.current_card_index = card_num
                        self._update_card_visibility()
                        self.page.refresh()
                        self._display_navigation_info()
                        print(f"\n🎯 Jumped to Card {key}")
                
                elif key.lower() == 'r':
                    self.run_current_card()
                    self._update_card_visibility()
                    self.page.refresh()
                    self._display_navigation_info()
                
                elif key.lower() == 'a':
                    # Show all cards (architecture demo)
                    print("\n🔍 Showing all cards for architecture overview...")
                    for card in self.cards:
                        card.show()
                    self.page.refresh()
                    input("\nPress Enter to return to single-card view...")
                    self._update_card_visibility()
                    self.page.refresh()
                    self._display_navigation_info()
                
                elif key.lower() == 'q':
                    self.page.clear_screen()
                    print("👋 Proper architecture demo complete!")
                    break
                
                elif key not in ['\x1b', '\r', '\n']:
                    print(f"\n💡 Page Up/Down to navigate, 'r' to run, 'a' for all cards, 'q' to quit")
                    
        except KeyboardInterrupt:
            self.page.clear_screen()
            print("\n👋 Demo interrupted. Goodbye!")


def main():
    """Main entry point for the proper card shuffling demo."""
    print("🎴 Initializing Proper Card Shuffling Demo...")
    print("🏗️ This demo uses the correct TUI engine architecture")
    
    try:
        demo = ProperCardShufflingDemo()
        demo.run_demo()
    except Exception as e:
        print(f"❌ Failed to start demo: {e}")
        print("💡 This demo requires a terminal that supports raw key input")


if __name__ == "__main__":
    main()