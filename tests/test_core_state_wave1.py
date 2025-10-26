from questionary_extended.core.state import PageState


def test_pagestate_set_get_and_clear():
    s = PageState()
    s.set("global", 1)
    assert s.get("global") == 1

    s.set("assembly.field", "x")
    assert s.get("assembly.field") == "x"
    assert s.get_assembly_state("assembly") == {"field": "x"}

    assert s.has_key("assembly.field")
    assert not s.has_key("assembly.missing")

    all_state = s.get_all_state()
    assert "assembly.field" in all_state and "global" in all_state

    s.clear_assembly("assembly")
    assert not s.has_key("assembly.field")

    s.clear_all()
    assert not s.has_key("global")
