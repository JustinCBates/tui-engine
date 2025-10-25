import pytest

from questionary_extended.core import component as comp_mod


def make_stub(component_name):
    def _stub(**kwargs):
        # return a simple dict so we can assert inputs without creating a prompt
        return {"component": component_name, "kwargs": kwargs}

    return _stub


def test_wrappers_and_create_questionary_component(monkeypatch):
    # Monkeypatch questionary functions to simple stubs
    monkeypatch.setattr(comp_mod.questionary, "text", make_stub("text"))
    monkeypatch.setattr(comp_mod.questionary, "select", make_stub("select"))
    monkeypatch.setattr(comp_mod.questionary, "confirm", make_stub("confirm"))
    monkeypatch.setattr(comp_mod.questionary, "password", make_stub("password"))
    monkeypatch.setattr(comp_mod.questionary, "checkbox", make_stub("checkbox"))
    monkeypatch.setattr(comp_mod.questionary, "autocomplete", make_stub("autocomplete"))
    monkeypatch.setattr(comp_mod.questionary, "path", make_stub("path"))

    # text wrapper default message
    t = comp_mod.text("user_name")
    assert isinstance(t, comp_mod.Component)
    assert t.name == "user_name"
    assert t.component_type == "text"
    created = t.create_questionary_component()
    assert created["component"] == "text"
    assert "message" in created["kwargs"]

    # select wrapper default choices and message
    s = comp_mod.select("fruit")
    assert s.component_type == "select"
    created_s = s.create_questionary_component()
    assert created_s["component"] == "select"
    # default choices becomes empty list
    assert created_s["kwargs"].get("choices") == []

    # confirm, password, checkbox, autocomplete, path should all return stubs
    for fn in (comp_mod.confirm, comp_mod.password, comp_mod.checkbox, comp_mod.autocomplete, comp_mod.path):
        comp = fn("x")
        assert isinstance(comp, comp_mod.Component)
        result = comp.create_questionary_component()
        assert isinstance(result, dict) and "component" in result

    # custom message provided preserved
    p = comp_mod.text("abc", message="Hello!")
    assert p.create_questionary_component()["kwargs"]["message"] == "Hello!"

    # add_validator and is_visible
    c = comp_mod.Component("n", "text")
    # initially no validators
    assert c.validators == []
    c.add_validator(lambda v: True)
    assert len(c.validators) == 1
    # is_visible without when condition returns True
    assert c.is_visible({}) is True


def test_create_questionary_component_unsupported_type():
    c = comp_mod.Component("n", "not-a-type")
    with pytest.raises(ValueError):
        c.create_questionary_component()


def test_is_visible_with_when_condition():
    # When a when_condition is present the code path after the initial
    # early-return should run. The implementation currently always returns True
    # for now; this test ensures that branch is executed for coverage.
    c = comp_mod.Component("x", "text", when="some_cond")
    assert c.when_condition == "some_cond"
    assert c.is_visible({}) is True
