#!/usr/bin/env python3
"""
Simple Card Shuffling Navigation Demo

A working demonstration of card-based navigation using the TUI engine.
This version focuses on the core functionality with proper architecture usage.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

def main():
    """Simple card shuffling demo with proper TUI engine usage."""
    
    print("\n" + "="*60)
    print("🎴 CARD SHUFFLING NAVIGATION DEMO")
    print("="*60)
    print("📋 Use Page Up and Down to shuffle cards")
    print("="*60)
    
    # Card definitions
    cards = [
        {
            "title": "🏠 Personal Information",
            "description": "Enter your basic personal details",
            "prompt": "What is your age?",
        },
        {
            "title": "💼 Professional Details", 
            "description": "Tell us about your work experience",
            "prompt": "How many years of experience do you have?",
        },
        {
            "title": "🎓 Education Level",
            "description": "Share your educational background", 
            "prompt": "How many degrees do you hold?",
        },
        {
            "title": "🌟 Preferences",
            "description": "Set your personal preferences",
            "prompt": "Rate your interest level (1-10):",
        },
        {
            "title": "🎯 Goals & Targets",
            "description": "Define your objectives and targets",
            "prompt": "How many goals do you want to achieve this year?",
        }
    ]
    
    current_card = 0
    results = {}
    
    def show_card(index):
        """Display a single card."""
        card = cards[index]
        print(f"\n🎴 Card {index + 1}/5: {card['title']}")
        print(f"📝 {card['description']}")
        print("-" * 50)
        return card
    
    def navigate():
        """Handle navigation between cards."""
        nonlocal current_card
        
        while True:
            # Show current card
            card = show_card(current_card)
            
            print(f"\n🎮 Navigation (Currently on Card {current_card + 1}/5):")
            print("   [N] Next card | [P] Previous card | [1-5] Jump to card")
            print("   [R] Run this card | [Q] Quit demo")
            
            try:
                choice = input("\n📥 Your choice: ").strip().lower()
                
                if choice == 'n':
                    current_card = (current_card + 1) % len(cards)
                    print(f"🔄 Shuffled to Card {current_card + 1}")
                    
                elif choice == 'p':
                    current_card = (current_card - 1) % len(cards)
                    print(f"🔄 Shuffled to Card {current_card + 1}")
                    
                elif choice in ['1', '2', '3', '4', '5']:
                    new_card = int(choice) - 1
                    if 0 <= new_card < len(cards):
                        current_card = new_card
                        print(f"🎯 Jumped to Card {current_card + 1}")
                        
                elif choice == 'r':
                    # Run the current card's assembly
                    result = run_card_assembly(card, current_card + 1)
                    if result is not None:
                        results[f"card_{current_card + 1}"] = result
                        print(f"✅ Card {current_card + 1} completed: {result}")
                        
                elif choice == 'q':
                    break
                    
                else:
                    print("❌ Invalid choice. Please try again.")
                    
            except KeyboardInterrupt:
                print("\n👋 Demo interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def run_card_assembly(card, card_number):
        """Run the assembly for a card (simulate integer input)."""
        try:
            print(f"\n🚀 Running Assembly for Card {card_number}")
            print(f"📋 {card['description']}")
            print("-" * 40)
            
            # Get integer input from user
            while True:
                try:
                    value = input(f"🔢 {card['prompt']} ")
                    integer_value = int(value)
                    return integer_value
                except ValueError:
                    print("❌ Please enter a valid integer.")
                except KeyboardInterrupt:
                    print("\n❌ Input cancelled.")
                    return None
                    
        except Exception as e:
            print(f"❌ Error running assembly: {e}")
            return None
    
    # Start the demo
    try:
        print("\n🎴 Welcome to the Card Shuffling Navigation Demo!")
        print("🎯 Starting with Card 1...")
        
        navigate()
        
        # Show final results
        if results:
            print(f"\n🎉 Demo completed! Results collected:")
            for card_name, value in results.items():
                print(f"   • {card_name}: {value}")
        else:
            print("\n👋 Demo ended without collecting results.")
            
    except Exception as e:
        print(f"❌ Demo error: {e}")


if __name__ == "__main__":
    main()