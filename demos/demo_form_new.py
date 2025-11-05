#!/usr/bin/env python3
"""
Refactored Form Demo - Using New TUI Engine Architecture

This demo shows how to migrate from the old architecture to the new
Page/Section/Container/Component system.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
from pathlib import Path
from typing import Any, Dict

# New architecture imports
from tui_engine.page import Page
from tui_engine.app import App
from tui_engine.container import Container
from tui_engine.text_element import TextElement, DynamicTextElement
from tui_engine.input_component import SingleLineInput, MultiLineInput
from tui_engine.button_component import Buttons
from tui_engine.component_base import Validators


def create_form_page() -> Page:
    """Create a comprehensive form using the new architecture."""
    page = Page("User Information Form")
    
    # Title Section
    title_container = page.title_section_container("title")
    title_container.set_title("User Registration").set_border(True)
    
    title_text = TextElement("form_title", "📝 Please fill out your information")
    title_container.add(title_text)
    
    # Header Section - Instructions
    header_container = page.header_section_container("header")
    header_container.set_title("Instructions").set_border(True)
    
    instructions = TextElement("instructions", "Fill out all required fields marked with (*)")
    header_container.add(instructions)
    
    # Body Section - Form fields organized in containers
    
    # Personal Information Section
    personal_container = Container("personal_info")
    personal_container.set_title("Personal Information").set_border(True)
    
    # First Name
    fname_label = TextElement("fname_label", "First Name: *")
    first_name = SingleLineInput("first_name")
    first_name.set_placeholder("Enter your first name")
    first_name.set_required(True)
    first_name.add_validation_rule(Validators.min_length(2))
    
    # Last Name
    lname_label = TextElement("lname_label", "Last Name: *")
    last_name = SingleLineInput("last_name")
    last_name.set_placeholder("Enter your last name")
    last_name.set_required(True)
    last_name.add_validation_rule(Validators.min_length(2))
    
    # Age
    age_label = TextElement("age_label", "Age: *")
    age = SingleLineInput("age")
    age.set_placeholder("Enter your age")
    age.set_required(True)
    age.add_validation_rule(Validators.numeric())
    age.add_validation_rule(Validators.range_check(13, 120))
    
    personal_container.add(fname_label)
    personal_container.add(first_name)
    personal_container.add(lname_label)
    personal_container.add(last_name)
    personal_container.add(age_label)
    personal_container.add(age)
    
    # Contact Information Section
    contact_container = Container("contact_info")
    contact_container.set_title("Contact Information").set_border(True)
    
    # Email
    email_label = TextElement("email_label", "Email Address: *")
    email = SingleLineInput("email")
    email.set_placeholder("your.email@example.com")
    email.set_required(True)
    email.add_validation_rule(Validators.email())
    
    # Phone
    phone_label = TextElement("phone_label", "Phone Number:")
    phone = SingleLineInput("phone")
    phone.set_placeholder("(555) 123-4567")
    phone.add_validation_rule(Validators.min_length(10))
    
    contact_container.add(email_label)
    contact_container.add(email)
    contact_container.add(phone_label)
    contact_container.add(phone)
    
    # Additional Information Section
    additional_container = Container("additional_info")
    additional_container.set_title("Additional Information").set_border(True)
    
    # Bio
    bio_label = TextElement("bio_label", "Bio (optional):")
    bio = MultiLineInput("bio")
    bio.set_placeholder("Tell us about yourself...")
    bio.set_max_length(500)
    
    # Interests
    interests_label = TextElement("interests_label", "Interests:")
    interests = SingleLineInput("interests")
    interests.set_placeholder("Programming, music, sports...")
    
    additional_container.add(bio_label)
    additional_container.add(bio)
    additional_container.add(interests_label)
    additional_container.add(interests)
    
    # Add all containers to the page body
    page.body_section.add(personal_container)
    page.body_section.add(contact_container)
    page.body_section.add(additional_container)
    
    # Footer Section - Form status and actions
    footer_container = page.footer_section_container("footer")
    footer_container.set_layout_direction("horizontal")
    
    # Status display
    status_text = DynamicTextElement("status", "📝 Please fill out the required fields")
    
    # Collect all form fields for validation
    form_fields = {
        'first_name': first_name,
        'last_name': last_name,
        'age': age,
        'email': email,
        'phone': phone,
        'bio': bio,
        'interests': interests
    }
    
    def update_form_status():
        """Update the form status based on validation."""
        errors = []
        for field_name, field in form_fields.items():
            if hasattr(field, 'validate'):
                field_errors = field.validate()
                errors.extend(field_errors)
        
        if not errors:
            status_text.set_text("✅ Form is ready to submit!")
        else:
            required_errors = len([e for e in errors if 'required' in e.lower()])
            validation_errors = len(errors) - required_errors
            
            if required_errors > 0:
                status_text.set_text(f"⚠️  {required_errors} required fields missing")
            elif validation_errors > 0:
                status_text.set_text(f"⚠️  {validation_errors} validation errors")
    
    # Connect status updates to field changes
    for field in form_fields.values():
        if hasattr(field, 'on_event'):
            field.on_event("value_changed", lambda *args: update_form_status())
    
    def save_form(btn):
        """Save the form data to JSON file."""
        # Validate all fields
        all_errors = []
        for field in form_fields.values():
            if hasattr(field, 'validate'):
                all_errors.extend(field.validate())
        
        if all_errors:
            status_text.set_text(f"❌ Cannot save: {len(all_errors)} validation errors")
            return
        
        # Collect form data
        form_data = {}
        for field_name, field in form_fields.items():
            if hasattr(field, 'get_text'):
                form_data[field_name] = field.get_text()
            else:
                form_data[field_name] = field.current_value or ""
        
        # Save to file
        output_file = Path(__file__).parent / "form_output.json"
        with open(output_file, 'w') as f:
            json.dump(form_data, f, indent=2)
        
        status_text.set_text(f"💾 Form saved to {output_file.name}")
        print(f"Form data saved to: {output_file}")
        print("Form contents:")
        print(json.dumps(form_data, indent=2))
    
    def reset_form(btn):
        """Reset all form fields."""
        for field in form_fields.values():
            if hasattr(field, 'clear'):
                field.clear()
            else:
                field.set_value("")
        status_text.set_text("🔄 Form reset - ready for new input")
    
    def exit_form(btn):
        """Exit the form."""
        print("Exiting form demo...")
        sys.exit(0)
    
    # Create action buttons
    save_btn = Buttons.save("save_form", save_form)
    reset_btn = Buttons.reset("reset_form", reset_form)
    exit_btn = Buttons.cancel("exit_form", exit_form)
    exit_btn.set_text("Exit")
    
    # Add status and buttons to footer
    footer_container.add(status_text)
    footer_container.add(save_btn)
    footer_container.add(reset_btn)
    footer_container.add(exit_btn)
    
    return page


def main():
    """Main demo function."""
    print("🚀 TUI Engine Form Demo - New Architecture")
    print("=" * 50)
    
    # Create the application and form page
    app = App()
    form_page = create_form_page()
    app.add_page("form", form_page)
    
    print("📋 Form Structure:")
    print("-" * 30)
    
    # Render the form to show its structure
    content = form_page.render()
    
    # Show the form layout
    for i, line in enumerate(content):
        print(f"  {line}")
        if i > 50:  # Limit output for readability
            print(f"  ... ({len(content) - i - 1} more lines)")
            break
    
    print(f"\n✅ Form demo complete!")
    print(f"📊 Form contains {count_form_components(form_page)} components")
    print(f"💾 Form data will be saved to 'form_output.json'")
    print(f"🎯 All form sections properly organized")
    
    # In a real implementation, you would call:
    # app.run()
    
    print(f"\n💡 To run interactively, uncomment: app.run()")


def count_form_components(page: Page) -> int:
    """Count the total number of components in the form."""
    count = 0
    
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