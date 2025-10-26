import questionary

from questionary_extended import prompts_extended as prompts
from questionary_extended.core.component_wrappers import Component
from tests.helpers.questionary_helpers import mock_questionary


def test_component_create_questionary_component_di():
    """Test component creation using clean DI pattern."""
    with mock_questionary() as mock_q:
        mock_q.text.return_value = "TEXT_QUESTION"
        
        comp = Component("name", "text", message="hi", foo="bar")
        res = comp.create_questionary_component()
        
        assert res == "TEXT_QUESTION"
        mock_q.text.assert_called_once_with(message="hi", foo="bar")


def test_component_unsupported_type_raises():
    c = Component("x", "unknown")
    try:
        c.create_questionary_component()
    except ValueError:
        pass
    else:
        raise AssertionError("Unsupported component type should raise ValueError")


def test_prompts_enhanced_text_returns_lazy_and_builds(monkeypatch):
    # Ensure LazyQuestion.build returns a questionary-like object
    def fake_text(message, default=None, **kwargs):
        return {"message": message, "default": default, **kwargs}

    monkeypatch.setattr(questionary, "text", fake_text)
    q = prompts.enhanced_text("Enter:")
    built = q.build()
    assert built["message"] == "Enter:"


def test_prompts_tree_select_flattening():
    choices = {"a": {"b": ["x", "y"], "c": {}}, "d": ["z"]}

    # Monkeypatch questionary.select so build() does not create a PromptSession
    def fake_select(message, **kwargs):
        return {"message": message, **kwargs}

    import questionary as _q

    _q.select = fake_select

    q = prompts.tree_select("pick", choices)
    built = q.build()
    # ensure choices were provided and flattened
    assert "choices" in built and isinstance(built["choices"], list)


def test_prompts_rating_choices_structure(monkeypatch):
    # Stub questionary.select to capture choices passed
    captured = {}

    def fake_select(*args, **kwargs):
        captured.update(kwargs)
        # also capture positional message if provided
        if args:
            captured["message"] = args[0]
        return "SEL"

    monkeypatch.setattr(questionary, "select", fake_select)
    q = prompts.rating("rate", max_rating=3, icon="*")
    q.build()
    # Ensure choices kwarg present and has 3 entries
    assert "choices" in captured
    assert len(captured["choices"]) == 3
