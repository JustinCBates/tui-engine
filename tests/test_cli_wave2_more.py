class FakeQ:
    def __init__(self, value=None):
        self._value = value

    def ask(self, *a, **k):
        return self._value


class FakeProgressTracker:
    def __init__(self, title, total_steps=None, total=None):
        self.title = title
        self.total_steps = total_steps

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def step(self, description: str) -> None:
        pass

    def update(self, step: int, description: str) -> None:
        pass

    def complete(self, message: str = "All steps completed!") -> None:
        pass


def test_cli_demo_and_quick_and_wizard(monkeypatch):
    from questionary_extended import cli as cli_mod

    # Patch ProgressTracker in cli module
    monkeypatch.setattr(cli_mod, 'ProgressTracker', FakeProgressTracker)

    # Patch interactive prompts used in demo
    monkeypatch.setattr(cli_mod, 'enhanced_text', lambda msg, **k: FakeQ('Alice'))
    monkeypatch.setattr(cli_mod, 'number', lambda msg, **k: FakeQ('30'))
    monkeypatch.setattr(cli_mod, 'date_prompt', lambda msg, **k: FakeQ('2020-01-01'))
    monkeypatch.setattr(cli_mod, 'tree_select', lambda msg, **k: FakeQ('Python'))
    monkeypatch.setattr(cli_mod, 'rating', lambda msg, **k: FakeQ(4))

    # Running demo callback directly
    cli_mod.demo.callback()

    # Quick: number branch
    cli_mod.number = lambda msg, **k: FakeQ('10')
    cli_mod.quick.callback('number')

    # Quick: color branch
    cli_mod.color = lambda msg, **k: FakeQ('#ff0000')
    cli_mod.quick.callback('color')

    # Wizard demo (use small steps and avoid sleep by monkeypatching time.sleep)
    import time
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    monkeypatch.setattr(cli_mod, 'ProgressTracker', FakeProgressTracker)
    # Patch questionary.text used inside wizard
    import questionary
    monkeypatch.setattr(questionary, 'text', lambda *a, **k: FakeQ('data'))
    cli_mod.wizard_demo.callback(steps=1)


def test_cli_form_builder_with_one_select_field(monkeypatch):
    from questionary_extended import cli as cli_mod
    import questionary

    # confirm should return True once (to add a field) then False
    seq = iter([True, False])

    def fake_confirm(*a, **k):
        return FakeQ(next(seq))

    # text responses: Field name, Field prompt, Choices input
    def fake_text(msg, **k):
        if 'Field name' in msg:
            return FakeQ('f1')
        if 'Field prompt' in msg:
            return FakeQ('Please choose')
        if 'Choices' in msg:
            return FakeQ('a,b')
        return FakeQ('')

    # select for field type -> return 'select'
    def fake_select(*a, **k):
        return FakeQ('select')

    monkeypatch.setattr(questionary, 'confirm', fake_confirm)
    monkeypatch.setattr(questionary, 'text', fake_text)
    monkeypatch.setattr(questionary, 'select', fake_select)

    # questionary.prompt should return results for the form
    monkeypatch.setattr(questionary, 'prompt', lambda questions, **k: {'f1': ['a', 'b']})

    # Call the form_builder callback directly
    cli_mod.form_builder.callback()
