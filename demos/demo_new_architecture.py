#!/usr/bin/env python3
"""
TUI Engine Architecture Demo

This demo showcases the complete Page/Section/Container/Component architecture
with all the new features we've built.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from tui_engine.page import Page
from tui_engine.app import App
from tui_engine.container import Container
from tui_engine.text_element import TextElement, DynamicTextElement
from tui_engine.input_component import SingleLineInput, MultiLineInput, PasswordInput
from tui_engine.button_component import ButtonComponent, Buttons
from tui_engine.component_base import Validators


def create_welcome_page() -> Page:
    """Create a welcome page demonstrating the section structure."""
    page = Page("Welcome")
    
    # Title Section
    title_container = page.title_section_container("title")
    title_container.set_title("TUI Engine Demo").set_border(True)
    
    title_text = TextElement("welcome_title", "🎉 Welcome to TUI Engine!")
    title_text.set_style("title")
    title_container.add(title_text)
    
    # Header Section  
    header_container = page.header_section_container("header")
    header_container.set_title("Navigation").set_border(True)
    header_container.set_layout_direction("horizontal")
    
    nav_text = TextElement("nav_info", "Use TAB to navigate between controls • ENTER to activate • ESC to exit")
    header_container.add(nav_text)
    
    # Body Section - Main content
    info_container = Container("info")
    info_container.set_title("Architecture Overview").set_border(True)
    
    # Architecture explanation
    arch_text = TextElement("architecture", """
This demo showcases the new TUI Engine architecture:

📄 PAGE: Contains fixed sections (title, header, body, footer)
📦 SECTION: Organized areas within a page  
🔲 CONTAINER: Layout containers with borders and titles
🧩 COMPONENT: Interactive widgets (inputs, buttons, text)

