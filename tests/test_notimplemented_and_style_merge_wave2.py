def test_assembly_card_page_not_implemented():
    from questionary_extended.core.assembly import Assembly
    from questionary_extended.core.card import Card
    from questionary_extended.core.page import Page

    # Minimal Page stub for parent
    class P:
        pass

    # Assembly methods that should raise NotImplementedError
    a = Assembly("name", parent=P())

    # text() and select() are now implemented, so they should NOT raise
    # Instead, test the methods that DO raise NotImplementedError
    try:
        a.show_components(["f"])
        raised_show = False
    except NotImplementedError:
        raised_show = True

    try:
        a.hide_components(["f"])
        raised_hide = False
    except NotImplementedError:
        raised_hide = True

    try:
        a.get_value("f")
        raised_get = False
    except NotImplementedError:
        raised_get = True

    try:
        a.get_related_value("f")
        raised_related = False
    except NotImplementedError:
        raised_related = True

    assert raised_show and raised_hide and raised_get and raised_related

    # Card - check if it has similar NotImplementedError methods
    # For now, just verify Card can be instantiated
    Card("t", parent=P())
    # text() and select() should work if Card has them implemented
    # If they're not implemented, they would raise AttributeError, not NotImplementedError

    # Page.run should raise NotImplementedError
    p = Page("p")
    try:
        p.run()
        pr = False
    except NotImplementedError:
        pr = True

    assert pr


def test_apply_theme_to_style_various_rules():
    from prompt_toolkit.styles.style import Style

    from questionary_extended.styles import ColorPalette, Theme, apply_theme_to_style

    th = Theme("t", palette=ColorPalette())

    # Create fake base_style with _style_rules as list of tuples
    class FakeBase:
        _style_rules = [("a", "fg:#123456"), ("b", "fg:#abcdef")]

    merged = apply_theme_to_style(th, base_style=FakeBase())
    assert isinstance(merged, Style)

    # Create fake base_style with token/style attributes in objects
    class RuleObj:
        def __init__(self, token, style):
            self.token = token
            self.style = style

    class FakeBase2:
        _style_rules = [RuleObj("x", "fg:#112233"), RuleObj("y", "fg:#334455")]

    merged2 = apply_theme_to_style(th, base_style=FakeBase2())
    assert isinstance(merged2, Style)
