import asyncio

import pytest

from tui_engine.factories import text
from tui_engine.page import Page
from tui_engine.ptk_adapter import ApplicationWrapper, PTKAdapter


def test_wrap_with_visibility_returns_conditional_and_filter_works():
    try:
        # Build a small adapter and a real prompt-toolkit Window to wrap
        from prompt_toolkit.layout.containers import ConditionalContainer, Window
        from prompt_toolkit.layout.controls import FormattedTextControl
    except Exception:
        pytest.skip("prompt-toolkit not available; skipping ConditionalContainer test")

    p = Page("vis-test")
    c = p.container('c1')
    child = text('child', 'hidden child')
    # make child initially invisible
    child.visible = False
    c.add(child)

    adapter = PTKAdapter(p.root, p.page_state, p.events, app=ApplicationWrapper())

    # Ensure cached_visibility not set until wrap_with_visibility is used
    container = Window(content=FormattedTextControl('x'))
    wrapped = adapter.wrap_with_visibility(container, child.path)

    # Should return a ConditionalContainer when PTK is available
    assert isinstance(wrapped, ConditionalContainer)

    # cached_visibility path should have been defaulted to True by wrap_with_visibility
    assert child.path in adapter.cached_visibility

    # The filter should reflect the cached_visibility when evaluated
    # Access the filter attribute and call it if possible
    filt = getattr(wrapped, 'filter', None)
    assert filt is not None
    # When cached_visibility is True -> filter() should be True
    adapter.cached_visibility[child.path] = True
    assert bool(filt()) is True
    # When cached_visibility is False -> filter() should be False
    adapter.cached_visibility[child.path] = False
    assert bool(filt()) is False


def test_schedule_invalidate_triggers_app_invalidate():
    p = Page("invalidate-test")
    c = p.container('c2')
    child = text('child2', 'visible child', offset=0)
    child.visible = True
    c.add(child)

    app = ApplicationWrapper()
    adapter = PTKAdapter(p.root, p.page_state, p.events, app=app)

    # Monkeypatch app.invalidate to record calls
    def _mark():
        app.invalidated = True

    app.invalidated = False
    app.invalidate = _mark

    # Replace create_background_task to run coroutine synchronously
    def _run_sync(coro):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coro)
        finally:
            try:
                loop.close()
            except Exception:
                pass

    app.create_background_task = _run_sync

    # Ensure flag false initially
    assert not getattr(app, 'invalidated', False)

    # Schedule an invalidate; this should run the background coroutine
    adapter._invalidate_scheduled = False
    adapter._schedule_invalidate()

    # After scheduling, app.invalidated should be True
    assert getattr(app, 'invalidated', False) is True