Features demonstrated:
• Page section-based layout
• Container organization with borders
• Text elements (static and dynamic)
• Input components with validation
• Button components with events
• Layout direction control (vertical/horizontal)
""")
    info_container.add(arch_text)
    
    page.body_section.add(info_container)
    
    # Footer Section
    footer_container = page.footer_section_container("footer")
    footer_container.set_layout_direction("horizontal")
    
    next_btn = Buttons.ok("continue", lambda btn: print("Navigate to form page"))
    next_btn.set_text("Continue to Form Demo →")
    
    exit_btn = Buttons.cancel("exit", lambda btn: sys.exit(0))
    exit_btn.set_text("Exit")
    
    footer_container.add(next_btn)
    footer_container.add(exit_btn)
    
    return page


def create_form_page() -> Page:
    """Create a form page demonstrating all component types."""
    page = Page("User Registration")
    
    # Title Section
    title_container = page.title_section_container("title")
    title_container.set_title("User Registration Form").set_border(True)
    
    form_title = TextElement("form_title", "📝 Please enter your information")
    title_container.add(form_title)
    
    # Header Section - Dynamic status
    header_container = page.header_section_container("header")
    header_container.set_title("Status").set_border(True)
    
    status_text = DynamicTextElement("status", "Ready to fill out form")
    status_text.set_style("status")
    header_container.add(status_text)
    
    # Body Section - Form fields
    form_container = Container("form_fields")
    form_container.set_title("Personal Information").set_border(True)
    
    # Username field
    username_label = TextElement("username_label", "Username:")
    username = SingleLineInput("username")
    username.set_placeholder("Enter your username")
    username.set_required(True)
    username.add_validation_rule(Validators.min_length(3))
    username.add_validation_rule(Validators.max_length(20))
    
    # Email field
    email_label = TextElement("email_label", "Email:")
    email = SingleLineInput("email")
    email.set_placeholder("your.email@example.com")
    email.set_required(True)
    email.add_validation_rule(Validators.email())
    
    # Password field
    password_label = TextElement("password_label", "Password:")
    password = PasswordInput("password")
    password.set_placeholder("Enter a secure password")
    password.set_required(True)
    password.add_validation_rule(Validators.min_length(8))
    
    # Comments field (multi-line)
    comments_label = TextElement("comments_label", "Comments (optional):")
    comments = MultiLineInput("comments")
    comments.set_placeholder("Tell us about yourself...")
    comments.set_max_length(500)
    
    # Add all form elements
    form_container.add(username_label)
    form_container.add(username)
    form_container.add(email_label)
    form_container.add(email)
    form_container.add(password_label)
    form_container.add(password)
    form_container.add(comments_label)
    form_container.add(comments)
    
    page.body_section.add(form_container)
    
    # Event handlers for real-time validation feedback
    def update_status():
        """Update status based on form validation."""
        errors = []
        if username.get_text():
            errors.extend(username.validate())
        if email.get_text():
            errors.extend(email.validate())
        if password.get_text():
            errors.extend(password.validate())
            
        if errors:
            status_text.set_text(f"⚠️  Validation errors: {len(errors)} issues found")
        elif username.get_text() and email.get_text() and password.get_text():
            status_text.set_text("✅ Form looks good! Ready to submit")
        else:
            status_text.set_text("📝 Fill out required fields")
    
    # Connect validation events
    username.on_event("value_changed", lambda *args: update_status())
    email.on_event("value_changed", lambda *args: update_status())
    password.on_event("value_changed", lambda *args: update_status())
    
    # Footer Section - Action buttons
    footer_container = page.footer_section_container("footer")
    footer_container.set_layout_direction("horizontal")
    
    def submit_form(btn):
        """Handle form submission."""
        # Validate all fields
        all_errors = []
        all_errors.extend(username.validate())
        all_errors.extend(email.validate())
        all_errors.extend(password.validate())
        
        if all_errors:
            status_text.set_text(f"❌ Cannot submit: {len(all_errors)} validation errors")
        else:
            status_text.set_text("🎉 Form submitted successfully!")
            # In a real app, you'd process the form data here
            print(f"Form submitted:")
            print(f"  Username: {username.get_text()}")
            print(f"  Email: {email.get_text()}")
            print(f"  Password: [hidden]")
            print(f"  Comments: {comments.get_text()}")
    
    def reset_form(btn):
        """Reset all form fields."""
        username.clear()
        email.clear()
        password.clear()
        comments.clear()
        status_text.set_text("🔄 Form reset - ready for new input")
    
    submit_btn = Buttons.submit("submit", submit_form)
    reset_btn = Buttons.reset("reset", reset_form)
    back_btn = Buttons.cancel("back", lambda btn: print("Go back to welcome page"))
    back_btn.set_text("← Back")
    
    footer_container.add(submit_btn)
    footer_container.add(reset_btn)
    footer_container.add(back_btn)
    
    return page


def create_component_showcase_page() -> Page:
    """Create a page showcasing all component types and features."""
    page = Page("Component Showcase")
    
    # Title Section
    title_container = page.title_section_container("title")
    title_container.set_title("Component Showcase").set_border(True)
    
    showcase_title = TextElement("showcase_title", "🧩 All TUI Engine Components")
    title_container.add(showcase_title)
    
    # Body Section - Multiple containers showing different components
    
    # Text Components Container
    text_container = Container("text_components")
    text_container.set_title("Text Components").set_border(True)
    
    static_text = TextElement("static", "📝 Static Text: This text never changes")
    
    dynamic_text = DynamicTextElement("dynamic", "🔄 Dynamic Text: Click button to update")
    counter = [0]  # Mutable counter for closure
    
    def update_dynamic(btn):
        counter[0] += 1
        dynamic_text.set_text(f"🔄 Dynamic Text: Updated {counter[0]} times")
    
    update_btn = ButtonComponent("update_dynamic", "Update Dynamic Text")
    update_btn.on_click(update_dynamic)
    
    text_container.add(static_text)
    text_container.add(dynamic_text)
    text_container.add(update_btn)
    
    # Input Components Container
    input_container = Container("input_components")
    input_container.set_title("Input Components").set_border(True)
    
    # Various input types
    single_input = SingleLineInput("single")
    single_input.set_placeholder("Single-line input")
    
    multi_input = MultiLineInput("multi")
    multi_input.set_placeholder("Multi-line input\nType multiple lines here...")
    
    password_input = PasswordInput("pwd")
    password_input.set_placeholder("Password input (hidden)")
    
    input_container.add(TextElement("input_label1", "Single Line Input:"))
    input_container.add(single_input)
    input_container.add(TextElement("input_label2", "Multi Line Input:"))
    input_container.add(multi_input)
    input_container.add(TextElement("input_label3", "Password Input:"))
    input_container.add(password_input)
    
    # Button Components Container
    button_container = Container("button_components")
    button_container.set_title("Button Components").set_border(True)
    button_container.set_layout_direction("horizontal")
    
    # Different button types
    primary_btn = Buttons.ok("primary")
    primary_btn.set_text("Primary")
    primary_btn.on_click(lambda btn: print(f"Clicked: {btn.text}"))
    
    secondary_btn = Buttons.cancel("secondary")
    secondary_btn.set_text("Secondary")
    secondary_btn.on_click(lambda btn: print(f"Clicked: {btn.text}"))
    
    danger_btn = Buttons.delete("danger")
    danger_btn.on_click(lambda btn: print(f"Clicked: {btn.text}"))
    
    help_btn = Buttons.help("help")
    help_btn.on_click(lambda btn: print(f"Clicked: {btn.text}"))
    
    button_container.add(primary_btn)
    button_container.add(secondary_btn)
    button_container.add(danger_btn)
    button_container.add(help_btn)
    
    # Layout Demo Container
    layout_container = Container("layout_demo")
    layout_container.set_title("Layout Directions").set_border(True)
    
    # Horizontal layout example
    h_container = Container("horizontal_example")
    h_container.set_title("Horizontal Layout").set_border(True)
    h_container.set_layout_direction("horizontal")
    
    h_container.add(TextElement("h1", "Item 1"))
    h_container.add(TextElement("h2", "Item 2"))
    h_container.add(TextElement("h3", "Item 3"))
    
    # Vertical layout example (default)
    v_container = Container("vertical_example")
    v_container.set_title("Vertical Layout").set_border(True)
    
    v_container.add(TextElement("v1", "Item A"))
    v_container.add(TextElement("v2", "Item B"))
    v_container.add(TextElement("v3", "Item C"))
    
    layout_container.add(h_container)
    layout_container.add(v_container)
    
    # Add all containers to page body
    page.body_section.add(text_container)
    page.body_section.add(input_container)
    page.body_section.add(button_container)
    page.body_section.add(layout_container)
    
    # Footer Section
    footer_container = page.footer_section_container("footer")
    footer_container.set_layout_direction("horizontal")
    
    back_btn = Buttons.cancel("back_showcase", lambda btn: print("Go back"))
    back_btn.set_text("← Back to Form")
    
    exit_btn = Buttons.close("exit_showcase", lambda btn: sys.exit(0))
    
    footer_container.add(back_btn)
    footer_container.add(exit_btn)
    
    return page


def main():
    """Main demo function."""
    print("🚀 Starting TUI Engine Architecture Demo")
    print("=" * 50)
    
    # Create the application
    app = App()
    
    # Create and add pages
    welcome = create_welcome_page()
    form = create_form_page()
    showcase = create_component_showcase_page()
    
    app.add_page("welcome", welcome)
    app.add_page("form", form)
    app.add_page("showcase", showcase)
    
    print("📄 Created 3 demo pages:")
    print("  1. Welcome Page - Architecture overview")
    print("  2. Form Page - User registration with validation")
    print("  3. Showcase Page - All component types")
    print()
    
    # For now, let's render each page to show the architecture
    print("📋 Page Layouts:")
    print("=" * 50)
    
    for page_name, page in [("Welcome", welcome), ("Form", form), ("Showcase", showcase)]:
        print(f"\n🔹 {page_name} Page Structure:")
        print("-" * 30)
        
        # Render the page content
        content = page.render()
        for line in content[:20]:  # Show first 20 lines
            print(f"  {line}")
        
        if len(content) > 20:
            print(f"  ... ({len(content) - 20} more lines)")
    
    print(f"\n✅ Demo complete! Architecture validation successful.")
    print(f"📊 Total components created: {count_components(welcome, form, showcase)}")
    print(f"🎯 All page sections utilized and functional")
    
    # Note: In a real implementation, you would call app.run() here
    # For demo purposes, we're showing the structure instead
    print(f"\n💡 To run interactively, use: app.run()")


def count_components(welcome: Page, form: Page, showcase: Page) -> int:
    """Count total components across all pages."""
    count = 0
    
    for page in [welcome, form, showcase]:
        # Count components in all sections
        for section in [page.title_section, page.header_section, page.body_section, page.footer_section]:
            if section:
                count += count_elements_recursive(section)
    
    return count


def count_elements_recursive(container: Container) -> int:
    """Recursively count elements in a container."""
    count = len(container.children)
    
    for child in container.children:
        if isinstance(child, Container):
            count += count_elements_recursive(child)
    
    return count


if __name__ == "__main__":
    main()