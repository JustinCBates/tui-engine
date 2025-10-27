#!/usr/bin/env python3
"""
TUI Engine Architecture Demo - Visibility and Refresh

Demonstrates the proper TUI engine architecture with:
- Assemblies in Cards and directly on Page
- Universal visibility system (Page, Card, Assembly, Component)
- Central Page.refresh() method for screen management
- State-driven visibility with Page Up/Down navigation
"""

import os
import sys
import termios
import tty

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from questionary_extended.page_runtime import Page


class ArchitectureDemo:
    """
    Demonstrates the TUI engine architecture with proper visibility management.
    
    Features:
    - Mixed structure: Cards with Assemblies + Page-level Assemblies
    - Universal visibility: All elements have show/hide capabilities
    - Central refresh: Page manages all screen updates
    - Page Up/Down navigation with state-driven visibility
    """
    
    def __init__(self):
        self.page = self._create_page()
        self.current_view = 0
        self.views = self._setup_views()
    
    def _create_page(self) -> Page:
        """Create the page structure demonstrating the architecture."""
        page = Page("🏗️ TUI Engine Architecture Demo")
        
        # Card 1: Personal Information with Assembly
        personal_card = page.card("Personal Information", style="bordered")
        personal_assembly = personal_card.assembly("personal")
        personal_assembly.text("name", message="What's your name?")
        personal_assembly.text("age", message="What's your age?")
        
        # Card 2: Preferences with Assembly  
        prefs_card = page.card("Preferences", style="highlighted")
        prefs_assembly = prefs_card.assembly("preferences")
        prefs_assembly.select("theme", message="Choose theme:", choices=["dark", "light", "auto"])
        prefs_assembly.select("language", message="Choose language:", choices=["en", "es", "fr"])
        
        # Page-level Assembly (not in a card)
        config_assembly = page.assembly("configuration")
        config_assembly.text("app_name", message="Application name:")
        config_assembly.select("environment", message="Environment:", choices=["dev", "staging", "prod"])
        
        # Card 3: Advanced Settings with Assembly
        advanced_card = page.card("Advanced Settings", style="collapsible")
        advanced_assembly = advanced_card.assembly("advanced")
        advanced_assembly.text("timeout", message="Timeout (seconds):")
        advanced_assembly.select("log_level", message="Log level:", choices=["DEBUG", "INFO", "WARN", "ERROR"])
        
        return page
    
    def _setup_views(self) -> list:
        """Define different visibility configurations for navigation."""
        return [
            {
                "name": "Personal Info Only",
                "visible_cards": ["Personal Information"],
                "visible_assemblies": [],
                "description": "Show only personal information card"
            },
            {
                "name": "Preferences Only", 
                "visible_cards": ["Preferences"],
                "visible_assemblies": [],
                "description": "Show only preferences card"
            },
            {
                "name": "Configuration Only",
                "visible_cards": [],
                "visible_assemblies": ["configuration"],
                "description": "Show only page-level configuration assembly"
            },
            {
                "name": "Advanced Settings Only",
                "visible_cards": ["Advanced Settings"],
                "visible_assemblies": [],
                "description": "Show only advanced settings card"
            },
            {
                "name": "Personal + Configuration",
                "visible_cards": ["Personal Information"],
                "visible_assemblies": ["configuration"],
                "description": "Show personal card and page-level configuration"
            },
            {
                "name": "All Visible",
                "visible_cards": ["Personal Information", "Preferences", "Advanced Settings"],
                "visible_assemblies": ["configuration"],
                "description": "Show all cards and assemblies"
            }
        ]
    
    def _apply_visibility(self, view_config: dict):
        """Apply visibility settings based on view configuration."""
        # First, hide everything
        for component in self.page.components:
            component.hide()
        
        # Show specified cards
        for component in self.page.components:
            if hasattr(component, 'title') and component.title in view_config["visible_cards"]:
                component.show()
        
        # Show specified page-level assemblies
        for component in self.page.components:
            if hasattr(component, 'name') and component.name in view_config["visible_assemblies"]:
                component.show()
    
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
    
    def display_navigation_info(self):
        """Display current view and navigation instructions."""
        view = self.views[self.current_view]
        print(f"\n🎯 Current View: {view['name']}")
        print(f"📝 {view['description']}")
        print(f"\n📊 View {self.current_view + 1} of {len(self.views)}")
        print("💡 Page Up/Down to navigate views, 'r' to run page, 'q' to quit")
    
    def run_demo(self):
        """Run the architecture demonstration."""
        try:
            print("🏗️ TUI Engine Architecture Demo")
            print("=" * 50)
            print("This demo shows the proper architecture:")
            print("- Cards containing Assemblies")
            print("- Page-level Assemblies (not in cards)")
            print("- Universal visibility system")
            print("- Central Page.refresh() method")
            print("\nUse Page Up/Down to navigate between different visibility configurations")
            input("\nPress Enter to start...")
            
            # Initial view setup
            self._apply_visibility(self.views[self.current_view])
            self.page.refresh()
            self.display_navigation_info()
            
            # Handle navigation
            while True:
                key = self.get_key()
                
                # Page Up: Previous view
                if key == '\x1b[5~':
                    self.current_view = (self.current_view - 1) % len(self.views)
                    self._apply_visibility(self.views[self.current_view])
                    self.page.refresh()
                    self.display_navigation_info()
                
                # Page Down: Next view
                elif key == '\x1b[6~':
                    self.current_view = (self.current_view + 1) % len(self.views)
                    self._apply_visibility(self.views[self.current_view])
                    self.page.refresh()
                    self.display_navigation_info()
                
                elif key.lower() == 'r':
                    print("\n🚀 Running page with current visibility settings...")
                    try:
                        # This would normally run the page interactively
                        # For demo purposes, just show what would be collected
                        print("📊 Page structure (for demonstration):")
                        self._show_structure_info()
                        input("\nPress Enter to continue...")
                        self.page.refresh()
                        self.display_navigation_info()
                    except Exception as e:
                        print(f"❌ Error running page: {e}")
                        input("Press Enter to continue...")
                        self.page.refresh()
                        self.display_navigation_info()
                
                elif key.lower() == 'q':
                    self.page.clear_screen()
                    print("👋 Architecture demo complete!")
                    break
                
                elif key not in ['\x1b', '\r', '\n']:
                    print(f"\n💡 Unknown key. Use Page Up/Down to navigate, 'r' to run, 'q' to quit")
                    
        except KeyboardInterrupt:
            self.page.clear_screen()
            print("\n👋 Demo interrupted. Goodbye!")
    
    def _show_structure_info(self):
        """Show information about the current page structure."""
        print("\n📋 Current Page Structure:")
        
        for i, component in enumerate(self.page.components):
            if not component.visible:
                continue
                
            if hasattr(component, 'title') and hasattr(component, 'components'):
                # This is a Card
                print(f"  🎴 Card: {component.title}")
                for assembly in component.components:
                    if assembly.visible:
                        print(f"    🔧 Assembly: {assembly.name}")
                        for comp in assembly.components:
                            if comp.visible:
                                print(f"      📝 Component: {comp.name} ({comp.component_type})")
                                
            elif hasattr(component, 'name') and hasattr(component, 'components'):
                # This is a page-level Assembly
                print(f"  🔧 Page Assembly: {component.name}")
                for comp in component.components:
                    if comp.visible:
                        print(f"    📝 Component: {comp.name} ({comp.component_type})")


def main():
    """Main entry point for the architecture demo."""
    print("🏗️ Initializing TUI Engine Architecture Demo...")
    print("💡 This demo showcases proper Page/Card/Assembly structure")
    
    try:
        demo = ArchitectureDemo()
        demo.run_demo()
    except Exception as e:
        print(f"❌ Failed to start demo: {e}")
        print("💡 This demo requires a terminal that supports raw key input")


if __name__ == "__main__":
    main()