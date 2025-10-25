import io
import sys


class FakeQ:
    def __init__(self, value=None):
        self._value = value

    def ask(self, *a, **k):
        return self._value


def test_tag_and_fuzzy_and_slider_and_table_and_form(monkeypatch):
    from questionary_extended import prompts as prompts_mod
    import questionary

    # tag_select -> checkbox
    monkeypatch.setattr(questionary, 'checkbox', lambda *a, **k: FakeQ(['tag1', 'tag2']))
    q = prompts_mod.tag_select('Tags:', ['tag1', 'tag2'])
    assert q.ask() == ['tag1', 'tag2']

    # fuzzy_select -> autocomplete
    monkeypatch.setattr(questionary, 'autocomplete', lambda *a, **k: FakeQ('choice1'))
    q2 = prompts_mod.fuzzy_select('Find:', ['choice1', 'choice2'])
    assert q2.ask() == 'choice1'

    # slider delegates to number -> text
    monkeypatch.setattr(questionary, 'text', lambda *a, **k: FakeQ('10'))
    q3 = prompts_mod.slider('Slide:', min_value=0, max_value=10, step=1)
    assert q3.ask() == '10'

    # table currently returns LazyQuestion wrapping text
    q4 = prompts_mod.table('Table:', [])
    assert hasattr(q4, 'ask')

    # form/wizard call questionary.prompt -> return dict
    monkeypatch.setattr(questionary, 'prompt', lambda q, **k: {'a': 1})
    res = prompts_mod.form([{'name': 'a', 'type': 'text'}])
    assert isinstance(res, dict)
    assert res.get('a') == 1


def test_progress_tracker_prints(monkeypatch, capsys):
    from questionary_extended.prompts_core import ProgressTracker

    pt = ProgressTracker('T', total_steps=3)
    # Capture stdout
    pt.__enter__()
    pt.step('one')
    pt.update(2, 'two')
    pt.complete('done')
    pt.__exit__(None, None, None)

    captured = capsys.readouterr()
    assert 'Starting' in captured.out or 'Starting' in captured.err
    assert 'Completed' in captured.out or 'Completed' in captured.err or 'done' in captured.out
