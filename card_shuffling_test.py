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
        # Enable spatial layout and buffer management to prevent instruction duplication
        header_lines = [
            "Navigation: ← → (arrow keys) or A/D to move between cards",
            "Space: Toggle current card visibility",
            "T: Run animation test (5 cards transition)",
            "Q: Quit demo",
            "",
        ]
        self.page = PageBase("🎴 Card Shuffling Navigation", use_spatial_layout=False, header=header_lines)
        self.current_card = 0
        self.status_message = ""
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
        # Instructions are now placed in header via Page constructor; keep this
        # method for backward compatibility but no-op.
        return
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update the status message.
        
        Uses the page's built-in text_status method for clean display management.
        """
        self.status_message = message
        # Use the page's built-in status method
        self.page.text_status(message, status_type)
    
    def _setup_cards(self):
        """Create the 5 demo cards with bordered style."""
        from src.questionary_extended.core.card import Card

        # Ensure body section exists
        body = self.page.body_section()

        self.cards = []
        titles = [
            "🏠 Personal Information",
            "💼 Professional Details",
            "🎓 Education Level",
            "🌟 Preferences",
            "🎯 Goals & Targets",
        ]
        for t in titles:
            c = Card(t, self.page, style="bordered")
            body.add_element(c)
            self.cards.append(c)
    
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

            # Use questionary when available, but allow forcing plain input
            # via environment for environments where questionary clears the
            # terminal (e.g., alternate screen). Prefer plain input when
            # TUI_NO_QUESTIONARY=1 is set.
            import os
            use_questionary = os.environ.get('TUI_NO_QUESTIONARY', '') == ''

            # Use our Component wrapper to present the prompt so the wrapper's
            # stdout/stderr proxy can capture any clears and propagate them to
            # the Page. This avoids calling questionary directly from the demo
            # and ensures the spatial rendering system can respond.
            from src.questionary_extended.core.component_wrappers import Component

            comp = Component(name="interactive_choice", component_type="text", message="📥 Your choice:")
            try:
                comp.activate_for_input(0)
                result = comp.render_interactive_prompt()
            except KeyboardInterrupt:
                self.page.text_status("Demo interrupted. Goodbye!", "info")
                self.page.refresh()
                break
            except Exception:
                # Fall back to plain input if something goes wrong
                try:
                    raw = input("📥 Your choice: ")
                except KeyboardInterrupt:
                    self.page.text_status("Demo interrupted. Goodbye!", "info")
                    self.page.refresh()
                    break
                result = raw
            finally:
                try:
                    comp.deactivate()
                except Exception:
                    pass

            choice = result

            # Re-assert page rendering after returning from the prompt; the
            # component propagation already notifies the Page if a clear was
            # detected. As an extra safeguard (covers prompt backends that
            # write directly to the TTY), clear the screen and then refresh
            # the spatial render so the UI is visible again.
            try:
                self.page.clear_screen()
            except Exception:
                pass
            try:
                self.page.refresh()
            except Exception:
                pass

            choice = str(choice).strip().lower()

            if choice == 'n':
                self.current_card = (self.current_card + 1) % len(self.cards)
                self.show_only_current_card()
                # Clear any transient error/status shown previously
                self.page.clear_status()

            elif choice == 'p':
                self.current_card = (self.current_card - 1) % len(self.cards)
                self.show_only_current_card()
                # Clear any transient error/status shown previously
                self.page.clear_status()

            elif choice in ['1', '2', '3', '4', '5']:
                new_card = int(choice) - 1
                if 0 <= new_card < len(self.cards):
                    self.current_card = new_card
                    self.show_only_current_card()
                    # Clear any transient error/status shown previously
                    self.page.clear_status()

            elif choice == 'a':
                self.show_all_cards()
                # Clear any transient error/status shown previously
                self.page.clear_status()

            elif choice == 'q':
                self.update_status("Demo completed!", "success")
                self.page.refresh()
                break

            else:
                self.update_status("Invalid choice. Use: n/p/1-5/a/q", "error")
                # Single refresh to show the error status; avoid duplicate refresh
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


def run_section_demo():
    """Simple demo that displays a page with title, header and body sections.

    This demo uses no interactive prompts. It places explicit text in each
    section so the user can see where the title, header and body are rendered.
    Ctrl-C is not intercepted here and will behave normally.
    """
    from src.questionary_extended.core.page_base import PageBase
    from src.questionary_extended.core.component_wrappers import text_display

    # Title text is provided to the Page constructor. Header lines go in
    # the header section. The body gets one element that explains itself.
    header_lines = [
        "Header Section: This is the header",
        "Instruction: This demo shows title/header/body only (no prompts).",
        "Instruction: Press Ctrl-C to interrupt and return to the menu.",
        "Instruction: Press Enter after viewing to return to the main menu.",
    ]

    page = PageBase("Title Section: This is the title", use_spatial_layout=True, header=header_lines)

    body = page.body_section()

    # Add a single bordered card into the body with explanatory text
    from src.questionary_extended.core.card import Card
    card = Card("🔖 Demo Card", page, style="bordered")
    card.add_element(text_display("Inside Demo Card: This card lives in the body."))
    body.add_element(card)
    # Start the first card hidden by default
    try:
        card.hide()
    except Exception:
        # If Card doesn't support hide at construction time for some reason,
        # ignore the error so the demo still runs.
        pass

    # Add a second card to the body to demonstrate multiple cards in the
    # body section. This card uses a different title and explanatory text.
    card2 = Card("🔷 Second Demo Card", page, style="bordered")
    card2.add_element(text_display("Inside Second Demo Card: Additional body content."))
    body.add_element(card2)

    # Add a third card, initially hidden
    card3 = Card("🟩 Third Demo Card", page, style="bordered")
    card3.add_element(text_display("Inside Third Demo Card: Extra content."))
    body.add_element(card3)
    # Ensure the third card starts hidden to match the `visible` state below
    try:
        card3.hide()
    except Exception:
        # If hide() isn't supported at this point, ignore so demo still runs
        pass

    # Small instructional line after the cards so the prompt text is visible
    body.add_element(text_display("Press Tab to cycle cards or Enter to exit..."))

    # Render once and then enter a small input loop that allows the user to
    # press Tab to toggle visibility of the cards in the body or Enter to
    # return to the main menu. We intentionally do not swallow Ctrl-C so the
    # user can interrupt and return immediately.
    page.refresh()

    # Track visibility state explicitly for the three-card demo. Second card
    # starts visible and others hidden.
    cards = [card, card2, card3]
    visible = [False, True, False]

    prompt_msg = "✨ Press Tab to toggle cards or Enter to return to main menu..."

    import sys
    try:
        import termios
        fd = sys.stdin.fileno()
        old_attrs = termios.tcgetattr(fd)
        termios_ok = True
    except Exception:
        termios_ok = False
    if termios_ok:
        try:
            # Put terminal into cbreak-like mode (disable canonical & echo but keep ISIG)
            new_attrs = termios.tcgetattr(fd)
            new_attrs[3] = new_attrs[3] & ~termios.ICANON & ~termios.ECHO
            termios.tcsetattr(fd, termios.TCSADRAIN, new_attrs)

            while True:
                try:
                    # Display prompt in the page status area so spatial rendering handles it
                    try:
                        page.text_status(prompt_msg, "info")
                    except Exception:
                        # Fallback to printing if status API isn't available
                        print("\n" + prompt_msg)
                    page.refresh()

                    ch = sys.stdin.read(1)
                    if not ch:
                        continue

                    # Tab toggles each card's visibility (invert). This matches
                    # the original two-card behavior.
                    if ch == "\t":
                        for i, c in enumerate(cards):
                            visible[i] = not visible[i]
                            try:
                                if visible[i]:
                                    c.show()
                                else:
                                    c.hide()
                            except Exception:
                                pass
                            try:
                                c.mark_dirty()
                            except Exception:
                                pass
                        page.refresh()

                    # Enter/Return exits the demo
                    elif ch in ("\r", "\n"):
                        break

                    # Ctrl-C will raise KeyboardInterrupt because ISIG is preserved
                except KeyboardInterrupt:
                    # Restore terminal attrs then re-raise so caller can handle it
                    raise
        finally:
            try:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_attrs)
            except Exception:
                pass
            try:
                page.clear_status()
            except Exception:
                pass
            try:
                page.refresh()
            except Exception:
                pass
    else:
        # Fallback for non-tty environments: use simple input loop. Here the
        # user can type 't' (then Enter) to toggle or press Enter to return.
        try:
            while True:
                try:
                    page.text_status(prompt_msg + " (or type 't' + Enter to toggle)", "info")
                except Exception:
                    print("\n" + prompt_msg + " (or type 't' + Enter to toggle)")
                page.refresh()
                try:
                    resp = input()
                except KeyboardInterrupt:
                    raise
                except EOFError:
                    # Non-interactive stdin closed; exit the fallback loop
                    break
                if resp == "":
                    break
                if resp.lower().strip().startswith('t'):
                    # In the fallback, toggle each card's visibility (invert)
                    for i, c in enumerate(cards):
                        visible[i] = not visible[i]
                        try:
                            if visible[i]:
                                c.show()
                            else:
                                c.hide()
                        except Exception:
                            pass
                        try:
                            c.mark_dirty()
                        except Exception:
                            pass
                    page.refresh()
        finally:
            try:
                page.clear_status()
            except Exception:
                pass
            try:
                page.refresh()
            except Exception:
                pass


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
                "🧭 Section Demo - Title/Header/Body (no prompts)",
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

        elif "Section Demo" in choice:
            # Simple demo that displays a Page with title, header and body
            # sections and no interactive prompts. The demo itself handles
            # Tab/Enter input (Tab toggles cards, Enter returns). Ctrl-C
            # remains available to interrupt.
            run_section_demo()
            
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
        # Allow a top-level --debug flag to enable internal debug logging even
        # when the script also accepts positional subcommands. We enable the
        # project's DebugMode and remove the flag so downstream arg parsing
        # doesn't treat it as an unknown option.
        if '--debug' in sys.argv:
            try:
                from src.questionary_extended.core.debug_mode import DebugMode
                DebugMode.enable()
            except Exception:
                # Best-effort; ignore if debug mode cannot be enabled
                pass
            # Remove the debug flag so later arg handling won't fail
            sys.argv = [a for a in sys.argv if a != '--debug']

        # Install a questionary factory that avoids alternate-screen behaviour
        # by using prompt_toolkit non-fullscreen prompts where available.
        # If prompt_toolkit isn't available we won't override the default
        # questionary behavior (no fake prompts will be used).
        try:
            from src.tui_engine.questionary_factory import (
                set_prompt_toolkit_non_fullscreen_factory,
            )
            try:
                set_prompt_toolkit_non_fullscreen_factory()
            except Exception:
                # If prompt_toolkit is unavailable, leave default questionary
                # import behavior in place (do not install fake/plain prompts).
                pass
        except Exception:
            # Best-effort; do not fail startup if DI helper cannot be imported
            pass

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