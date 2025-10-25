import questionary
from questionary_extended import prompts


def test_percentage_prompt_uses_number_validator(monkeypatch):
    # monkeypatch questionary.text to avoid prompt_toolkit
    monkeypatch.setattr(questionary, "text", lambda *a, **kw: type("Q", (), {"_kw": kw})())

    lq = prompts.percentage("pct")
    # validator should be present in LazyQuestion kwargs
    assert "validate" in lq._kwargs


def test_date_prompt_default_and_format_str(monkeypatch):
    monkeypatch.setattr(questionary, "text", lambda *a, **kw: type("Q", (), {"_kw": kw, "kwargs": kw})())

    import datetime as dt

    d = dt.date(2021, 12, 31)
    q = prompts.date("dob", default=d, format_str="%d/%m/%Y")
    # questionary.text should have default formatted using format_str
    assert getattr(q, "kwargs", {}).get("default") == d.strftime("%d/%m/%Y")


def test_enhanced_text_validator_propagation(monkeypatch):
    monkeypatch.setattr(questionary, "text", lambda *a, **kw: type("Q", (), {"_kw": kw})())

    def my_validator(text):
        return True

    lq = prompts.enhanced_text("hi", validator=my_validator)
    # some implementations use 'validate' while others forward as 'validator'
    assert "validate" in lq._kwargs or "validator" in lq._kwargs
