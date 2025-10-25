import questionary

from questionary_extended.core import component as comp_mod


def _mk_factory(captured, name=None):
    def factory(**kwargs):
        captured["kwargs"] = kwargs
        return type("Q", (), {"_kwargs": kwargs, "kwargs": kwargs})()

    return factory


def test_questionary_config_filters_keys_and_mapping(monkeypatch):
    # Prepare captures for each factory
    caps = {}
    for key in ("text", "select", "confirm", "password", "checkbox", "autocomplete", "path"):
        caps[key] = {}
        monkeypatch.setattr(questionary, key, _mk_factory(caps[key], key))

    # Create component with keys that should be filtered out
    kwargs = {"message": "m", "when": "cond", "enhanced_validation": True, "extra": 5}
    # For each supported type, ensure create_questionary_component calls the right factory
    for t in ("text", "select", "confirm", "password", "checkbox", "autocomplete", "path"):
        c = comp_mod.Component("n", t, **kwargs)
        q = c.create_questionary_component()
        # Ensure the returned object has kwargs and 'extra' passed through, but 'when' and 'enhanced_validation' removed
        received = caps[t].get("kwargs")
        assert received is not None
        assert received.get("extra") == 5
        assert "when" not in received
        assert "enhanced_validation" not in received


def test_unsupported_type_raises():
    c = comp_mod.Component("x", "nope")
    try:
        c.create_questionary_component()
        assert False, "Expected ValueError"
    except ValueError as e:
        assert "Unsupported component type" in str(e)


def test_add_validator_and_is_visible_branches():
    c1 = comp_mod.Component("a", "text")
    assert c1.is_visible({}) is True
    assert c1.validators == []

    called = []

    def v(x):
        called.append(x)
        return True

    c1.add_validator(v)
    assert len(c1.validators) == 1
    # call the validator to ensure it's usable
    assert c1.validators[0](123) is True
    assert called == [123]

    # when_condition branch
    c2 = comp_mod.Component("b", "text", when="some>0")
    assert c2.when_condition == "some>0"
    # is_visible currently returns True for both branches
    assert c2.is_visible({}) is True

