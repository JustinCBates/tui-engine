import builtins
from typing import Any

import pytest

from questionary_extended.core import component as compmod


def test_wrapper_defaults_text_and_password_and_path():
    c = compmod.text("first_name")
    assert c.name == "first_name"
    assert c.component_type == "text"
    # default message is derived from the name
    assert "First Name" in c.questionary_config["message"].replace("_", " ") or "First" in c.questionary_config["message"]

    p = compmod.password("secret")
    assert p.component_type == "password"
    assert "Secret" in p.questionary_config["message"]

    path = compmod.path("save_path")
    assert path.component_type == "path"
    assert "Save Path" in path.questionary_config["message"].replace("_", " ")


def test_wrapper_defaults_select_checkbox_autocomplete_confirm():
    s = compmod.select("color")
    assert s.component_type == "select"
    assert s.questionary_config["choices"] == []
    assert "Choose" in s.questionary_config["message"]

    chk = compmod.checkbox("items")
    assert chk.component_type == "checkbox"
    assert chk.questionary_config["choices"] == []

    a = compmod.autocomplete("pick")
    assert a.component_type == "autocomplete"
    assert a.questionary_config["choices"] == []

    conf = compmod.confirm("agree")
    assert conf.component_type == "confirm"
    assert "Confirm" in conf.questionary_config["message"]


def test_add_validator_and_is_visible_branching():
    c = compmod.Component("x", "text", message="m")
    assert c.is_visible({}) is True

    # when_condition present still returns True in current implementation
    c2 = compmod.Component("y", "text", message="m", when="some_cond")
    assert c2.when_condition == "some_cond"
    assert c2.is_visible({}) is True

    called = []

    def val(x: Any):
        called.append(x)

    c.add_validator(val)
    assert c.validators and c.validators[-1] is val


def test_create_questionary_component_calls_monkeypatched_questionary(monkeypatch):
    # Prepare sentinels and capture kwargs
    sentinel = object()

    def make_fake(name):
        def _fake(**kwargs):
            # return a tuple so tests can inspect call
            return (name, kwargs)

        return _fake

    # Patch all functions used in the map
    for k in ("text", "select", "confirm", "password", "checkbox", "autocomplete", "path"):
        monkeypatch.setattr(compmod.questionary, k, make_fake(k))

    # Test each mapping
    for comp_type in ("text", "select", "confirm", "password", "checkbox", "autocomplete", "path"):
        cfg = {"message": f"hi-{comp_type}"}
        if comp_type in ("select", "checkbox", "autocomplete"):
            cfg["choices"] = ["a", "b"]
        c = compmod.Component("n", comp_type, **cfg)
        result = c.create_questionary_component()
        assert isinstance(result, tuple)
        name, kwargs = result
        assert name == comp_type
        # message should be passed through
        assert kwargs.get("message") == cfg["message"]
        if "choices" in cfg:
            assert kwargs.get("choices") == cfg["choices"]


def test_create_questionary_component_unsupported():
    c = compmod.Component("z", "not-a-type", message="x")
    with pytest.raises(ValueError, match="Unsupported component type"):
        c.create_questionary_component()
