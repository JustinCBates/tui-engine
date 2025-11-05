from typing import Any

from tui_engine.ptk_adapter import ApplicationWrapper


def test_applicationwrapper_has_invalidated_and_last_style() -> None:
    app = ApplicationWrapper()
    # declared attributes should exist and have sane defaults
    assert hasattr(app, "invalidated")
    assert app.invalidated is False
    assert hasattr(app, "_last_style")
    assert app._last_style is None


def test_applicationwrapper_key_bindings_and_container() -> None:
    app = ApplicationWrapper()
    assert hasattr(app, "_key_bindings")
    assert hasattr(app, "_container")
    assert app._key_bindings is None
    assert app._container is None
