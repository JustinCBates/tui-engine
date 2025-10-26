from pathlib import Path

from tests.helpers.test_helpers import load_module_from_path

# load core modules via helper so package and relative imports resolve correctly
state_mod = load_module_from_path(
    "questionary_extended.core.state",
    Path("src/questionary_extended/core/state.py").resolve(),
)

page_mod = load_module_from_path(
    "questionary_extended.core.page",
    Path("src/questionary_extended/core/page.py").resolve(),
)


def test_pagestate_namespace_and_clear():
    ps = state_mod.PageState()
    ps.set("x", 1)
    assert ps.get("x") == 1
    ps.set("asm.f", 2)
    assert ps.get("asm.f") == 2
    assert ps.get_assembly_state("asm")["f"] == 2
    allstate = ps.get_all_state()
    assert "asm.f" in allstate and allstate["x"] == 1
    assert ps.has_key("x")
    assert ps.has_key("asm.f")
    ps.clear_assembly("asm")
    assert not ps.has_key("asm.f")
    ps.clear_all()
    assert not ps.has_key("x")


def test_page_card_and_assembly_creation():
    pg = page_mod.Page("T")
    card = pg.card("C")
    assert card.title == "C"
    assert card in pg.components
    assembly = pg.assembly("A")
    assert assembly in pg.components
    # Card hide/show
    card.hide()
    assert card.visible is False
    card.show()
    assert card.visible is True


def test_card_select_standalone_notimplemented():
    """Test Card.select() raises NotImplementedError for standalone cards (lines 81-83)."""
    from unittest.mock import Mock

    import pytest

    # Create a mock parent that doesn't have 'state' attribute
    mock_parent_without_state = Mock(spec=[])  # Empty spec means no attributes

    # Import Card from core.card module
    from questionary_extended.core.card import Card

    # Create a standalone card with a parent that has no state
    card = Card("test_card", mock_parent_without_state)

    # Verify that the parent doesn't have state attribute
    assert not hasattr(card.parent_page, "state")

    # Attempting to use select() should raise NotImplementedError
    with pytest.raises(
        NotImplementedError,
        match="Card.select is not implemented for standalone Card instances",
    ):
        card.select("test_field", choices=["option1", "option2"])


def test_card_select_with_state_success():
    """Test Card.select() succeeds when parent has state (lines 85-89)."""
    from unittest.mock import Mock

    # Create a mock parent that HAS 'state' attribute
    mock_parent_with_state = Mock()
    mock_parent_with_state.state = Mock()  # Add state attribute

    # Import Card from core.card module
    from questionary_extended.core.card import Card

    # Create a card with a parent that has state
    card = Card("test_card", mock_parent_with_state)

    # Verify that the parent has state attribute
    assert hasattr(card.parent_page, "state")

    # This should succeed and not raise NotImplementedError
    result = card.select("test_field", choices=["option1", "option2"])

    # Verify the card was returned (method chaining)
    assert result is card

    # Verify a component was added
    assert len(card.components) == 1
