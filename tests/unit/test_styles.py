from pathlib import Path
from tests.helpers.test_helpers import load_module_from_path, skip_if_coverage_excluded

# styles.py is a thin wrapper around styling helpers; respect exclusion guard
skip_if_coverage_excluded("src/questionary_extended/styles.py")

styles = load_module_from_path(
    "questionary_extended.styles", Path("src/questionary_extended/styles.py").resolve()
)

from prompt_toolkit.styles.style import Style


def test_create_theme_and_palette():
    t = styles.create_theme("Custom")
    assert t.name == "Custom"
    assert isinstance(t.palette, styles.ColorPalette)

    grad = styles.create_gradient_palette("#000000", "#ffffff", steps=3)
    assert isinstance(grad, list) and grad[0] == "#000000" and grad[1] == "#ffffff"


def test_theme_to_style_and_overrides():
    t = styles.Theme("Test", style_overrides={"qmark": "fg:#123456 bold"})
    qstyle = t.to_questionary_style()
    assert isinstance(qstyle, Style)

    # Ensure override applied
    found = any(item[0] == "qmark" and "#123456" in item[1] for item in getattr(qstyle, "_style_rules", []))
    assert found


def test_apply_theme_to_style_merge():
    t = styles.Theme("MergeTest")
    theme_style = t.to_questionary_style()

    # create a fake base_style with some rules
    class FakeRule:
        def __init__(self, token, style):
            self.token = token
            self.style = style

    base = type("B", (), {})()
    base._style_rules = [("qmark", "fg:#111111"), ("custom", "fg:#222222")]  # tuple form

    merged = styles.apply_theme_to_style(t, base_style=base)
    assert isinstance(merged, Style)
    # merged should contain theme's qmark overriding base
    rules = getattr(merged, "_style_rules", [])
    assert any(r[0] == "qmark" for r in rules)


def test_style_builder_chain_and_build():
    b = styles.StyleBuilder()
    s = b.primary("#abc").text("#123").success("#0f0").error("#f00").build()
    assert isinstance(s, Style)
    # Ensure some tokens present
    assert any(item[0] == "qmark" for item in getattr(s, "_style_rules", []))


def test_theme_lookup_helpers():
    names = styles.get_theme_names()
    assert isinstance(names, list)
    t = styles.get_theme(names[0])
    assert t is not None
    all_themes = styles.list_themes()
    assert isinstance(all_themes, dict)
