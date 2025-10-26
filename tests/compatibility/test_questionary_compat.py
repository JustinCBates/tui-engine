def test_import_questionary_and_qe():
    import questionary

    import questionary_extended as qe

    # Basic smoke test: API importability
    assert hasattr(questionary, "text")
    assert hasattr(qe, "Page") or hasattr(qe, "text")
