import questionary


class FakeQ:
    def ask(self, *a, **k):
        return "v"


def test_confirm_select_checkbox_wrappers(monkeypatch):
    from questionary_extended import prompts_core as pc

    monkeypatch.setattr(questionary, "confirm", lambda *a, **k: FakeQ())
    monkeypatch.setattr(questionary, "select", lambda *a, **k: FakeQ())
    monkeypatch.setattr(questionary, "checkbox", lambda *a, **k: FakeQ())

    assert pc.confirm_enhanced("C").ask() == "v"
    assert pc.select_enhanced("S", choices=[]).ask() == "v"
    assert pc.checkbox_enhanced("CB", choices=[]).ask() == "v"


def test_progresstracker_exit_on_exception(capsys):
    from questionary_extended.prompts_core import ProgressTracker

    pt = ProgressTracker("T", total_steps=1)
    pt.__enter__()
    # Simulate an exception occurred
    pt.__exit__(ValueError, ValueError("err"), None)
    out = capsys.readouterr()
    assert "Failed" in out.out or "Failed" in out.err
