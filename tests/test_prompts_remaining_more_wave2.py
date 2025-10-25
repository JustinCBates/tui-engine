import questionary


class FakeQ:
    def __init__(self, value=None):
        self._value = value

    def ask(self, *a, **k):
        return self._value


def test_rich_text_time_datetime_and_percentage(monkeypatch):
    from questionary_extended import prompts as prompts_mod

    monkeypatch.setattr(questionary, 'text', lambda *a, **k: FakeQ('txt'))

    # rich_text returns a questionary.text directly
    r = prompts_mod.rich_text('R')
    assert r.ask() == 'txt'

    # time and datetime_input format default when provided
    t = prompts_mod.time('T')
    assert t.ask() == 'txt'

    dt = prompts_mod.datetime_input('DT')
    assert dt.ask() == 'txt'

    # percentage should delegate to number / text prompt
    p = prompts_mod.percentage('Pct')
    assert p.ask() == 'txt'


def test_grouped_select_with_dict_choice(monkeypatch):
    from questionary_extended import prompts as prompts_mod

    class FakeSeparator:
        def __init__(self, text):
            self.text = text

    captured = {}

    def fake_select(message, **kwargs):
        captured['choices'] = kwargs.get('choices')
        return FakeQ('sel')

    monkeypatch.setattr(questionary, 'Separator', FakeSeparator)
    monkeypatch.setattr(questionary, 'select', fake_select)

    groups = {'G1': [{'name': 'Custom', 'value': 'v1'}, 'b']}
    q = prompts_mod.grouped_select('G', groups)
    assert q.ask() == 'sel'
    # Ensure dict choice preserved
    assert any(isinstance(c, dict) and c.get('value') == 'v1' for c in captured['choices'])


def test_lazyquestion_repr_and_build(monkeypatch):
    from questionary_extended.prompts_core import LazyQuestion

    # Use questionary.text patched to return FakeQ
    monkeypatch.setattr(questionary, 'text', lambda *a, **k: FakeQ('ok'))
    lq = LazyQuestion(questionary.text, 'Msg', default='d')
    rep = repr(lq)
    assert 'LazyQuestion' in rep
    assert lq.ask() == 'ok'
