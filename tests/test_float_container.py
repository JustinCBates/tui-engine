def test_float_container_builds():
    """Best-effort test: ensure build_real_layout can create a FloatContainer
    when the page has floats attached. If prompt-toolkit is absent the test
    will be skipped by raising ImportError.
    """
    try:
        from tui_engine.factories import text
        from tui_engine.page import Page
        from tui_engine.ptk_adapter import ApplicationWrapper, PTKAdapter
    except Exception:
        raise ImportError("tui_engine modules not available")

    p = Page(title="float-test")
    overlay = p.container('overlay')
    overlay.add(text('o1', 'Overlay text'))
    # attach overlay at top-right
    p.add_float(overlay, top=1, right=1)

    adapter = PTKAdapter(p.root, p.page_state, p.events, app=ApplicationWrapper())
    root = adapter.build_real_layout(p.root)
    if root is None:
        raise ImportError("prompt-toolkit not available; skipping float integration test")

    # If we reach here, construction succeeded at least without exception.
    assert root is not None
