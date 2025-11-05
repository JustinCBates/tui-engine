"""
Integration tests for the TUI Engine architecture.

These tests validate the complete Page→Section→Container→Component flow
and ensure all components work correctly with prompt-toolkit rendering.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from prompt_toolkit.widgets import Frame, TextArea, Button, Label
from prompt_toolkit.layout import HSplit, VSplit

# Import our TUI Engine components
from tui_engine.page import Page
from tui_engine.app import App
from tui_engine.container import Container
from tui_engine.text_element import TextElement, DynamicTextElement
from tui_engine.input_component import InputComponent, SingleLineInput, PasswordInput
from tui_engine.button_component import ButtonComponent, Buttons
from tui_engine.component_base import Validators


class TestPageSectionArchitecture:
    """Test the core Page and Section architecture."""
    
    def test_page_creation_and_sections(self):
        """Test that pages create proper section structure."""
        page = Page("test_page")
        
        # Initially sections are None or auto-created
        assert page.body_section is not None  # Body is always created
        
        # Sections are created on-demand when accessed via container methods
        title_container = page.title_section_container("title")
        header_container = page.header_section_container("header") 
        footer_container = page.footer_section_container("footer")
        
        # Now sections should exist
        assert page.title_section is not None
        assert page.header_section is not None
        assert page.footer_section is not None
        
        # Verify sections are Containers
        assert isinstance(page.title_section, Container)
        assert isinstance(page.header_section, Container)
        assert isinstance(page.body_section, Container)
        assert isinstance(page.footer_section, Container)
    
    def test_page_section_configuration(self):
        """Test that page sections can be configured properly."""
        page = Page("config_test")
        
        # Create sections by accessing them
        page.title_section_container("title")
        page.header_section_container("header")
        
        # Configure sections
        page.title_section.set_title("Page Title").set_border(True)
        page.header_section.set_title("Header").set_layout_direction("horizontal")
        page.body_section.set_layout_direction("vertical")
        page.footer_section_container("footer").parent.set_border(False)
        
        # Verify configurations
        assert page.title_section.title == "Page Title"
        assert page.title_section.show_border == True
        assert page.header_section.layout_hint == "horizontal"
        assert page.body_section.layout_hint == "vertical"
        assert page.footer_section.show_border == False
    
    def test_page_prompt_toolkit_layout(self):
        """Test that pages generate proper prompt-toolkit layouts."""
        page = Page("layout_test")
        
        # Add some content to sections
        title_container = page.title_section_container("title")
        title_text = TextElement("title", "Test Page")
        title_container.add(title_text)
        
        # Generate prompt-toolkit layout
        layout = page.to_prompt_toolkit_layout()
        
        # Should be a Layout object
        from prompt_toolkit.layout import Layout
        assert isinstance(layout, Layout)


class TestContainerIntegration:
    """Test Container integration with prompt-toolkit."""
    
    def test_container_prompt_toolkit_conversion(self):
        """Test container conversion to prompt-toolkit widgets."""
        container = Container("test_container")
        container.set_title("Test Container").set_border(True)
        
        # Add some elements
        text = TextElement("text", "Hello World")
        container.add(text)
        
        # Convert to prompt-toolkit
        ptk_widget = container.to_prompt_toolkit()
        
        # Should be a Frame widget
        assert isinstance(ptk_widget, Frame)
        assert ptk_widget.title == "Test Container"
    
    def test_container_layout_directions(self):
        """Test horizontal and vertical layout directions."""
        # Test vertical layout (default)
        v_container = Container("vertical")
        text1 = TextElement("text1", "Line 1")
        text2 = TextElement("text2", "Line 2")
        v_container.add(text1).add(text2)
        
        v_widget = v_container.to_prompt_toolkit()
        # Should contain a HSplit for vertical layout
        assert isinstance(v_widget.body, HSplit)
        
        # Test horizontal layout
        h_container = Container("horizontal")
        h_container.set_layout_direction("horizontal")
        h_container.add(text1).add(text2)
        
        h_widget = h_container.to_prompt_toolkit()
        # Should contain a VSplit for horizontal layout
        assert isinstance(h_widget.body, VSplit)
    
    def test_nested_containers(self):
        """Test containers nested within other containers."""
        root = Container("root")
        child1 = Container("child1")
        child2 = Container("child2")
        
        # Add text to children
        child1.add(TextElement("text1", "Child 1 Text"))
        child2.add(TextElement("text2", "Child 2 Text"))
        
        # Nest children in root
        root.add(child1).add(child2)
        
        # Convert to prompt-toolkit
        root_widget = root.to_prompt_toolkit()
        
        # Should be properly nested
        assert isinstance(root_widget, Frame)
        assert isinstance(root_widget.body, HSplit)  # Default vertical layout
        assert len(root_widget.body.children) == 2


class TestTextElementIntegration:
    """Test TextElement and DynamicTextElement integration."""
    
    def test_text_element_prompt_toolkit(self):
        """Test TextElement conversion to prompt-toolkit Label."""
        text = TextElement("test_text", "Hello, World!")
        text.set_style("bold")
        
        # Convert to prompt-toolkit
        ptk_widget = text.to_prompt_toolkit()
        
        # Should be a Label widget
        assert isinstance(ptk_widget, Label)
    
    def test_dynamic_text_element_events(self):
        """Test DynamicTextElement event handling."""
        dynamic_text = DynamicTextElement("dynamic", "Initial")
        
        # Test event handler
        def update_handler(data):
            return f"Updated: {data}"
        
        dynamic_text.on_update("data_change", update_handler)
        
        # Trigger event
        result = dynamic_text.handle_event("data_change", "test data")
        
        assert result == True  # Event was handled
        assert dynamic_text.text == "Updated: test data"
    
    def test_dynamic_text_data_updates(self):
        """Test DynamicTextElement data-driven updates."""
        progress = DynamicTextElement("progress", "Starting...")
        
        # Test progress update
        progress.update_text_from_data({"current": 50, "total": 100})
        assert "50/100" in progress.text
        assert "50%" in progress.text
        
        # Test status update
        progress.update_text_from_data({"status": "Complete"})
        assert "Status: Complete" in progress.text


class TestInputComponentIntegration:
    """Test InputComponent integration with prompt-toolkit."""
    
    def test_input_component_prompt_toolkit(self):
        """Test InputComponent conversion to TextArea."""
        input_comp = SingleLineInput("username")
        input_comp.set_placeholder("Enter username")
        input_comp.set_default_value("test_user")
        
        # Convert to prompt-toolkit
        ptk_widget = input_comp.to_prompt_toolkit()
        
        # Should be a TextArea widget
        assert isinstance(ptk_widget, TextArea)
        assert ptk_widget.multiline == False  # Single line
        
    def test_input_validation_integration(self):
        """Test input validation with ComponentBase integration."""
        input_comp = SingleLineInput("email")
        input_comp.set_required(True)
        input_comp.add_validation_rule(Validators.email())
        input_comp.add_validation_rule(Validators.min_length(5))
        
        # Test empty value (should fail required)
        input_comp.set_value("")
        errors = input_comp.validate()
        assert len(errors) > 0
        assert any("required" in error.lower() for error in errors)
        
        # Test invalid email
        input_comp.set_value("bad")
        errors = input_comp.validate()
        assert len(errors) > 0
        assert any("email" in error.lower() for error in errors)
        
        # Test valid email
        input_comp.set_value("test@example.com")
        errors = input_comp.validate()
        assert len(errors) == 0
    
    def test_password_input_masking(self):
        """Test password input masking."""
        password = PasswordInput("password")
        password.set_default_value("secret123")
        
        # Convert to prompt-toolkit
        ptk_widget = password.to_prompt_toolkit()
        
        # Should be a TextArea with password=True
        assert isinstance(ptk_widget, TextArea)
        assert ptk_widget.password == True
    
    def test_input_event_handling(self):
        """Test input component event handling."""
        input_comp = SingleLineInput("test_input")
        
        # Track events
        events_fired = []
        
        def on_change(comp, old_val, new_val):
            events_fired.append(f"changed: {old_val} -> {new_val}")
            
        def on_validation_error(comp, errors):
            events_fired.append(f"validation_error: {errors}")
        
        input_comp.on_event("value_changed", on_change)
        input_comp.on_event("validation_error", on_validation_error)
        input_comp.add_validation_rule(Validators.min_length(5))
        
        # Trigger value changes
        input_comp.set_value("hi")  # Too short, should trigger validation error
        input_comp.set_value("hello")  # Valid
        
        # Check events were fired
        assert len(events_fired) >= 2
        assert any("validation_error" in event for event in events_fired)
        assert any("changed" in event for event in events_fired)


class TestButtonComponentIntegration:
    """Test ButtonComponent integration with prompt-toolkit."""
    
    def test_button_component_prompt_toolkit(self):
        """Test ButtonComponent conversion to Button widget."""
        button = ButtonComponent("test_btn", "Click Me")
        button.set_width(20)
        
        # Convert to prompt-toolkit
        ptk_widget = button.to_prompt_toolkit()
        
        # Should be a Button widget
        assert isinstance(ptk_widget, Button)
        assert ptk_widget.text == "Click Me"
        assert ptk_widget.width == 20
    
    def test_button_click_handling(self):
        """Test button click event handling."""
        clicks_received = []
        
        def on_click(btn):
            clicks_received.append(f"Button {btn.name} clicked")
        
        button = ButtonComponent("test_btn", "Test")
        button.on_click(on_click)
        
        # Trigger click
        button.click()
        
        assert len(clicks_received) == 1
        assert "test_btn clicked" in clicks_received[0]
    
    def test_button_factory_methods(self):
        """Test button factory convenience methods."""
        # Test factory methods
        ok_btn = Buttons.ok()
        cancel_btn = Buttons.cancel()
        save_btn = Buttons.save()
        delete_btn = Buttons.delete()
        
        # Verify button types and text
        assert ok_btn.text == "OK"
        assert cancel_btn.text == "Cancel"
        assert save_btn.text == "Save"
        assert delete_btn.text == "Delete"
        
        # Verify they can be converted to prompt-toolkit
        assert isinstance(ok_btn.to_prompt_toolkit(), Button)
        assert isinstance(cancel_btn.to_prompt_toolkit(), Button)
        assert isinstance(save_btn.to_prompt_toolkit(), Button)
        assert isinstance(delete_btn.to_prompt_toolkit(), Button)


class TestFullIntegrationScenarios:
    """Test complete integration scenarios combining all components."""
    
    def test_complete_form_page(self):
        """Test a complete form page with all component types."""
        # Create a form page
        form_page = Page("user_form")
        
        # Configure sections
        form_page.title_section.set_title("User Registration").set_border(True)
        form_page.footer_section.set_layout_direction("horizontal")
        
        # Add title text
        title_text = TextElement("title", "Please enter your information")
        form_page.header_section.add_element(title_text)
        
        # Create form container in body
        form_container = Container("form")
        form_container.set_title("User Details").set_border(True)
        
        # Add form fields
        username = SingleLineInput("username")
        username.set_label("Username").set_required(True)
        username.add_validation_rule(Validators.min_length(3))
        
        email = SingleLineInput("email")
        email.set_label("Email").set_required(True)
        email.add_validation_rule(Validators.email())
        
        password = PasswordInput("password")
        password.set_label("Password").set_required(True)
        password.add_validation_rule(Validators.min_length(8))
        
        # Add status text (dynamic)
        status = DynamicTextElement("status", "Ready to submit")
        
        form_container.add_element(username)
        form_container.add_element(email)
        form_container.add_element(password)
        form_container.add_element(status)
        
        form_page.body_section.add_element(form_container)
        
        # Add buttons to footer
        submit_btn = Buttons.submit("submit_form")
        cancel_btn = Buttons.cancel("cancel_form")
        
        form_page.footer_section.add_element(submit_btn)
        form_page.footer_section.add_element(cancel_btn)
        
        # Test that everything converts to prompt-toolkit properly
        layout = form_page.to_prompt_toolkit_layout()
        assert isinstance(layout, VSplit)
        
        # Verify all components are accessible
        assert username.to_prompt_toolkit() is not None
        assert email.to_prompt_toolkit() is not None
        assert password.to_prompt_toolkit() is not None
        assert submit_btn.to_prompt_toolkit() is not None
        assert cancel_btn.to_prompt_toolkit() is not None
    
    def test_form_validation_workflow(self):
        """Test complete form validation workflow."""
        # Create form components
        username = SingleLineInput("username")
        username.set_required(True).add_validation_rule(Validators.min_length(3))
        
        email = SingleLineInput("email")
        email.set_required(True).add_validation_rule(Validators.email())
        
        # Test invalid form
        username.set_value("ab")  # Too short
        email.set_value("invalid")  # Not an email
        
        username_errors = username.validate()
        email_errors = email.validate()
        
        assert len(username_errors) > 0
        assert len(email_errors) > 0
        
        # Test valid form
        username.set_value("testuser")
        email.set_value("test@example.com")
        
        username_errors = username.validate()
        email_errors = email.validate()
        
        assert len(username_errors) == 0
        assert len(email_errors) == 0
    
    def test_app_page_management(self):
        """Test App class managing multiple pages."""
        app = App()
        
        # Create pages
        page1 = Page("page1")
        page2 = Page("page2")
        
        # Add content to distinguish pages
        page1.title_section.add_element(TextElement("title1", "Page 1"))
        page2.title_section.add_element(TextElement("title2", "Page 2"))
        
        # Add pages to app
        app.add_page(page1)
        app.add_page(page2)
        
        # Test page management
        assert app.get_current_page() == page1  # First page is current
        
        app.navigate_to_page("page2")
        assert app.get_current_page() == page2
        
        app.navigate_to_page("page1")
        assert app.get_current_page() == page1
        
        # Test that app can generate prompt-toolkit application
        ptk_app = app.to_prompt_toolkit_application()
        assert ptk_app is not None
    
    def test_interactive_component_integration(self):
        """Test interactive components working together."""
        # Create a container with interactive components
        container = Container("interactive")
        
        # Add input that updates dynamic text
        input_field = SingleLineInput("input")
        status_text = DynamicTextElement("status", "Type something...")
        
        # Connect input to status text
        def update_status(comp, old_val, new_val):
            if new_val:
                status_text.set_text(f"You typed: {new_val}")
            else:
                status_text.set_text("Type something...")
        
        input_field.on_event("value_changed", update_status)
        
        # Add button that processes input
        process_btn = ButtonComponent("process", "Process")
        result_text = DynamicTextElement("result", "No result yet")
        
        def process_input(btn):
            input_value = input_field.get_text()
            if input_value:
                result_text.set_text(f"Processed: {input_value.upper()}")
            else:
                result_text.set_text("Nothing to process")
        
        process_btn.on_click(process_input)
        
        # Add all to container
        container.add_element(input_field)
        container.add_element(status_text)
        container.add_element(process_btn)
        container.add_element(result_text)
        
        # Test the interaction
        input_field.set_value("hello world")
        # Status should update automatically via event
        assert "hello world" in status_text.get_text()
        
        # Process the input
        process_btn.click()
        assert "HELLO WORLD" in result_text.get_text()
        
        # Test that everything converts to prompt-toolkit
        ptk_widget = container.to_prompt_toolkit()
        assert isinstance(ptk_widget, Frame)


# Helper function to run tests
def run_integration_tests():
    """Run all integration tests and report results."""
    import sys
    
    # Test classes to run
    test_classes = [
        TestPageSectionArchitecture,
        TestContainerIntegration,
        TestTextElementIntegration,
        TestInputComponentIntegration,
        TestButtonComponentIntegration,
        TestFullIntegrationScenarios,
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = []
    
    for test_class in test_classes:
        print(f"\nRunning {test_class.__name__}...")
        
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        for test_method in test_methods:
            total_tests += 1
            try:
                getattr(test_instance, test_method)()
                print(f"  ✓ {test_method}")
                passed_tests += 1
            except Exception as e:
                print(f"  ✗ {test_method}: {e}")
                failed_tests.append((test_class.__name__, test_method, str(e)))
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Integration Test Results")
    print(f"{'='*60}")
    print(f"Total tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    
    if failed_tests:
        print(f"\nFailed tests:")
        for class_name, method_name, error in failed_tests:
            print(f"  {class_name}.{method_name}: {error}")
        return False
    else:
        print(f"\nAll tests passed! 🎉")
        return True


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)