from unittest.mock import Mock, PropertyMock, patch

import pytest

from src.questionary_extended.core.assembly import Assembly


class DummyPage:
    pass


def test_assembly_init_and_parent():
    p = DummyPage()
    a = Assembly("my_asm", p)

    assert a.name == "my_asm"
    assert a.parent_page is p
    assert a.components == []
    assert isinstance(a.event_handlers, dict)
    # default event handler keys
    assert set(a.event_handlers.keys()) == {"change", "validate", "complete"}


def test_on_change_on_validate_on_complete_append_handlers():
    p = DummyPage()
    a = Assembly("n", p)

    def handler(v, asm=None):
        return "ok"

    a.on_change("field1", handler)
    a.on_validate(lambda asm: None)
    a.on_complete("field2", handler)

    assert any(
        isinstance(h, tuple) and h[0] == "field1" for h in a.event_handlers["change"]
    )
    assert any(callable(h) for h in a.event_handlers["validate"])
    assert any(
        isinstance(h, tuple) and h[0] == "field2" for h in a.event_handlers["complete"]
    )


def test_parent_method_returns_page():
    p = DummyPage()
    a = Assembly("x", p)
    assert a.parent() is p


def test_component_methods_raise_not_implemented():
    p = DummyPage()
    a = Assembly("z", p)

    # text() and select() are now implemented, so they should NOT raise
    # Only test methods that DO raise NotImplementedError

    with pytest.raises(NotImplementedError):
        a.show_components(["a"])

    with pytest.raises(NotImplementedError):
        a.hide_components(["a"])

    with pytest.raises(NotImplementedError):
        a.get_value("field")

    with pytest.raises(NotImplementedError):
        a.get_related_value("other.field")


def test_assembly_component_name_exception_handling():
    """Test exception handling when component name cannot be set (lines 64-67, 83-93)."""

    p = DummyPage()
    assembly = Assembly("test_assembly", p)

    # Create a mock component that raises an exception when name is set
    mock_component = Mock()
    # Make the name property raise an exception when assigned
    type(mock_component).name = PropertyMock(side_effect=Exception("Cannot set name"))

    # Mock the text component creation to return our problematic component
    with patch(
        "src.questionary_extended.core.component.text", return_value=mock_component
    ):
        # This should catch the exception and continue (lines 64-67)
        result = assembly.text("test_field", message="Test")

        # The assembly should still work and add the component
        assert result is assembly  # Method chaining should still work
        assert len(assembly.components) == 1
        assert assembly.components[0] is mock_component

    # Test the same for select method (lines 83-93)
    mock_component2 = Mock()
    type(mock_component2).name = PropertyMock(
        side_effect=AttributeError("Read-only name")
    )

    with patch(
        "src.questionary_extended.core.component.select", return_value=mock_component2
    ):
        # This should catch the exception and continue (lines 83-93)
        result = assembly.select("test_select", choices=["a", "b"])

        # The assembly should still work and add the component
        assert result is assembly  # Method chaining should still work
        assert len(assembly.components) == 2
        assert assembly.components[1] is mock_component2
