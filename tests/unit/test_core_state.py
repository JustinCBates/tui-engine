import pytest

from src.questionary_extended.core.state import PageState


def test_set_and_get_global_key():
    s = PageState()
    s.set("foo", 123)
    assert s.get("foo") == 123
    assert s.has_key("foo") is True


def test_set_and_get_namespaced_key():
    s = PageState()
    s.set("asm.field", "value")
    assert s.get("asm.field") == "value"
    assert s.has_key("asm.field") is True


def test_get_with_default_and_missing_keys():
    s = PageState()
    assert s.get("missing", default=42) == 42
    assert s.get("asm.missing", default="x") == "x"


def test_get_assembly_state_and_clear():
    s = PageState()
    s.set("a.x", 1)
    s.set("a.y", 2)
    s.set("b.z", 3)

    a_state = s.get_assembly_state("a")
    assert a_state == {"x": 1, "y": 2}

    # clear assembly
    s.clear_assembly("a")
    assert s.get_assembly_state("a") == {}


def test_get_all_state_flattening():
    s = PageState()
    s.set("global", "g")
    s.set("a.x", 10)
    s.set("b.y", 20)

    all_state = s.get_all_state()
    assert all_state["global"] == "g"
    assert all_state["a.x"] == 10
    assert all_state["b.y"] == 20


def test_clear_all():
    s = PageState()
    s.set("x", 1)
    s.set("a.y", 2)

    s.clear_all()
    assert s.get("x") is None
    assert s.get_assembly_state("a") == {}


def test_has_key_for_missing_namespaces():
    s = PageState()
    assert s.has_key("no.such") is False


def test_overwrite_values():
    s = PageState()
    s.set("a.x", 1)
    s.set("a.x", 2)
    assert s.get("a.x") == 2


def test_non_string_key_behavior():
    s = PageState()
    # keys are expected to be strings; passing non-string should raise TypeError
    with pytest.raises(TypeError):
        # Attempting to use '.' in non-string will raise a TypeError
        s.set(123, "v")
