def test_assembly_card_page_not_implemented():
    from questionary_extended.core.assembly import Assembly
    from questionary_extended.core.card import Card
    from questionary_extended.core.page import Page

    # Minimal Page stub for parent
    class P:
        pass

    # Assembly methods should raise NotImplementedError for text/select etc.
    a = Assembly('name', parent=P())
    try:
        a.text('f')
        raised_text = False
    except NotImplementedError:
        raised_text = True

    try:
        a.select('f', [])
        raised_select = False
    except NotImplementedError:
        raised_select = True

    assert raised_text and raised_select

    # Card text/select should raise
    c = Card('t', parent=P())
    try:
        c.text('n')
        rt = False
    except NotImplementedError:
        rt = True

    try:
        c.select('n', [])
        rs = False
    except NotImplementedError:
        rs = True

    assert rt and rs

    # Page.run should raise NotImplementedError
    p = Page('p')
    try:
        p.run()
        pr = False
    except NotImplementedError:
        pr = True

    assert pr


def test_apply_theme_to_style_various_rules():
    from questionary_extended.styles import Theme, ColorPalette, apply_theme_to_style
    from questionary import Style

    th = Theme('t', palette=ColorPalette())

    # Create fake base_style with _style_rules as list of tuples
    class FakeBase:
        _style_rules = [('a', 'fg:#123456'), ('b', 'fg:#abcdef')]

    merged = apply_theme_to_style(th, base_style=FakeBase())
    assert isinstance(merged, Style)

    # Create fake base_style with token/style attributes in objects
    class RuleObj:
        def __init__(self, token, style):
            self.token = token
            self.style = style

    class FakeBase2:
        _style_rules = [RuleObj('x', 'fg:#112233'), RuleObj('y', 'fg:#334455')]

    merged2 = apply_theme_to_style(th, base_style=FakeBase2())
    assert isinstance(merged2, Style)
