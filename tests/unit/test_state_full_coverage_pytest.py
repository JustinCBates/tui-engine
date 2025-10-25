import pytest

from questionary_extended.core.state import PageState


def test_page_state_basic_operations():
    ps = PageState()

    # global set/get
    ps.set("global_key", 123)
    assert ps.get("global_key") == 123
    assert ps.has_key("global_key") is True

    # namespaced set/get
    ps.set("asm1.field1", "value1")
    assert ps.get("asm1.field1") == "value1"
    assert ps.has_key("asm1.field1") is True

    # unknown returns default
    assert ps.get("non.existent", default=5) == 5

    # get_assembly_state returns a copy
    asm_state = ps.get_assembly_state("asm1")
    assert isinstance(asm_state, dict)
    assert asm_state["field1"] == "value1"
    asm_state["field1"] = "changed"
    # original not affected
    assert ps.get("asm1.field1") == "value1"

    # get_all_state includes namespaced keys
    all_state = ps.get_all_state()
    assert "global_key" in all_state
    assert "asm1.field1" in all_state

    # clear_assembly removes assembly state
    ps.clear_assembly("asm1")
    assert ps.get("asm1.field1") is None
    assert ps.has_key("asm1.field1") is False

    # clear_all removes everything
    ps.set("another", 1)
    ps.set("asm2.k", 2)
    ps.clear_all()
    assert ps.get("another") is None
    assert ps.get("asm2.k") is None
