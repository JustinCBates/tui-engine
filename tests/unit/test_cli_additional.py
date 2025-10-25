import types
import builtins

import pytest


def make_seq_factory(values):
    it = iter(values)

    class FP:
        def __init__(self):
            pass

        def ask(self):
            return next(it)

    return lambda *a, **k: FP()


def test_form_builder_select_branch(monkeypatch, capsys):
    """Simulate adding one select field so the choices-input branch runs."""
    import questionary_extended.cli as cli

    # confirm: True (add field), then False (stop)
    monkeypatch.setattr(cli, "questionary", types.SimpleNamespace())
    fake_q = cli.questionary
    fake_q.confirm = make_seq_factory([True, False])
    # text will be used for field_name, field_message, and choices_input
    fake_q.text = make_seq_factory(["field1", "Prompt for field1", "a, b, c"])
    # select returns the type selected
    fake_q.select = make_seq_factory(["select"])  # field_type
    # prompt returns results mapping
    fake_q.prompt = lambda *a, **k: {"field1": "value"}

    # Call the underlying function (click-decorated object exposes .callback)
    fn = getattr(cli.form_builder, "callback", cli.form_builder)
    fn()

    out = capsys.readouterr().out
    assert "Form Results" in out


def test_quick_no_input(monkeypatch, capsys):
    """Call quick with a prompt that returns falsy to hit the else branch."""
    import questionary_extended.cli as cli

    # enhanced_text returns an object whose ask() returns None
    class FP:
        def ask(self):
            return None

    monkeypatch.setattr(cli, "enhanced_text", lambda *a, **k: FP())

    fn = getattr(cli.quick, "callback", cli.quick)
    # call underlying function directly with argument
    fn("text")

    out = capsys.readouterr().out
    assert "No input provided" in out
