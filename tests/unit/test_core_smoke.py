import pytest

from tests.conftest_questionary import setup_questionary_mocks


def test_core_api_importable():
    """Smoke test: ensure core API is importable from package root."""
    import questionary_extended as qe

    # Check core classes and convenience functions are available
    assert hasattr(qe, "Page")
    assert hasattr(qe, "Card")
    assert hasattr(qe, "Assembly")
    assert hasattr(qe, "text") or hasattr(qe, "text_component")


def test_page_card_assembly_run_smoke(monkeypatch):
    # Setup deterministic responses keyed by message strings
    responses = {
        "Enter name": "Alice",
        "Enter x": "42",
    }

    # Our mock factory looks for the exact message string; the component
    # default messages include a trailing ':' so tests should supply a
    # message matching the mapping above (without colon) or the mapping
    # can be adjusted. We'll pass explicit messages below matching keys.
    setup_questionary_mocks(monkeypatch, responses)

    import questionary_extended as qe

    page = qe.Page("Test")
    page.card("Basic").text("name", message="Enter name")
    page.assembly("a").text("x", message="Enter x")

    result = page.run()

    # The PageState flattens assembly value to 'a.x'
    assert result["name"] == "Alice"
    assert result["a.x"] == "42"
