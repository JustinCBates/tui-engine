#!/usr/bin/env python3
"""
Card Swapping Demo - Using New TUI Engine Architecture

This demo showcases a single page with multiple data collection containers
that can be navigated one at a time. It demonstrates:
- Page section organization (title, header, body, footer)
- Container visibility management
- Keyboard navigation between containers
- Data collection workflow

Features:
- 5 data collection containers (only one visible at a time)
- Navigation with PgUp/PgDn keys
- CTRL+C to exit
- Save/Close buttons in footer
- Bordered containers for visual organization

Run with:
    python demos/demo_swap_cards.py
"""

import sys
import os
import json
from pathlib import Path

# Add the src directory to the path so we can import our TUI Engine
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tui_engine.page import Page
from tui_engine.app import App
from tui_engine.container import Container
from tui_engine.text_element import TextElement, DynamicTextElement
from tui_engine.input_component import SingleLineInput, MultiLineInput
from tui_engine.button_component import Buttons
from tui_engine.component_base import Validators
from tui_engine.radio_component import RadioButtons


class CardSwapDemo:
    """Manages the card swapping demo state and navigation."""
    
    def __init__(self):
        self.current_container = 0
        self.total_containers = 5
        self.data = {}  # Store collected data
        self.component_touched = {}  # Track which components have been touched
        self.component_valid = {}    # Track validation state of components
        
    def mark_component_touched(self, component_name: str):
        """Mark a component as having been touched by the user."""
        self.component_touched[component_name] = True
        
    def is_component_touched(self, component_name: str) -> bool:
        """Check if a component has been touched."""
        return self.component_touched.get(component_name, False)
        
    def set_component_valid(self, component_name: str, is_valid: bool):
        """Set the validation state of a component."""
        self.component_valid[component_name] = is_valid
        
    def is_component_valid(self, component_name: str) -> bool:
        """Check if a component is valid."""
        return self.component_valid.get(component_name, False)
        
    def is_card_valid(self, card_index: int) -> bool:
        """Check if all components in a card are valid and touched."""
        card_components = self.get_card_components(card_index)
        if not card_components:
            return False
            
        for component_name in card_components:
            if not self.is_component_touched(component_name) or not self.is_component_valid(component_name):
                return False
        return True
        
    def get_card_components(self, card_index: int) -> list[str]:
        """Get the list of component names for a given card."""
        card_components = {
            0: ["project_name", "version_tag"],  # Project Information
            1: ["deployment_type", "db_type"],   # Environment Settings
            2: ["image_name", "port_mapping"],   # Container Configuration
            3: ["requirements"],                 # Dependencies
            4: ["notes"]                        # Additional Notes
        }
        return card_components.get(card_index, [])
        
    def are_all_cards_valid(self) -> bool:
        """Check if all cards are valid."""
        for i in range(self.total_containers):
            if not self.is_card_valid(i):
                return False
        return True
        
    def next_container(self):
        """Navigate to the next container."""
        if self.current_container < self.total_containers - 1:
            self.current_container += 1
            return True
        return False
    
    def previous_container(self):
        """Navigate to the previous container."""
        if self.current_container > 0:
            self.current_container -= 1
            return True
        return False
    
    def get_container_info(self):
        """Get current container information."""
        return f"Container {self.current_container + 1} of {self.total_containers}"
    
    def save_data(self, form_data: dict):
        """Save the collected data."""
        self.data.update(form_data)
        output_file = Path(__file__).parent / "card_swap_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.data, f, indent=2)
        return output_file


