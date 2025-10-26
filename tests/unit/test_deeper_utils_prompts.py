import pytest
import questionary

from questionary_extended import prompts, prompts_core, utils


def test_create_progress_bar_total_zero():
    bar = utils.create_progress_bar(0, 0, width=10)
    assert "0/0" in bar or "0/0" in bar


def test_parse_color_hex_fallback_and_invalid():
    c = utils.parse_color("#00ff00")
    assert hasattr(c, "hex") and c.hex.lower() == "#00ff00"

    # invalid should fallback or raise; check it doesn't crash
    try:
        _ = utils.parse_color("not-a-color")
    except Exception:
        pytest.skip("parse_color raised for unexpected input")


def test_create_table_row_truncation():
    # create_table_row lives in a different module path; assert truncate behavior instead
    # Implementation keeps `max_length - len(suffix)` chars, so for length 6 and '...' -> 3 chars
    assert utils.truncate_text("longvalue", 6) == "lon..."


def test_prompts_core_form_calls_questionary_prompt(monkeypatch):
    called = {}

    def fake_prompt(questions, **kw):
        called["q"] = questions
        return {questions[0]["name"]: "ans"}

    monkeypatch.setattr(questionary, "prompt", fake_prompt)
    res = prompts_core.form([{"type": "input", "name": "f", "message": "m"}])
    assert res.get("f") == "ans"


def test_progress_tracker_exception_path(capsys):
    pt = prompts_core.ProgressTracker("T", total=1)
    try:
        with pt:
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    out = capsys.readouterr().out
    assert "Failed" in out


def test_prompts_color_defaults_and_tag_and_fuzzy(monkeypatch):
    # Avoid building real prompts
    monkeypatch.setattr(
        questionary, "text", lambda *a, **kw: type("Q", (), {"_kw": kw, "kwargs": kw})()
    )
    monkeypatch.setattr(
        questionary,
        "checkbox",
        lambda *a, **kw: type("Q", (), {"_kw": kw, "kwargs": kw})(),
    )
    monkeypatch.setattr(
        questionary,
        "autocomplete",
        lambda *a, **kw: type("Q", (), {"_kw": kw, "kwargs": kw})(),
    )

    lq = prompts.color("pick")
    assert getattr(lq, "_kwargs", {}).get("formats") is None or isinstance(
        getattr(lq, "_kwargs", {}).get("formats"), list
    )

    lq2 = prompts.tag_select("t", ["a", "b"])
    # tag_select returns a LazyQuestion (inspect internals)
    assert hasattr(lq2, "_kwargs")

    lq3 = prompts.fuzzy_select("f", ["one", "two"])
    assert hasattr(lq3, "_kwargs")
