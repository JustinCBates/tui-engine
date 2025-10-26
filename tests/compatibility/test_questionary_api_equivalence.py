def test_questionary_and_qe_have_core_functions():
    """Ensure questionary and questionary_extended expose the same core prompt names."""
    import questionary

    import questionary_extended as qe

    core_names = [
        "text",
        "select",
        "confirm",
        "password",
        "checkbox",
        "autocomplete",
        "path",
    ]

    for name in core_names:
        assert hasattr(questionary, name), f"questionary missing {name}"
        # qe may expose wrappers under different names; check either root or core module
        has_qe = hasattr(qe, name) or hasattr(qe, f"{name}_component")
        assert has_qe, f"questionary_extended missing wrapper for {name}"