def create_data_containers(demo: CardSwapDemo) -> list[Container]:
    """Create the 5 data collection containers."""
    containers = []
    
    # Custom validators
    def validate_project_name(value: str) -> str:
        """Validate project name: no spaces, only letters/numbers, at least 1 char."""
        if not value or len(value.strip()) == 0:
            return "Project name is required"
        elif ' ' in value:
            return "Project name cannot contain spaces"
        elif not value.replace('_', '').replace('-', '').isalnum():
            return "Project name can only contain letters, numbers, hyphens, and underscores"
        return ""
    
    def validate_version_tag(value: str) -> str:
        """Validate version tag: no spaces, specific allowed characters, at least 1 char."""
        if not value or len(value.strip()) == 0:
            return "Version tag is required"
        elif ' ' in value:
            return "Version tag cannot contain spaces"
        else:
            # Check for allowed characters: letters, numbers, /-_()#[]@
            allowed_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/-_()#[]@.')
            if not all(c in allowed_chars for c in value):
                return "Version tag can only contain letters, numbers, and these symbols: /-_()#[]@."
        return ""
    
    # Container 1: Project Information
    container1 = Container("project_info")
    container1.set_title("Project Information").set_border(True)
    
    project_name = SingleLineInput("project_name")
    project_name.set_placeholder("ProjectName")
    project_name.set_required(True)
    project_name.add_validation_rule(validate_project_name)

    container1.add(TextElement("name_label", "Project Name: (docker containers will be prepended with this name)"))
    container1.add(project_name)

    tag_input = SingleLineInput("version_tag")
    tag_input.set_placeholder("v1.0.0, latest, etc.")
    tag_input.set_required(True)
    tag_input.add_validation_rule(validate_version_tag)
    
    container1.add(TextElement("tag_label", "Version Tag:"))
    container1.add(tag_input)
    
    containers.append(container1)
    
        # Container 2: Environment Settings
    container2 = Container("environment")
    container2.set_title("Environment Settings").set_border(True)
    container2.set_layout_direction("horizontal")  # Set horizontal layout

    # Sub-container 1: Deployment Type
    deployment_container = Container("deployment_container")
    deployment_container.set_border(False)  # Remove border
    deployment_container.add(TextElement("deployment_label", "Deployment Type"))
    deployment_radio = RadioButtons.local_remote("deployment_type", "local")
    deployment_radio.set_hint("Choose where to deploy your application")
    deployment_container.add(deployment_radio)
    container2.add(deployment_container)

    # Sub-container 2: Environment
    env_container = Container("env_container")
    env_container.set_border(False)  # Remove border
    env_container.add(TextElement("env_label", "Environment"))
    environment_radio = RadioButtons.environment("environment", "development")
    environment_radio.set_hint("Select the target environment")
    env_container.add(environment_radio)
    container2.add(env_container)

    # Sub-container 3: Linux Distribution
    distro_container = Container("distro_container")
    distro_container.set_border(False)  # Remove border
    distro_container.add(TextElement("distro_label", "Linux Distribution"))
    distro_radio = RadioButtons.linux_distro("linux_distro", "debian")
    distro_radio.set_hint("Choose your preferred Linux distribution")
    distro_container.add(distro_radio)
    container2.add(distro_container)
    
    containers.append(container2)
    
    # Container 3: Experience
    container3 = Container("experience")
    container3.set_title("Experience & Background").set_border(True)
    
    container3.add(TextElement("label3", "Tell us about your experience:"))
    
    experience_input = MultiLineInput("experience")
    experience_input.set_placeholder("Describe your relevant experience...")
    container3.add(TextElement("exp_label", "Experience:"))
    container3.add(experience_input)
    
    skills_input = SingleLineInput("skills")
    skills_input.set_placeholder("Python, JavaScript, Design, etc.")
    container3.add(TextElement("skills_label", "Skills:"))
    container3.add(skills_input)
    
    containers.append(container3)
    
    # Container 4: Goals
    container4 = Container("goals")
    container4.set_title("Goals & Objectives").set_border(True)
    
    container4.add(TextElement("label4", "What are your goals?"))
    
    goals_input = MultiLineInput("goals")
    goals_input.set_placeholder("Describe your goals and objectives...")
    container4.add(TextElement("goals_label", "Primary Goals:"))
    container4.add(goals_input)
    
    timeline_input = SingleLineInput("timeline")
    timeline_input.set_placeholder("6 months, 1 year, 2 years, etc.")
    container4.add(TextElement("timeline_label", "Timeline:"))
    container4.add(timeline_input)
    
    containers.append(container4)
    
    # Container 5: Review
    container5 = Container("review")
    container5.set_title("Review & Submit").set_border(True)
    
    container5.add(TextElement("label5", "Review your information before submitting:"))
    container5.add(TextElement("review_text", "All previous data will be displayed here for review."))
    container5.add(TextElement("review_note", "Use the Save button in the footer to submit your data."))
    
    containers.append(container5)
    
    return containers


