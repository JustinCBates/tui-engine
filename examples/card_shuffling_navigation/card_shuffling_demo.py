#!/usr/bin/env python3
"""
Card Shuffling Navigation Demo with TUI Engine

This demo showcases a single page with 5 cards where only one is visible at a time.
Users can navigate between cards using actual Page Up/Down keys.
Each card contains descriptive text and a simple integer input assembly.

This version intercepts Page Up/Down keys directly and auto-navigates with screen clearing.
"""

import sys
import os
import termios
import tty
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from questionary_extended.page_runtime import Page
from questionary_extended.assembly_runtime import Assembly


class CardShufflingDemo:
    """
    Demonstrates card-based navigation with direct Page Up/Down key capture.
    
    Features:
    - Single page with multiple assemblies (representing cards)
    - Only one assembly visible/active at a time
    - Real Page Up/Down key interception
    - Automatic screen clearing and card display
    - Each assembly has descriptive text and an integer input
    """
    
    def __init__(self):
        self.current_card_index = 0
        self.assemblies: List[Assembly] = []
        self.assembly_configs = []
        self.results: Dict[str, Any] = {}
        self.setup_assemblies()
    
    def setup_assemblies(self):
        """Create 5 assemblies representing different cards."""
        
        # Assembly configurations (representing our "cards")
        self.assembly_configs = [
            {
                "name": "personal_info",
                "title": "🏠 Personal Information",
                "description": "Enter your basic personal details",
                "prompt": "What is your age?",
                "field": "age"
            },
            {
                "name": "professional", 
                "title": "💼 Professional Details",
                "description": "Tell us about your work experience",
                "prompt": "How many years of experience do you have?",
                "field": "experience_years"
            },
            {
                "name": "education",
                "title": "🎓 Education Level",
                "description": "Share your educational background",
                "prompt": "How many degrees do you hold?",
                "field": "degrees_count"
            },
            {
                "name": "preferences",
                "title": "🌟 Preferences",
                "description": "Set your personal preferences",
                "prompt": "Rate your interest level (1-10):",
                "field": "interest_rating"
            },
            {
                "name": "goals",
                "title": "🎯 Goals & Targets",
                "description": "Define your objectives and targets",
                "prompt": "How many goals do you want to achieve this year?",
                "field": "goals_count"
            }
        ]
    
    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_header(self):
        """Display the demo header with instructions."""
        print("="*60)
        print("🎴 CARD SHUFFLING NAVIGATION DEMO")
        print("="*60)
        print("📋 Use Page Up and Down to shuffle cards")
        print("📋 Press 'R' to run current card, 'Q' to quit, 'S' for results")
        print("="*60)
    
    def show_current_card(self):
        """Display the current card information."""
        config = self.assembly_configs[self.current_card_index]
        
        print(f"\n🎴 Card {self.current_card_index + 1}/5: {config['title']}")
        print(f"📝 {config['description']}")
        print("-" * 50)
        print(f"🎯 Currently viewing: Card {self.current_card_index + 1} of 5")
        print(f"⌨️  Use Page Up/Down keys to navigate")
    
    def display_full_screen(self):
        """Clear screen and display header + current card."""
        self.clear_screen()
        self.display_header()
        self.show_current_card()
    
    def navigate_to_card(self, card_index: int) -> bool:
        """Navigate to a specific card by index."""
        if 0 <= card_index < len(self.assembly_configs):
            self.current_card_index = card_index
            self.display_full_screen()
            return True
        return False
    
    def next_card(self):
        """Move to the next card (wrapping around)."""
        next_index = (self.current_card_index + 1) % len(self.assembly_configs)
        self.navigate_to_card(next_index)
        print(f"\n🔄 Shuffled to Card {next_index + 1}")
    
    def previous_card(self):
        """Move to the previous card (wrapping around)."""
        prev_index = (self.current_card_index - 1) % len(self.assembly_configs)
        self.navigate_to_card(prev_index)
        print(f"\n🔄 Shuffled to Card {prev_index + 1}")
    
    def get_key(self):
        """Get a single keypress from the terminal."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            ch = sys.stdin.read(1)
            
            # Handle escape sequences (arrow keys, page up/down, etc.)
            if ch == '\x1b':  # ESC sequence
                ch += sys.stdin.read(2)
                if len(ch) == 3:
                    # Check for additional characters (Page Up/Down have longer sequences)
                    try:
                        # Set a very short timeout to check for more characters
                        import select
                        if select.select([sys.stdin], [], [], 0.01)[0]:
                            ch += sys.stdin.read(3)
                    except:
                        pass
            
            return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    
    def handle_key_navigation(self):
        """Handle keyboard navigation with direct key capture."""
        print(f"\n💡 Press Page Up/Down to navigate, 'r' to run card, 's' for results, 'q' to quit")
        
        while True:
            try:
                key = self.get_key()
                
                # Page Up: \x1b[5~
                if key == '\x1b[5~':
                    self.previous_card()
                
                # Page Down: \x1b[6~
                elif key == '\x1b[6~':
                    self.next_card()
                
                # Regular keys
                elif key.lower() == 'r':
                    print(f"\n🚀 Running current card...")
                    self.run_current_card()
                    input("\n📥 Press Enter to continue navigating...")
                    self.display_full_screen()
                
                elif key.lower() == 's':
                    self.display_full_screen()
                    self.show_results()
                    input("\n📥 Press Enter to continue navigating...")
                    self.display_full_screen()
                
                elif key.lower() == 'q':
                    self.clear_screen()
                    print("👋 Exiting demo. Thanks for trying the Card Shuffling Navigation!")
                    break
                
                # Number keys for direct navigation
                elif key in ['1', '2', '3', '4', '5']:
                    card_num = int(key) - 1
                    if self.navigate_to_card(card_num):
                        print(f"\n🎯 Jumped to Card {key}")
                
                # Show help for unknown keys
                elif key not in ['\x1b', '\r', '\n']:
                    print(f"\n❓ Unknown key. Use Page Up/Down to navigate, 'r' to run, 's' for results, 'q' to quit")
                    
            except KeyboardInterrupt:
                self.clear_screen()
                print("\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Navigation error: {e}")
                print("💡 Use 'q' to quit if navigation is stuck")
    
    def run_current_card(self) -> Optional[Dict[str, Any]]:
        """Execute the assembly for the current card."""
        try:
            config = self.assembly_configs[self.current_card_index]
            
            print(f"\n🚀 Running Card {self.current_card_index + 1}: {config['title']}")
            print(f"📋 {config['description']}")
            print("-" * 40)
            
            # Get integer input from user
            while True:
                try:
                    value = input(f"🔢 {config['prompt']} ")
                    integer_value = int(value)
                    
                    # Store the result
                    result = {config['field']: integer_value}
                    self.results[config['name']] = result
                    
                    print(f"✅ Card {self.current_card_index + 1} completed!")
                    print(f"📊 Stored: {config['field']} = {integer_value}")
                    
                    return result
                    
                except ValueError:
                    print("❌ Please enter a valid integer.")
                except KeyboardInterrupt:
                    print("\n❌ Input cancelled.")
                    return None
                    
        except Exception as e:
            print(f"❌ Error running card: {e}")
            return None
    
    def show_results(self):
        """Display all collected results."""
        print(f"\n📊 COLLECTED RESULTS:")
        print("=" * 30)
        if self.results:
            for assembly_name, data in self.results.items():
                config = next((c for c in self.assembly_configs if c['name'] == assembly_name), None)
                if config:
                    print(f"🎴 {config['title']}")
                    for field, value in data.items():
                        print(f"   📋 {field}: {value}")
                    print()
        else:
            print("📊 No results collected yet.")
            print("💡 Tip: Press 'r' to run cards and collect data.")
    
    def run_demo(self):
        """Run the complete card shuffling demo."""
        try:
            # Initial display
            self.display_full_screen()
            print("\n🎴 Welcome to the Card Shuffling Navigation Demo!")
            print("🎯 Use Page Up/Down keys to navigate between cards")
            
            # Handle keyboard navigation
            self.handle_key_navigation()
            
            # Show final results
            if self.results:
                print(f"\n🎉 Demo Session Summary:")
                self.show_results()
            
        except KeyboardInterrupt:
            self.clear_screen()
            print("\n👋 Demo interrupted. Goodbye!")
        except Exception as e:
            print(f"❌ Demo error: {e}")


def main():
    """Main entry point for the card shuffling demo."""
    print("🎴 Initializing Card Shuffling Navigation Demo...")
    print("💡 Make sure your terminal supports Page Up/Down key detection")
    
    try:
        demo = CardShufflingDemo()
        demo.run_demo()
    except Exception as e:
        print(f"❌ Failed to start demo: {e}")
        print("💡 This demo requires a terminal that supports raw key input")


if __name__ == "__main__":
    main()

import sys
import os
from typing import Dict, Any, List, Optional

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from questionary_extended.page_runtime import Page
from questionary_extended.assembly_runtime import Assembly


class CardShufflingDemo:
    """
    Demonstrates card-based navigation with the TUI engine.
    
    Features:
    - Single page with multiple assemblies (representing cards)
    - Only one assembly visible/active at a time
    - Page Up/Down navigation between assemblies
    - Numeric key shortcuts (1-5)
    - Each assembly has descriptive text and an integer input
    """
    
    def __init__(self):
        self.current_card_index = 0
        self.assemblies: List[Assembly] = []
        self.assembly_configs = []
        self.results: Dict[str, Any] = {}
        self.setup_assemblies()
    
    def setup_assemblies(self):
        """Create 5 assemblies representing different cards."""
        
        # Assembly configurations (representing our "cards")
        self.assembly_configs = [
            {
                "name": "personal_info",
                "title": "🏠 Personal Information",
                "description": "Enter your basic personal details",
                "prompt": "What is your age?",
                "field": "age"
            },
            {
                "name": "professional", 
                "title": "💼 Professional Details",
                "description": "Tell us about your work experience",
                "prompt": "How many years of experience do you have?",
                "field": "experience_years"
            },
            {
                "name": "education",
                "title": "🎓 Education Level",
                "description": "Share your educational background",
                "prompt": "How many degrees do you hold?",
                "field": "degrees_count"
            },
            {
                "name": "preferences",
                "title": "🌟 Preferences",
                "description": "Set your personal preferences",
                "prompt": "Rate your interest level (1-10):",
                "field": "interest_rating"
            },
            {
                "name": "goals",
                "title": "🎯 Goals & Targets",
                "description": "Define your objectives and targets",
                "prompt": "How many goals do you want to achieve this year?",
                "field": "goals_count"
            }
        ]
    
    def display_header(self):
        """Display the demo header with instructions."""
        print("\n" + "="*60)
        print("🎴 CARD SHUFFLING NAVIGATION DEMO")
        print("="*60)
        print("📋 Instructions:")
        print("   • Use Page Up/Down to shuffle between cards")
        print("   • Use numeric keys 1-5 to jump to specific cards")
        print("   • Each card contains a simple integer input")
        print("   • Press Ctrl+C to exit at any time")
        print("="*60)
    
    def show_current_card(self):
        """Display the current card information."""
        config = self.assembly_configs[self.current_card_index]
        
        print(f"\n🎴 Card {self.current_card_index + 1}/5: {config['title']}")
        print(f"📝 {config['description']}")
        print("-" * 50)
        print(f"🎯 Currently showing: Card {self.current_card_index + 1}/5")
    
    def navigate_to_card(self, card_index: int) -> bool:
        """Navigate to a specific card by index."""
        if 0 <= card_index < len(self.assembly_configs):
            self.current_card_index = card_index
            self.show_current_card()
            return True
        return False
    
    def next_card(self):
        """Move to the next card (wrapping around)."""
        next_index = (self.current_card_index + 1) % len(self.assembly_configs)
        self.navigate_to_card(next_index)
        print(f"🔄 Shuffled to next card: {next_index + 1}")
    
    def previous_card(self):
        """Move to the previous card (wrapping around)."""
        prev_index = (self.current_card_index - 1) % len(self.assembly_configs)
        self.navigate_to_card(prev_index)
        print(f"🔄 Shuffled to previous card: {prev_index + 1}")
    
    def run_current_card(self) -> Optional[Dict[str, Any]]:
        """Execute the assembly for the current card."""
        try:
            config = self.assembly_configs[self.current_card_index]
            
            print(f"\n🚀 Running Card {self.current_card_index + 1}: {config['title']}")
            print(f"📋 {config['description']}")
            print("-" * 40)
            
            # Get integer input from user
            while True:
                try:
                    value = input(f"🔢 {config['prompt']} ")
                    integer_value = int(value)
                    
                    # Store the result
                    result = {config['field']: integer_value}
                    self.results[config['name']] = result
                    
                    print(f"✅ Card {self.current_card_index + 1} completed!")
                    print(f"� Stored: {config['field']} = {integer_value}")
                    
                    return result
                    
                except ValueError:
                    print("❌ Please enter a valid integer.")
                except KeyboardInterrupt:
                    print("\n❌ Input cancelled.")
                    return None
                    
        except Exception as e:
            print(f"❌ Error running card: {e}")
            return None
    
    def handle_navigation_input(self):
        """Handle user input for navigation."""
        while True:
            print("\n" + "="*50)
            print("🎮 Navigation Options:")
            print("   [N] Next card (Page Down)")
            print("   [P] Previous card (Page Up)")
            print("   [1-5] Jump to specific card")
            print("   [R] Run current card")
            print("   [S] Show all results")
            print("   [Q] Quit demo")
            print("="*50)
            
            try:
                choice = input("\n📥 Enter your choice: ").strip().lower()
                
                if choice == 'n':
                    self.next_card()
                elif choice == 'p':
                    self.previous_card()
                elif choice in ['1', '2', '3', '4', '5']:
                    card_num = int(choice) - 1
                    if self.navigate_to_card(card_num):
                        print(f"🎯 Jumped to card {choice}")
                elif choice == 'r':
                    self.run_current_card()
                elif choice == 's':
                    self.show_results()
                elif choice == 'q':
                    print("👋 Exiting demo. Thanks for trying the Card Shuffling Navigation!")
                    return
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n\n👋 Demo interrupted. Goodbye!")
                return
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def show_results(self):
        """Display all collected results."""
        if self.results:
            print("\n� Collected Results:")
            print("-" * 30)
            for assembly_name, data in self.results.items():
                config = next((c for c in self.assembly_configs if c['name'] == assembly_name), None)
                if config:
                    print(f"🎴 {config['title']}")
                    for field, value in data.items():
                        print(f"   📋 {field}: {value}")
        else:
            print("\n📊 No results collected yet.")
            print("💡 Tip: Use 'R' to run cards and collect data.")
    
    def run_demo(self):
        """Run the complete card shuffling demo."""
        try:
            self.display_header()
            print("\n🎴 Welcome to the Card Shuffling Navigation Demo!")
            print("🎯 Starting with Card 1...")
            
            # Show the first card
            self.show_current_card()
            
            # Handle navigation and user input
            self.handle_navigation_input()
            
            # Show final results
            print("\n🎉 Demo Session Summary:")
            self.show_results()
            
        except KeyboardInterrupt:
            print("\n\n👋 Demo interrupted. Goodbye!")
        except Exception as e:
            print(f"❌ Demo error: {e}")


def main():
    """Main entry point for the card shuffling demo."""
    demo = CardShufflingDemo()
    demo.run_demo()


if __name__ == "__main__":
    main()
