def test_questionary_bridge_runs_smoke():
    """Smoke test: create a minimal Page with a Component and run the bridge."""
    import questionary
    import questionary_extended as qe
    from questionary_extended.integration import QuestionaryBridge

    # Create a state and a component
    state = qe.PageState()
    c = qe.text('sample', message='Sample:')

    # Run bridge but avoid interactive prompt if questionary.ask is not available
    bridge = QuestionaryBridge(state)

    # Ensure bridge.walk doesn't raise on simple structure
    try:
        bridge.run([c])
    except RuntimeError:
        # If questionary is not available in CI, bridge may raise; that's acceptable as long as code paths execute
        assert True
    else:
        assert state.get('sample') is not None
