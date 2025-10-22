def test_core_api_importable():
    """Smoke test: ensure core API is importable from package root."""
    import questionary_extended as qe

    # Check core classes and convenience functions are available
    assert hasattr(qe, 'Page')
    assert hasattr(qe, 'Card')
    assert hasattr(qe, 'Assembly')
    # component convenience functions
    assert hasattr(qe, 'text') or hasattr(qe, 'text_component')
