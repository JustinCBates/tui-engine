#!/usr/bin/env python3
"""
Page Up/Down Key Interception Demo

Demonstrates direct Page Up/Down key capture with screen clearing and card navigation.
No navigation prompts - just automatic card switching on key press.
"""

import os
import sys
import termios
import tty


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name == 'posix' else 'cls')


def display_header():
    """Display the demo header."""
    print("=" * 60)
    print("🎴 CARD SHUFFLING NAVIGATION DEMO")
    print("=" * 60)
    print("📋 Use Page Up and Down to shuffle cards")
    print("=" * 60)


def display_card(card_index, cards):
    """Display a specific card."""
    card = cards[card_index]
    print(f"\n🎴 Card {card_index + 1}/5: {card['title']}")
    print(f"📝 {card['description']}")
    print("-" * 50)
    print(f"🎯 Currently viewing: Card {card_index + 1} of 5")


def get_key():
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
                # Check for additional characters (Page Up/Down have longer sequences)
                try:
                    import select
                    if select.select([sys.stdin], [], [], 0.01)[0]:
                        ch += sys.stdin.read(3)
                except:
                    pass
        
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


def main():
    """Main demo function."""
    # Card data
    cards = [
        {
            "title": "🏠 Personal Information",
            "description": "Enter your basic personal details"
        },
        {
            "title": "💼 Professional Details", 
            "description": "Tell us about your work experience"
        },
        {
            "title": "🎓 Education Level",
            "description": "Share your educational background"
        },
        {
            "title": "🌟 Preferences",
            "description": "Set your personal preferences"
        },
        {
            "title": "🎯 Goals & Targets",
            "description": "Define your objectives and targets"
        }
    ]
    
    current_card = 0
    
    # Initial display
    clear_screen()
    display_header()
    display_card(current_card, cards)
    
    print(f"\n💡 Press Page Up/Down to navigate, 'q' to quit")
    
    while True:
        try:
            key = get_key()
            
            # Page Up: \x1b[5~
            if key == '\x1b[5~':
                current_card = (current_card - 1) % len(cards)
                clear_screen()
                display_header()
                display_card(current_card, cards)
                print(f"\n🔄 Shuffled to Card {current_card + 1}")
            
            # Page Down: \x1b[6~
            elif key == '\x1b[6~':
                current_card = (current_card + 1) % len(cards)
                clear_screen()
                display_header()
                display_card(current_card, cards)
                print(f"\n🔄 Shuffled to Card {current_card + 1}")
            
            elif key.lower() == 'q':
                clear_screen()
                print("👋 Exiting demo. Thanks for trying!")
                break
            
            elif key not in ['\x1b', '\r', '\n']:
                print(f"\n💡 Press Page Up/Down to navigate, 'q' to quit")
                
        except KeyboardInterrupt:
            clear_screen()
            print("\n👋 Demo interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    print("🎴 Initializing Page Key Navigation Demo...")
    print("💡 Make sure your terminal supports Page Up/Down keys")
    main()