def create_card_swap_page() -> tuple[Page, CardSwapDemo, callable, callable]:
    """Create the card swapping demo page with all its components."""
    demo = CardSwapDemo()
    page = Page("Card Swapping Demo")
    
    # Button references - will be set when buttons are created
    prev_btn = None
    next_btn = None
    save_btn = None
    close_btn = None
    
    def update_button_visibility_impl():
        """Update button visibility based on validation state and current position."""
        if not prev_btn or not next_btn or not save_btn or not close_btn:
            return  # Buttons not created yet
            
        # Previous button: invisible on first card
        prev_btn.visible = (demo.current_container > 0)
        
        # Next button: invisible if current card is invalid or we're on last card
        current_card_valid = demo.is_card_valid(demo.current_container)
        is_last_card = (demo.current_container >= demo.total_containers - 1)
        next_btn.visible = current_card_valid and not is_last_card
        
        # Save button: only visible if all cards are valid
        save_btn.visible = demo.are_all_cards_valid()
        
        # Close button: always visible
        close_btn.visible = True
        
        # Rebuild layout to reflect visibility changes
        try:
            from prompt_toolkit.application import get_app
            app = get_app()
            if app:
                new_layout = page.to_prompt_toolkit_layout()
                app.layout = new_layout
                app.invalidate()
        except Exception:
            pass
    
    # Title Section
    title_container = page.title_section_container("title")
    title_container.set_title("Card Swapping Demo").set_border(False)  # Remove border - title centering is now working
    
    # Remove border from the title section itself
    if page.title_section:
        page.title_section.set_border(False)
    
    title_text = TextElement("demo_title", "🚀 Card Swapping Demo 🚀")
    title_text.set_style("title")  # Apply title styling
    title_container.add(title_text)
    
    # Set the title container to take full width and center content
    title_container.set_layout_direction("horizontal")  # This might help with width
    title_container.set_align("center")  # Center the title
    
    # Header Section - Navigation Instructions
    header_container = page.header_section_container("header")
    header_container.set_title("Navigation").set_border(False)  # Remove border
    
    # Remove border from the header section itself
    if page.header_section:
        page.header_section.set_border(False)
    
    instructions = TextElement("instructions", "• Use Tab to focus next, Shift+Tab to focus previous.\n• Enter to commit value.\n• Ctrl+C to exit.")
    instructions.set_style("info")  # Apply info styling
    current_position = DynamicTextElement("position", demo.get_container_info())
    current_position.set_style("status")  # Apply status styling
    
    # Add spacing around navigation instructions
    header_container.add(TextElement("spacer_before", ""))  # Blank line above
    header_container.add(instructions)
    header_container.add(TextElement("spacer_after", ""))   # Blank line below
    header_container.add(current_position)
    
    # Body Section - Data Collection Containers
    body_container = page.body_section
    
    # Create all 5 containers and add them all to the body
    data_containers = create_data_containers(demo)
    
    # Add all containers to the body
    for container in data_containers:
        body_container.add(container)
    
    # Create navigation container - always visible under the cards
    nav_container = Container("navigation")
    nav_container.set_title("Navigation").set_border(False)  # Borderless navigation
    nav_container.set_layout_direction("horizontal")
    nav_container.set_align("center")  # Center the navigation buttons
    nav_container.visible = True  # Always visible
    body_container.add(nav_container)
    
    def update_container_visibility():
        """Update which container is visible based on current_container."""
        # Show only the current container, hide all others
        for i, container in enumerate(data_containers):
            container.visible = (i == demo.current_container)
        
        # Navigation container always stays visible
        nav_container.visible = True
    
    # Set initial visibility - only first container visible
    update_container_visibility()
    
    # Footer Section - Status Messages
    footer_container = page.footer_section_container("footer")
    footer_container.set_layout_direction("horizontal")
    footer_container.set_border(False)  # Remove border from footer container
    
    # Remove border from the footer section itself
    if page.footer_section:
        page.footer_section.set_border(False)
    
    # Remove border from the body section
    page.body_section.set_border(False)
    
    # Navigation status - now in footer
    nav_status = DynamicTextElement("nav_status", "")
    nav_status.set_style("status")  # Apply status styling
    footer_container.add(nav_status)
    
    def collect_all_data() -> dict:
        """Collect data from all containers."""
        all_data = {}
        for container in data_containers:
            for child in container.children:
                if hasattr(child, 'get_text') and hasattr(child, 'name'):
                    # This is an input component
                    value = child.get_text()
                    if value:  # Only save non-empty values
                        all_data[child.name] = value
                elif hasattr(child, 'get_selected_value') and hasattr(child, 'name'):
                    # This is a radio button group
                    value = child.get_selected_value()
                    if value:
                        all_data[child.name] = value
        return all_data
    
    def save_results(btn):
        """Save all collected data."""
        data = collect_all_data()
        if data:
            output_file = demo.save_data(data)
            nav_status.set_text(f"✅ Data saved to {output_file.name}")
            print(f"Data saved to: {output_file}")
            print("Saved data:")
            print(json.dumps(data, indent=2))
        else:
            nav_status.set_text("⚠️ No data to save")
    
    def close_app(btn):
        """Close the application."""
        print("Closing Card Swapping Demo...")
        sys.exit(0)
    
    def validate_current_card() -> bool:
        """Validate all components in the current card and update tracking."""
        current_components = demo.get_card_components(demo.current_container)
        all_valid = True
        
        for container in data_containers:
            if container.visible:
                for child in container.children:
                    if hasattr(child, 'name') and child.name in current_components:
                        # Mark as touched since user is trying to navigate
                        demo.mark_component_touched(child.name)
                        
                        # Validate the component
                        if hasattr(child, 'validate'):
                            errors = child.validate()
                            is_valid = len(errors) == 0
                            demo.set_component_valid(child.name, is_valid)
                            if not is_valid:
                                all_valid = False
                        elif hasattr(child, 'get_text'):
                            # For input components, get current value and validate
                            current_value = child.get_text() or ""
                            if child.name == "project_name":
                                error = validate_project_name(current_value)
                                is_valid = len(error) == 0
                                demo.set_component_valid(child.name, is_valid)
                                if not is_valid:
                                    all_valid = False
                            elif child.name == "version_tag":
                                error = validate_version_tag(current_value)
                                is_valid = len(error) == 0
                                demo.set_component_valid(child.name, is_valid)
                                if not is_valid:
                                    all_valid = False
        
        return all_valid
    
    # Navigation functions for keyboard handling
    def navigate_up():
        """Navigate to previous container."""
        success = demo.previous_container()
        if success:
            update_container_visibility()  # Update which container is visible
            nav_status.set_text(f"⬆️ Moved to {demo.get_container_info()}")
            update_button_visibility_impl()  # Update buttons after navigation
            # Rebuild and reassign the layout to make visibility changes take effect
            try:
                from prompt_toolkit.application import get_app
                app = get_app()
                new_layout = page.to_prompt_toolkit_layout()
                app.layout = new_layout
                app.invalidate()
            except Exception:
                pass  # Ignore errors silently
        else:
            nav_status.set_text("⚠️ Already at first container")
    
    def navigate_down():
        """Navigate to next container."""
        # First validate the current card
        if not validate_current_card():
            nav_status.set_text("⚠️ Please fix validation errors before proceeding")
            update_button_visibility_impl()
            return
            
        success = demo.next_container()
        if success:
            update_container_visibility()  # Update which container is visible
            nav_status.set_text(f"⬇️ Moved to {demo.get_container_info()}")
            update_button_visibility_impl()  # Update buttons after navigation
            # Rebuild and reassign the layout to make visibility changes take effect
            try:
                from prompt_toolkit.application import get_app
                app = get_app()
                new_layout = page.to_prompt_toolkit_layout()
                app.layout = new_layout
                app.invalidate()
            except Exception:
                pass  # Ignore errors silently
        else:
            nav_status.set_text("⚠️ Already at last container")
    
    # Button handlers that call navigation functions directly
    def button_navigate_up(btn):
        """Button handler for previous container."""
        navigate_up()
        # Rebuild and reassign the layout like keyboard navigation does
        try:
            from prompt_toolkit.application import get_app
            app = get_app()
            new_layout = page.to_prompt_toolkit_layout()
            app.layout = new_layout
            app.invalidate()
        except Exception:
            pass  # Ignore errors silently
    
    def button_navigate_down(btn):
        """Button handler for next container.""" 
        navigate_down()
        # Rebuild and reassign the layout like keyboard navigation does
        try:
            from prompt_toolkit.application import get_app
            app = get_app()
            new_layout = page.to_prompt_toolkit_layout()
            app.layout = new_layout
            app.invalidate()
        except Exception:
            pass  # Ignore errors silently
    
    # Create footer buttons
    save_btn = Buttons.save("save_results", save_results)
    save_btn.set_text("[ 💾  Save ]")
    save_btn.set_symbols("", "")  # Remove default symbols since we include them in text
    
    close_btn = Buttons.close("close_app", close_app)
    close_btn.set_text("[ 🚪  Close ]")
    close_btn.set_symbols("", "")  # Remove default symbols since we include them in text
    
    # Navigation buttons that trigger keyboard events
    prev_btn = Buttons.cancel("prev_container", button_navigate_up)
    prev_btn.set_text("[ ⬆️  Previous ]")
    prev_btn.set_symbols("", "")  # Remove default symbols since we include them in text
    
    next_btn = Buttons.ok("next_container", button_navigate_down) 
    next_btn.set_text("[ ⬇️  Next ]")
    next_btn.set_symbols("", "")  # Remove default symbols since we include them in text
    
    # Add buttons to navigation container (in body) - status messages moved to footer
    nav_container.add(prev_btn)
    nav_container.add(next_btn)
    nav_container.add(save_btn)
    nav_container.add(close_btn)
    
    # Set initial visibility - only first container visible
    update_container_visibility()
    
    # Set initial button visibility based on validation state
    update_button_visibility_impl()
    
    # Footer now contains status messages while body contains navigation buttons
    # footer_container already has nav_status added above
    
    # Store navigation functions on the page for potential keyboard handling
    page._navigate_up = navigate_up
    page._navigate_down = navigate_down
    
    return page, demo, navigate_up, navigate_down
