import questionary

from questionary_extended.core import component as comp_mod


def _fake_factory(name=None, **kw):
    # Return a simple object capturing kwargs
    return type("Q", (), {"_kw": kw, "kwargs": kw, "choices": kw.get("choices")})()


def test_create_questionary_component_various_types(monkeypatch):
    # Monkeypatch all factories used in Component.create_questionary_component
    monkeypatch.setattr(questionary, "text", lambda **kw: _fake_factory(**kw))
    monkeypatch.setattr(questionary, "select", lambda **kw: _fake_factory(**kw))
    monkeypatch.setattr(questionary, "confirm", lambda **kw: _fake_factory(**kw))
    monkeypatch.setattr(questionary, "password", lambda **kw: _fake_factory(**kw))
    monkeypatch.setattr(questionary, "checkbox", lambda **kw: _fake_factory(**kw))
    monkeypatch.setattr(questionary, "autocomplete", lambda **kw: _fake_factory(**kw))
    monkeypatch.setattr(questionary, "path", lambda **kw: _fake_factory(**kw))

    types = [
        "text",
        "select",
        "confirm",
        "password",
        "checkbox",
        "autocomplete",
        "path",
    ]
    for t in types:
        c = comp_mod.Component("nm", t, foo=1)
        q = c.create_questionary_component()
        # ensure kw passed through
        assert getattr(q, "_kw", {}).get("foo") == 1


def test_convenience_wrappers_defaults(monkeypatch):
    # Ensure wrappers create Component instances with expected defaults
    t = comp_mod.text("my_name")
    assert t.questionary_config["message"].startswith("My Name")

    s = comp_mod.select("choice_field")
    assert isinstance(s.questionary_config.get("choices"), list)

    ch = comp_mod.checkbox("c")
    assert ch.questionary_config.get("choices") == []
