import questionary


class FakeQ:
    def __init__(self, value=None):
        self._value = value

    def ask(self, *a, **k):
        return self._value


def test_theme_and_stylebuilder_merge_and_palette():
    from questionary_extended.styles import Theme, ColorPalette, create_theme, StyleBuilder, apply_theme_to_style
    from questionary_extended.styles import DARK_PALETTE
    from prompt_toolkit.styles.style import Style

    th = create_theme('t', palette=DARK_PALETTE)
    qs = th.to_questionary_style()
    assert isinstance(qs, Style)

    sb = StyleBuilder()
    sb.primary('#123456').text('#abcdef').success('#00ff00')
    style_obj = sb.build()
    assert isinstance(style_obj, Style)

    merged = apply_theme_to_style(th, base_style=style_obj)
    assert isinstance(merged, Style)


def test_grouped_and_multi_level_select_and_rating_allow_zero(monkeypatch):
    from questionary_extended import prompts as prompts_mod

    # grouped_select uses questionary.Separator and questionary.select
    class FakeSeparator:
        def __init__(self, text):
            self.text = text

    monkeypatch.setattr(questionary, 'Separator', FakeSeparator)
    monkeypatch.setattr(questionary, 'select', lambda *a, **k: FakeQ('sel'))

    groups = {'G1': ['x', 'y']}
    q = prompts_mod.grouped_select('G', groups)
    assert q.ask() == 'sel'

    # multi_level_select is alias to tree_select
    monkeypatch.setattr(questionary, 'select', lambda *a, **k: FakeQ('multi'))
    data = {'A': ['v1']}
    q2 = prompts_mod.multi_level_select('M', data)
    assert q2.ask() == 'multi'

    # rating allow_zero
    monkeypatch.setattr(questionary, 'select', lambda *a, **k: FakeQ(0))
    q3 = prompts_mod.rating('R', max_rating=3, allow_zero=True)
    assert q3.ask() == 0


def test_color_default_formats(monkeypatch):
    from questionary_extended import prompts as prompts_mod

    # color defaults formats to ['hex'] when None
    monkeypatch.setattr(questionary, 'text', lambda *a, **k: FakeQ('#112233'))
    q = prompts_mod.color('Pick:', formats=None)
    assert q.ask() == '#112233'
