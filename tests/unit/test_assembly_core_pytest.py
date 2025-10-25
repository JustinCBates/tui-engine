import pytest

from questionary_extended.core.assembly import Assembly


class FakePage:
    pass


def test_assembly_init_and_parent():
    p = FakePage()
    a = Assembly("my_assembly", p)
    assert a.name == "my_assembly"
    assert a.parent_page is p
    assert a.components == []
    # event handlers dict initialized with keys
    assert set(a.event_handlers.keys()) == {"change", "validate", "complete"}
    # parent() returns the page
    assert a.parent() is p


def test_event_registration_methods():
    p = FakePage()
    a = Assembly("x", p)

    def handler(value, assem):
        pass

    # on_change should append a (field, handler) tuple
    ret = a.on_change("field1", handler)
    assert ret is a
    assert ("field1", handler) in a.event_handlers["change"]

    # on_validate appends a handler directly
    def vhandler(assem):
        return None

    ret2 = a.on_validate(vhandler)
    assert ret2 is a
    assert vhandler in a.event_handlers["validate"]

    # on_complete appends a (field, handler)
    def complete_handler(val, assem):
        pass

    ret3 = a.on_complete("done_field", complete_handler)
    assert ret3 is a
    assert ("done_field", complete_handler) in a.event_handlers["complete"]


def test_not_implemented_placeholders_raise():
    p = FakePage()
    a = Assembly("y", p)

    with pytest.raises(NotImplementedError):
        a.text("t")

    with pytest.raises(NotImplementedError):
        a.select("s", choices=["a", "b"])

    with pytest.raises(NotImplementedError):
        a.show_components(["a"])

    with pytest.raises(NotImplementedError):
        a.hide_components(["a"])

    with pytest.raises(NotImplementedError):
        a.get_value("x")

    with pytest.raises(NotImplementedError):
        a.get_related_value("other.x")
