"""
Tests for styles.py to improve coverage to 95%+

This test file targets the missing coverage lines:
- Line 190: apply_theme_to_style with base_style=None
- Lines 211-212: Style rule parsing with token/style attributes
- Lines 225-226: StyleBuilder.set() method
- Line 276: list_themes() function
"""

from unittest.mock import Mock

from prompt_toolkit.styles.style import Style

from questionary_extended import styles


def test_apply_theme_to_style_no_base_style():
    """Test apply_theme_to_style when base_style is None (line 190)."""
    # Create a simple theme
    palette = styles.ColorPalette(primary="#ff0000", success="#00ff00")
    theme = styles.Theme(name="test_theme", palette=palette)

    # Call apply_theme_to_style with base_style=None
    result_style = styles.apply_theme_to_style(theme, base_style=None)

    # Should return the theme's questionary style directly
    assert isinstance(result_style, Style)
    # The function should return early at line 190


def test_apply_theme_to_style_with_token_style_attributes():
    """Test apply_theme_to_style with rules having token/style attributes (lines 211-212)."""
    # Create a theme
    palette = styles.ColorPalette(primary="#ff0000")
    theme = styles.Theme(name="test_theme", palette=palette)

    # Create a mock base style with rules that have token/style attributes
    mock_rule = Mock()
    mock_rule.token = "test_token"
    mock_rule.style = "fg:blue bold"  # Use valid style format

    mock_base_style = Mock(spec=Style)
    mock_base_style._style_rules = [mock_rule]

    # Call apply_theme_to_style - this should trigger lines 211-212
    result_style = styles.apply_theme_to_style(theme, base_style=mock_base_style)

    assert isinstance(result_style, Style)


def test_style_builder_set_method():
    """Test StyleBuilder.set() method (lines 225-226)."""
    builder = styles.StyleBuilder()

    # Call the set method to cover lines 225-226
    result = builder.set("test_token", "fg:blue bold")

    # Should return self for chaining (line 226)
    assert result is builder
    # Should set the style in the internal dict (line 225)
    assert builder.styles["test_token"] == "fg:blue bold"


def test_list_themes_function():
    """Test list_themes() function (line 276)."""
    # Call list_themes to cover line 276
    themes_dict = styles.list_themes()

    # Should return a copy of THEMES dict
    assert isinstance(themes_dict, dict)
    assert len(themes_dict) > 0  # Should contain some built-in themes

    # Verify it's a copy by modifying it
    original_len = len(styles.THEMES)
    themes_dict.clear()
    # Original THEMES should be unchanged
    assert len(styles.THEMES) == original_len


def test_style_builder_chaining():
    """Additional test to verify StyleBuilder method chaining works."""
    builder = styles.StyleBuilder()

    # Chain multiple calls including set()
    result = (
        builder.set("custom_token", "fg:purple").primary("#ff0000").success("#00ff00")
    )

    assert result is builder
    assert "custom_token" in builder.styles
    assert builder.styles["custom_token"] == "fg:purple"

    # Build the final style
    final_style = builder.build()
    assert isinstance(final_style, Style)


def test_theme_integration():
    """Integration test to ensure themes work with apply_theme_to_style."""
    # Create custom palette and theme
    palette = styles.ColorPalette(primary="#1a1a1a", success="#28a745", error="#dc3545")
    theme = styles.Theme(name="custom_test", palette=palette)

    # Test with None base style (line 190)
    style1 = styles.apply_theme_to_style(theme)
    assert isinstance(style1, Style)

    # Test with empty base style
    empty_style = Style([])
    style2 = styles.apply_theme_to_style(theme, empty_style)
    assert isinstance(style2, Style)


def test_create_theme_function():
    """Test create_theme function (line 169)."""
    # Test with all parameters
    palette = styles.ColorPalette(primary="#ff0000")
    overrides = {"custom": "fg:blue"}

    theme = styles.create_theme("test", palette=palette, style_overrides=overrides)

    assert theme.name == "test"
    assert theme.palette is palette
    assert theme.style_overrides is overrides


def test_create_gradient_palette():
    """Test create_gradient_palette function (line 182)."""
    # Test the gradient palette creation
    gradient = styles.create_gradient_palette("#ff0000", "#00ff00", 3)

    # Should return a list with start and end colors (placeholder implementation)
    assert isinstance(gradient, list)
    assert len(gradient) == 2
    assert gradient[0] == "#ff0000"
    assert gradient[1] == "#00ff00"


def test_style_builder_all_methods():
    """Test all StyleBuilder methods to improve coverage."""
    builder = styles.StyleBuilder()

    # Test all builder methods (lines 241-242, 256-257, 266, 271)
    result = (
        builder.primary("#ff0000")  # lines 241-242
        .text("#ffffff")  # line 256
        .success("#00ff00")  # lines 256-257
        .error("#ff0000")
    )  # line 266

    assert result is builder

    # Verify the styles were set
    assert "qmark" in builder.styles
    assert "text" in builder.styles
    assert "answer" in builder.styles
    assert "validation_error" in builder.styles

    # Build final style (line 271)
    final_style = builder.build()
    assert isinstance(final_style, Style)


def test_get_theme_names():
    """Test get_theme_names function."""
    names = styles.get_theme_names()
    assert isinstance(names, list)
    assert len(names) > 0


def test_get_theme():
    """Test get_theme function."""
    # Get available theme names first
    names = styles.get_theme_names()
    if names:
        # Test getting an existing theme
        theme = styles.get_theme(names[0])
        assert isinstance(theme, styles.Theme)

        # Test getting non-existent theme
        none_theme = styles.get_theme("nonexistent")
        assert none_theme is None


def test_apply_theme_with_tuple_rules():
    """Test apply_theme_to_style with tuple-based style rules (lines 200-201)."""
    # Create theme
    palette = styles.ColorPalette(primary="#ff0000")
    theme = styles.Theme(name="test_theme", palette=palette)

    # Create base style with tuple rules
    base_style = Style([("test_token", "fg:blue bold")])

    # This should exercise the tuple handling code in lines 200-201
    result_style = styles.apply_theme_to_style(theme, base_style=base_style)

    assert isinstance(result_style, Style)


def test_apply_theme_with_short_tuple():
    """Test apply_theme_to_style with short tuple rules to test edge cases."""
    # Create theme
    palette = styles.ColorPalette(primary="#ff0000")
    theme = styles.Theme(name="test_theme", palette=palette)

    # Create a mock style with short tuples (less than 2 elements)
    mock_base_style = Mock(spec=Style)
    mock_base_style._style_rules = [("single_element",)]  # Short tuple

    # This should test the tuple length check
    result_style = styles.apply_theme_to_style(theme, base_style=mock_base_style)

    assert isinstance(result_style, Style)