def main():
    """Main function to run the card swapping demo."""
    print("🚀 Starting Card Swapping Demo - TUI Engine Architecture")
    print("=" * 60)
    
    # Create the application and demo page
    app = App()
    
    # Add title styling
    app.set_style({
        "frame.border": "fg:#00aaff",
        "frame.label": "fg:#00aaff", 
        "title": "bg:#1e88e5 fg:#ffffff bold nounderline",  # Blue background, white text, bold
        "info": "fg:#2196f3 italic",  # Blue text, italic for instructions
        "status": "bg:#e3f2fd fg:#0d47a1 bold",  # Light blue background, dark blue text for status
    })
    
    demo_page, demo, navigate_up_func, navigate_down_func = create_card_swap_page()
    app.add_page("demo", demo_page)
    
    # PgUp/PgDn navigation disabled - using validation-based navigation instead
    # @app.key_bindings.add("pageup", eager=True)
    # def _(event):
    #     navigate_up_func()
    #     # Rebuild the entire layout (needed for navigation to work)
    #     new_layout = demo_page.to_prompt_toolkit_layout()
    #     event.app.layout = new_layout
    #     event.app.invalidate()
    
    # @app.key_bindings.add("pagedown", eager=True) 
    # def _(event):
    #     navigate_down_func()
    #     # Rebuild the entire layout (needed for navigation to work)
    #     new_layout = demo_page.to_prompt_toolkit_layout()
    #     event.app.layout = new_layout
    #     event.app.invalidate()
    
    print("📋 Card Swapping Demo Features:")
    print("  • Single page with 4 sections (title, header, body, footer)")
    print("  • 5 data collection containers (one visible at a time)")
    print("  • Navigation between containers")
    print("  • Data collection and saving functionality")
    print("  • Clean section-based architecture")
    print()
    
    # Show the demo layout
    print("🎮 Demo Layout:")
    print("-" * 40)
    content = demo_page.render()
    
    for i, line in enumerate(content):
        print(f"  {line}")
        if i > 25:  # Limit output for readability
            print(f"  ... ({len(content) - i - 1} more lines)")
            break
    
    print(f"\n✅ Card Swapping Demo Ready!")
    print(f"📊 Current container: {demo.get_container_info()}")
    print(f"� Navigation: Use Previous/Next buttons (PgUp/PgDn simulation)")
    print(f"💾 Data saving: Use Save button to export collected data")
    print(f"🚪 Exit: Use Close button or CTRL+C")
    
    # NOTE: App class integration is now fixed!
    # Interactive mode enabled with working navigation:
    app.run()
    
    print(f"\n💡 Thanks for trying the interactive demo!")
    print(f"📋 You have exited interactive mode")


if __name__ == "__main__":
    main()
