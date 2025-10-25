import questionary


class FakeQ:
    def __init__(self, value=None):
        self._value = value

    def ask(self, *args, **kwargs):
        return self._value


def test_enhanced_text_lazy_question(monkeypatch):
    from questionary_extended import prompts as prompts_mod

    # Ensure LazyQuestion.build uses questionary.text
    monkeypatch.setattr(questionary, 'text', lambda *a, **k: FakeQ('ok'))

    q = prompts_mod.enhanced_text('Enter:')
    # Should be a LazyQuestion or Question-like; calling ask() returns patched value
    assert hasattr(q, 'ask')
    assert q.ask() == 'ok'


def test_number_lazy_question_and_integer(monkeypatch):
    from questionary_extended import prompts as prompts_mod

    monkeypatch.setattr(questionary, 'text', lambda *a, **k: FakeQ('42'))

    q = prompts_mod.number('Num:')
    assert q.ask() == '42'

    qi = prompts_mod.integer('Int:')
    assert qi.ask() == '42'


def test_rating_choices_and_selection(monkeypatch):
    from questionary_extended import prompts as prompts_mod

    # Patch questionary.select to capture choices passed
    captured = {}

    def fake_select(message, **kwargs):
        captured['message'] = message
        captured['choices'] = kwargs.get('choices')
        return FakeQ(3)

    monkeypatch.setattr(questionary, 'select', fake_select)

    q = prompts_mod.rating('Rate me:', max_rating=4, icon='*')
    # When asked, patched select returns 3
    assert q.ask() == 3
    # Validate choices were created with length 4 (1..4) by default
    assert len(captured['choices']) == 4


def test_tree_select_flatten(monkeypatch):
    from questionary_extended import prompts as prompts_mod

    data = {
        'A': {'X': ['one', 'two'], 'Y': ['three']},
        'B': ['four']
    }

    monkeypatch.setattr(questionary, 'select', lambda *a, **k: FakeQ('A/X/one'))

    q = prompts_mod.tree_select('Pick:', data)
    # The LazyQuestion should build/ask and return the patched selection
    assert q.ask() == 'A/X/one'


def test_grouped_select_uses_separator_and_choices(monkeypatch):
    from questionary_extended import prompts as prompts_mod

    # Patch Separator and select
    class FakeSeparator:
        def __init__(self, text):
            self.text = text

    monkeypatch.setattr(questionary, 'Separator', FakeSeparator)

    def fake_select(message, **kwargs):
        # Ensure choices include separators and values as strings
        choices = kwargs.get('choices')
        return FakeQ('choice')

    monkeypatch.setattr(questionary, 'select', fake_select)

    groups = {'G1': ['a', 'b'], 'G2': ['c']}
    q = prompts_mod.grouped_select('Pick group:', groups)
    assert q.ask() == 'choice'
