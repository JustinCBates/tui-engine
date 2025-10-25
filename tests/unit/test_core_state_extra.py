import pytest

from src.questionary_extended.core.state import PageState


def test_get_assembly_state_returns_copy():
    s = PageState()
    s.set("a.x", 1)
    a_state = s.get_assembly_state("a")
    a_state["x"] = 999
    # original should not be affected
    assert s.get("a.x") == 1


def test_get_all_state_returns_flat_copy_and_is_independent():
    s = PageState()
    s.set("global", "g")
    s.set("a.x", 10)
    flat = s.get_all_state()
    flat["a.x"] = 0
    assert s.get("a.x") == 10


def test_has_key_global_and_namespaced():
    s = PageState()
    s.set("k", 1)
    s.set("a.v", 2)
    assert s.has_key("k") is True
    assert s.has_key("a.v") is True
    assert s.has_key("a.missing") is False


def test_clear_assembly_nonexistent_is_noop():
    s = PageState()
    # clearing non-existent assembly should not raise
    s.clear_assembly("nope")
    assert s.get_assembly_state("nope") == {}
