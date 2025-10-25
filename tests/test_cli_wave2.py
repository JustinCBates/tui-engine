from click.testing import CliRunner


class FakeQ:
    def __init__(self, value=None):
        self._value = value

    def ask(self, *args, **kwargs):
        return self._value


class FakeProgressTracker:
    def __init__(self, title, total_steps=None, total=None):
        self.title = title
        self.total_steps = total_steps
        self.current_step = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def step(self, description: str) -> None:
        self.current_step += 1

    def update(self, step: int, description: str) -> None:
        self.current_step = step

    def complete(self, message: str = "All steps completed!") -> None:
        pass


def test_cli_themes_command():
    from questionary_extended.cli import cli
    runner = CliRunner()
    result = runner.invoke(cli, ['themes'])
    assert result.exit_code == 0
    assert 'Available Themes' in result.output


def test_cli_form_builder_no_fields(monkeypatch):
    # Call the form_builder function directly to avoid Click parsing/execution issues
    from questionary_extended import cli as cli_mod
    import questionary

    # confirm().ask() should return False to end the loop immediately
    monkeypatch.setattr(questionary, 'confirm', lambda *a, **k: FakeQ(False))
    monkeypatch.setattr(questionary, 'text', lambda *a, **k: FakeQ(''))

    # Call the underlying click callback directly to avoid Click parsing
    cli_mod.form_builder.callback()


def test_cli_quick_text_and_select(monkeypatch):
    import questionary
    # Patch the cli module's reference to enhanced_text so quick() uses our stub
    from questionary_extended import cli as cli_mod

    monkeypatch.setattr(cli_mod, 'enhanced_text', lambda message, **k: FakeQ('hello'))
    # For select branch, stub questionary.select
    monkeypatch.setattr(questionary, 'select', lambda *a, **k: FakeQ('Option 1'))

    # Call the underlying function directly
    cli_mod.quick.callback('text')
    cli_mod.quick.callback('select')


def test_cli_wizard_demo(monkeypatch):
    from questionary_extended.cli import cli
    import questionary
    import questionary_extended.cli as cli_mod

    # Monkeypatch ProgressTracker in cli module
    monkeypatch.setattr(cli_mod, 'ProgressTracker', FakeProgressTracker)

    # questionary.text should return FakeQ values
    monkeypatch.setattr(questionary, 'text', lambda *a, **k: FakeQ('stepdata'))

    # Avoid sleeping
    import time
    monkeypatch.setattr(time, 'sleep', lambda s: None)

    # Call the underlying click callback directly
    cli_mod.wizard_demo.callback(2)
