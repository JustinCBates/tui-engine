def test_frame_style_mapping():
    """Integration test: building a real PTK layout should register
    application-level style mappings containing the requested border colors.

    This test is best-effort: if prompt-toolkit is not available the adapter
    will return None and the test will be skipped by raising ImportError.
    """
    try:
        from tui_engine.page import Page
        from tui_engine.ptk_adapter import ApplicationWrapper, PTKAdapter
    except Exception:
        raise ImportError("Required tui_engine modules not available")

    p = Page(title="style-test")
    a = p.container('one')
    a.border = True
    a.border_color = '#aa0000'
    b = p.container('two')
    b.border = True
    b.border_color = '#00aa00'

    adapter = PTKAdapter(p.root, p.page_state, p.events, app=ApplicationWrapper())
    root = adapter.build_real_layout(p.root)

    # If prompt-toolkit is missing, build_real_layout returns None — skip
    if root is None:
        raise ImportError("prompt-toolkit not available; skipping PTK integration test")

    # The ApplicationWrapper stores the last style dict passed in _last_style
    s = getattr(adapter.app, '_last_style', None)
    assert isinstance(s, dict)
    vals = set(s.values())
    assert '#aa0000' in vals
    assert '#00aa00' in vals
    # ensure keys look like selectors with a '.border' suffix
    assert any(k.endswith('.border') for k in s.keys())
