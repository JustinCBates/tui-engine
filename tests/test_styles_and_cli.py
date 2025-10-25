from questionary_extended.styles import (
    ColorPalette,
    Theme,
    create_theme,
    create_gradient_palette,
    apply_theme_to_style,
    StyleBuilder,
    get_theme_names,
    get_theme,
)

from questionary_extended import cli
from click.testing import CliRunner


def test_theme_creation_and_gradient():
    palette = ColorPalette(primary="#111111")
    theme = create_theme("test", palette=palette, style_overrides={"qmark": "fg:#111"})
    s = theme.to_questionary_style()
    assert s is not None

    grad = create_gradient_palette("#000000", "#ffffff", steps=3)
    assert isinstance(grad, list) and len(grad) >= 2


def test_style_builder_and_apply():
    b = StyleBuilder().primary("#abc").text("#fff").success("#0f0").error("#f00")
    style = b.build()
    assert hasattr(style, "_style_rules")

    theme = get_theme("dark")
    merged = apply_theme_to_style(theme, base_style=style)
    assert hasattr(merged, "_style_rules")


def test_cli_themes_command():
    runner = CliRunner()
    result = runner.invoke(cli.cli, ["themes"])
    assert result.exit_code == 0
    assert "Available Themes" in result.output or "dark" in result.output
