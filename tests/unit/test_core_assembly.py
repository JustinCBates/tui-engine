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

    assert any(isinstance(h, tuple) and h[0] == "field1" for h in a.event_handlers["change"]) 
    assert any(callable(h) for h in a.event_handlers["validate"]) 
    assert any(isinstance(h, tuple) and h[0] == "field2" for h in a.event_handlers["complete"]) 


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
