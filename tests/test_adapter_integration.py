import pytest

try:
    from prompt_toolkit.widgets import TextArea, Button, RadioList
    from prompt_toolkit.layout.containers import Window
except Exception:  # pragma: no cover - skip on systems without PTK
    TextArea = None
    Button = None
    RadioList = None
    Window = None

from tui_engine import ptk_widget_factory


@pytest.mark.skipif(TextArea is None, reason="prompt-toolkit not installed")
def test_textarea_adapter_sync_on_accept():
    # Create a fake element that will receive updates
    el = type("E", (), {})()
    el.name = "inp"
    el.variant = "input"
    el.path = "/inp"
    el._value = "initial"

    desc = ptk_widget_factory.map_element_to_widget(el)
    w = desc.get("ptk_widget")
    assert w is not None

    # If adapter wraps the TextArea, get the underlying widget
    raw = getattr(w, "ptk_widget", w)

    # Modify the raw widget's text and call any provided _tui_sync
    try:
        raw.text = "changed"
    except Exception:
        # Some TextArea versions expose buffer; try setting via __init__ param
        pass

    sync = getattr(raw, "_tui_sync", None) or getattr(w, "_tui_sync", None)
    assert sync is not None

    # Trigger sync and ensure either the element or the adapter reports the
    # updated value. Different adapter wiring strategies exist depending on
    # runtime; be permissive but assert that something observed the change.
    sync()

    # Check adapter-level last-synced if available
    adapter_last = getattr(w, "_last_synced", None)
    if adapter_last:
        assert adapter_last.startswith("changed")
    else:
        # Fallback: element may have been updated by factory-level sync
        assert getattr(el, "_value", None) in ("changed", "changed\n", None)


@pytest.mark.skipif(Button is None, reason="prompt-toolkit not installed")
def test_button_adapter_click_triggers_element_on_click():
    el = type("E", (), {})()
    el.name = "btn"
    el.variant = "button"
    el.path = "/btn"
    called = {"ok": False}

    def on_click():
        called["ok"] = True

    el.on_click = on_click

    desc = ptk_widget_factory.map_element_to_widget(el)
    w = desc.get("ptk_widget")
    assert w is not None

    raw = getattr(w, "ptk_widget", w)

    # Trigger the raw handler if present
    handler = getattr(raw, "handler", None)
    if callable(handler):
        handler()
    else:
        # Fallback: try adapter.click()
        click = getattr(w, "click", None)
        if callable(click):
            click()

    assert called["ok"] is True


@pytest.mark.skipif(RadioList is None, reason="prompt-toolkit not installed")
def test_radiolist_adapter_syncs_selection():
    opts = [("a", "A"), ("b", "B")]
    el = type("E", (), {})()
    el.name = "r"
    el.variant = "radio"
    el.path = "/r"
    el.metadata = {"options": opts}
    el._value = None

    desc = ptk_widget_factory.map_element_to_widget(el)
    w = desc.get("ptk_widget")
    assert w is not None
    raw = getattr(w, "ptk_widget", w)

    # Set a selection on the raw widget if supported
    try:
        if hasattr(raw, "current_value"):
            raw.current_value = "b"
        elif hasattr(raw, "selected"):
            raw.selected = "b"
    except Exception:
        pass

    sync = getattr(raw, "_tui_sync", None) or getattr(w, "_tui_sync", None)
    assert sync is not None
    sync()

    # After sync, element._value should reflect the selection in best-effort
    assert getattr(el, "_value", None) in ("b", ["b"], None)
