from typing import Any

import pytest

from tui_engine import ptk_widget_factory


def _mk_elem(variant: str, name: str = "x", value: Any = None, options: Any = None) -> Any:
    e = type("E", (), {})()
    e.name = name
    e.variant = variant
    e.path = f"/{name}"
    e._value = value
    e.metadata = {}
    if options is not None:
        e.metadata['options'] = options
    return e


def test_factory_returns_adapters_when_available() -> None:
    # Require prompt-toolkit for these runtime widgets; if not installed skip
    try:
        import prompt_toolkit  # noqa: F401
    except Exception:
        pytest.skip("prompt-toolkit not available")

    descs = []

    # button
    b = _mk_elem('button', name='btn')
    b.on_click = lambda: None
    descs.append(('button', ptk_widget_factory.map_element_to_widget(b)))

    # input
    i = _mk_elem('input', name='inp', value='val')
    descs.append(('input', ptk_widget_factory.map_element_to_widget(i)))

    # radio/select
    opts = [('a', 'A'), ('b', 'B')]
    r = _mk_elem('radio', name='r', options=opts)
    descs.append(('radio', ptk_widget_factory.map_element_to_widget(r)))

    # checkbox_list
    c = _mk_elem('checkbox_list', name='c', options=opts)
    descs.append(('checkbox_list', ptk_widget_factory.map_element_to_widget(c)))

    # Verify that ptk_widget is non-None for all (PTK available) and
    # that it exposes the runtime `_tui_path` attribute at minimum.
    for kind, desc in descs:
        assert 'ptk_widget' in desc
        w = desc['ptk_widget']
        assert w is not None
        # The factory should apply _tui_path onto the underlying widget or
        # adapter wrapper. We accept either the adapter or raw widget but the
        # attribute must be present somewhere.
        found = False
        try:
            if hasattr(w, '_tui_path'):
                found = True
        except Exception:
            pass

        # Some adapters expose `.ptk_widget` which is the raw widget
        try:
            raw = getattr(w, 'ptk_widget', None)
            if raw is not None and hasattr(raw, '_tui_path'):
                found = True
        except Exception:
            pass

        assert found, f"widget for {kind} missing runtime _tui_path"
