class FakeQ:
    def __init__(self, value=None):
        self._value = value

    def ask(self, *args, **kwargs):
        return self._value


class DummyPrompt:
    def __init__(self, **kwargs):
        pass

    def ask(self):
        return "answer"


def test_questionary_bridge_asks_and_sets_state(monkeypatch):
    # Import here to use current package layout
    from questionary_extended.core.component import Component
    from questionary_extended.core.state import PageState
    from questionary_extended.integration.questionary_bridge import QuestionaryBridge

    ps = PageState()
    bridge = QuestionaryBridge(ps)

    # Create a simple component that maps to questionary.text
    comp = Component(name="field1", component_type="text", message="Enter:")

    # Monkeypatch the underlying questionary.text to return a FakeQ
    import questionary

    monkeypatch.setattr(questionary, "text", lambda **k: FakeQ("x"))

    ans = bridge.ask_component(comp)
    assert ans == "x"
    assert ps.get("field1") == "x"


def test_cli_quick_number_date_color_and_main_error(monkeypatch):
    # exercise quick number/date/color branches and main error handling
    from questionary_extended import cli as cli_mod
    from questionary_extended.cli import main

    # Quick: number -> monkeypatch number().ask() to return a number
    monkeypatch.setattr(cli_mod, "number", lambda *a, **k: FakeQ("123"))
    # cli imports date as 'date_prompt'
    monkeypatch.setattr(cli_mod, "date_prompt", lambda *a, **k: FakeQ("2020-01-01"))
    monkeypatch.setattr(cli_mod, "color", lambda *a, **k: FakeQ("#abcdef"))

    # Call quick for number
    cli_mod.quick.callback("number")
    # Call quick for date
    cli_mod.quick.callback("date")
    # Call quick for color
    cli_mod.quick.callback("color")

    # Now test main() handles KeyboardInterrupt gracefully by invoking cli that raises
    class BadCli:
        def __call__(self, *a, **k):
            raise KeyboardInterrupt()

    monkeypatch.setattr(cli_mod, "cli", BadCli())

    # CliRunner not needed; call main and ensure it exits with sys.exit(1) behavior

    try:
        main()
    except SystemExit as e:
        assert e.code == 1
