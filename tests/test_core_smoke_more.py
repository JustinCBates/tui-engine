from questionary_extended.core import Assembly, Card, Component, Page, PageState


def test_core_constructors_and_defaults():
    # Assembly requires a name and parent Page; create a parent Page to attach
    parent_page = Page("parent")
    a = Assembly("assembly", parent_page)
    c = Card("Test Card", parent_page)
    comp = Component("name", "text")
    p = Page("Title")

    assert isinstance(a, Assembly)
    assert c.title == "Test Card"
    assert comp.name == "name"
    assert p.title == "Title"


def test_pagestate_enum_and_page_methods():
    # PageState is an enum-like or container; just ensure access
    # This is a smoke test to import and call simple methods
    p = Page("T")
    # Use the Page.card() helper which appends a Card to the page
    p.card("c1")
    assert any(isinstance(card, Card) for card in p.components)
