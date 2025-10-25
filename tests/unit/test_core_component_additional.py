from types import SimpleNamespace
import pytest

from questionary import ValidationError

from questionary_extended.core.component import (
    Component,
    text,
    select,
    confirm,
    password,
    checkbox,
    autocomplete,
    path,
)


def test_factory_defaults_and_component_type():
    t = text("user_name")
    assert isinstance(t, Component)
    assert t.component_type == "text"
    assert "message" in t.questionary_config

    s = select("plan")
    assert s.component_type == "select"
    assert isinstance(s.questionary_config.get("choices"), list)

    assert confirm("agree").component_type == "confirm"
    assert password("pwd").component_type == "password"
    assert checkbox("opts").component_type == "checkbox"
    assert autocomplete("pick").component_type == "autocomplete"
    assert path("file").component_type == "path"


def test_create_questionary_component_mapping(monkeypatch):
    called = {}

    def mk(name):
        def _fake(**kwargs):
            called[name] = kwargs
            return SimpleNamespace(name=name, kwargs=kwargs)

        return _fake

    # Patch the questionary functions used by Component
    monkeypatch.setattr("questionary.text", mk("text"))
    monkeypatch.setattr("questionary.select", mk("select"))
    monkeypatch.setattr("questionary.confirm", mk("confirm"))
    monkeypatch.setattr("questionary.password", mk("password"))
    monkeypatch.setattr("questionary.checkbox", mk("checkbox"))
    monkeypatch.setattr("questionary.autocomplete", mk("autocomplete"))
    monkeypatch.setattr("questionary.path", mk("path"))

    c = Component("u", "text", message="Hello")
    res = c.create_questionary_component()
    assert res.name == "text"
    assert called["text"]["message"] == "Hello"

    c2 = Component("p", "select", choices=["a", "b"], message="Pick")
    r2 = c2.create_questionary_component()
    assert r2.name == "select"
    assert called["select"]["choices"] == ["a", "b"]


def test_unsupported_component_type_raises():
    c = Component("x", "unknown")
    with pytest.raises(ValueError):
        c.create_questionary_component()
