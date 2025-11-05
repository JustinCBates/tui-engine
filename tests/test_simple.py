"""
Simple integration test to validate core TUI Engine architecture.

This focuses on the essential functionality rather than comprehensive testing.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_basic_page_creation():
    """Test that we can create a basic page with content."""
    print("Testing basic page creation...")
    
    from tui_engine.page import Page
    from tui_engine.text_element import TextElement
    
    # Create a simple page
    page = Page("test_page")
    
    # Add content to body section
    text = TextElement("greeting", "Hello, TUI Engine!")
    page.body_section.add(text)
    
    # Verify basic structure
    assert page.body_section is not None
    assert len(page.body_section.children) == 1
    assert page.body_section.children[0].text == "Hello, TUI Engine!"
    
    print("✓ Basic page creation works")


def test_prompt_toolkit_integration():
    """Test that components convert to prompt-toolkit widgets."""
    print("Testing prompt-toolkit integration...")
    
    from tui_engine.container import Container
    from tui_engine.text_element import TextElement
    from tui_engine.button_component import ButtonComponent
    
    # Create container with mixed content
    container = Container("test_container")
    container.set_title("Test Container").set_border(True)
    
    # Add text element
    text = TextElement("text", "Test text content")
    container.add(text)
    
    # Add button
    button = ButtonComponent("btn", "Click Me")
    container.add(button)
    
    # Convert to prompt-toolkit
    ptk_widget = container.to_prompt_toolkit()
    
    # Basic validation - should not crash and return something
    assert ptk_widget is not None
    
    print("✓ prompt-toolkit integration works")


def test_component_validation():
    """Test component validation system."""
    print("Testing component validation...")
    
    from tui_engine.input_component import SingleLineInput
    from tui_engine.component_base import Validators
    
    # Create input with validation
    input_field = SingleLineInput("test_input")
    input_field.set_required(True)
    input_field.add_validation_rule(Validators.min_length(5))
    
    # Test invalid input
    input_field.set_value("hi")  # Too short
    errors = input_field.validate()
    assert len(errors) > 0
    
    # Test valid input
    input_field.set_value("hello world")
    errors = input_field.validate()
    assert len(errors) == 0
    
    print("✓ Component validation works")


def test_button_events():
    """Test button click events."""
    print("Testing button events...")
    
    from tui_engine.button_component import Buttons
    
    clicked = []
    
    def on_click(btn):
        clicked.append(btn.name)
    
    # Create button with handler
    button = Buttons.ok("test_ok", on_click)
    
    # Trigger click
    button.click()
    
    assert len(clicked) == 1
    assert clicked[0] == "test_ok"
    
    print("✓ Button events work")


def test_complete_form():
    """Test a complete form with all component types."""
    print("Testing complete form...")
    
    from tui_engine.page import Page
    from tui_engine.container import Container
    from tui_engine.text_element import TextElement
    from tui_engine.input_component import SingleLineInput
    from tui_engine.button_component import Buttons
    
    # Create form page
    page = Page("form_page")
    
    # Add title
    title_container = page.title_section_container("title")
    title_text = TextElement("title", "User Registration Form")
    title_container.add(title_text)
    
    # Create form in body
    form = Container("form")
    form.set_title("Enter Your Details").set_border(True)
    
    # Add form fields
    username = SingleLineInput("username")
    username.set_label("Username").set_required(True)
    form.add(username)
    
    # Add buttons
    submit_btn = Buttons.submit("submit")
    cancel_btn = Buttons.cancel("cancel")
    
    form.add(submit_btn)
    form.add(cancel_btn)
    
    page.body_section.add(form)
    
    # Test form validation
    username.set_value("")  # Empty
    errors = username.validate()
    assert len(errors) > 0  # Should have required field error
    
    username.set_value("testuser")
    errors = username.validate()
    assert len(errors) == 0  # Should be valid
    
    # Test prompt-toolkit conversion
    layout = page.to_prompt_toolkit_layout()
    assert layout is not None
    
    print("✓ Complete form works")


def run_simple_tests():
    """Run all simple integration tests."""
    print("Running TUI Engine Integration Tests")
    print("=" * 50)
    
    tests = [
        test_basic_page_creation,
        test_prompt_toolkit_integration,
        test_component_validation,
        test_button_events,
        test_complete_form,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The TUI Engine architecture works!")
    else:
        print(f"❌ {total - passed} tests failed")
    
    return passed == total


if __name__ == "__main__":
    success = run_simple_tests()
    sys.exit(0 if success else 1)