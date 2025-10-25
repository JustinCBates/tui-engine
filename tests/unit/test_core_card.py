import pytest

from src.questionary_extended.core.card import Card


class DummyPage:
    pass


def test_card_init_defaults():
    p = DummyPage()
    c = Card("My Card", p)

    assert c.title == "My Card"
    assert c.parent_page is p
    assert c.style == "minimal"
    assert c.components == []
    assert c.visible is True


def test_card_custom_style_and_components():
    p = DummyPage()
    c = Card("T", p, style="bordered")

    assert c.style == "bordered"
    # components list should be mutable and start empty
    c.components.append("comp")
    assert c.components == ["comp"]


def test_show_hide_and_parent():
    p = DummyPage()
    c = Card("x", p)

    c.hide()
    assert c.visible is False

    c.show()
    assert c.visible is True

    assert c.parent() is p


def test_text_raises_not_implemented():
    p = DummyPage()
    c = Card("x", p)

    with pytest.raises(NotImplementedError):
        c.text("name")


def test_select_raises_not_implemented():
    p = DummyPage()
    c = Card("x", p)

    with pytest.raises(NotImplementedError):
        c.select("name", ["a", "b"])


def test_page_card_integration_append():
    # Import Page lazily via core.page to exercise the factory path
    from src.questionary_extended.core.page import Page

    page = Page("Title")
    card = page.card("Header")

    # card should be a Card and appended to page.components
    from src.questionary_extended.core.card import Card as CardClass

    assert isinstance(card, CardClass)
    assert card in page.components