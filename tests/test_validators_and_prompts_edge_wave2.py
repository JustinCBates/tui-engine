import questionary


class DocLike:
    def __init__(self, text):
        self.text = text


class FakeQ:
    def __init__(self, value="v"):
        self._v = value

    def ask(self, *a, **k):
        return self._v


def test_number_validator_success_and_errors():
    from questionary import ValidationError

    from questionary_extended.validators import NumberValidator

    v = NumberValidator(min_value=0, max_value=10, allow_float=False)

    # valid
    v.validate(DocLike("5"))

    # invalid non-numeric
    try:
        v.validate(DocLike("x"))
    except ValidationError:
        ok = True
    else:
        ok = False
    assert ok

    # out of range
    try:
        v.validate(DocLike("11"))
    except ValidationError:
        ok2 = True
    else:
        ok2 = False
    assert ok2


def test_date_validator_and_email_url():
    from questionary import ValidationError

    from questionary_extended.validators import (
        DateValidator,
        EmailValidator,
        URLValidator,
    )

    dv = DateValidator(format_str="%Y-%m-%d")
    dv.validate(DocLike("2020-01-01"))

    try:
        dv.validate(DocLike("bad"))
    except ValidationError:
        passed = True
    else:
        passed = False
    assert passed

    ev = EmailValidator()
    ev.validate(DocLike("me@example.com"))
    try:
        ev.validate(DocLike("notemail"))
    except ValidationError:
        eok = True
    else:
        eok = False
    assert eok

    uv = URLValidator()
    uv.validate(DocLike("http://example.com"))
    try:
        uv.validate(DocLike("notaurl"))
    except ValidationError:
        uok = True
    else:
        uok = False
    assert uok


def test_range_regex_length_choice_and_composite():
    from questionary import ValidationError

    from questionary_extended.validators import (
        ChoiceValidator,
        CompositeValidator,
        LengthValidator,
        RangeValidator,
        RegexValidator,
    )

    rv = RangeValidator(1, 3)
    rv.validate(DocLike("2"))
    try:
        rv.validate(DocLike("0"))
    except ValidationError:
        ok = True
    else:
        ok = False
    assert ok

    reg = RegexValidator(r"^a+$")
    reg.validate(DocLike("aa"))
    try:
        reg.validate(DocLike("b"))
    except ValidationError:
        ok2 = True
    else:
        ok2 = False
    assert ok2

    lv = LengthValidator(min_length=2, max_length=3)
    lv.validate(DocLike("ab"))
    try:
        lv.validate(DocLike("a"))
    except ValidationError:
        ok3 = True
    else:
        ok3 = False
    assert ok3

    cv = ChoiceValidator(["a", "b"], case_sensitive=False)
    cv.validate(DocLike("A"))
    try:
        cv.validate(DocLike("c"))
    except ValidationError:
        ok4 = True
    else:
        ok4 = False
    assert ok4

    composite = CompositeValidator([RegexValidator(r"^x+$")])
    try:
        composite.validate(DocLike("y"))
    except Exception:
        comp_ok = True
    else:
        comp_ok = False
    assert comp_ok


def test_tree_select_flattening_and_wizard_question_build(monkeypatch):
    from questionary_extended import prompts as prompts_mod

    data = {"A": {"B": ["one"]}, "C": "leaf"}
    # patch questionary.select used by tree_select
    monkeypatch.setattr(questionary, "select", lambda *a, **k: FakeQ("A/B/one"))

    q = prompts_mod.tree_select("Pick", data)
    assert q.ask() == "A/B/one"

    # test wizard converts ProgressStep to question dict
    class PS:
        def __init__(self, name):
            self.name = name

        def to_question_dict(self):
            return {"type": "text", "name": self.name, "message": "m"}

    monkeypatch.setattr(questionary, "prompt", lambda qs, **k: {"s": "v"})
    out = prompts_mod.wizard([PS("s")])
    assert out.get("s") == "v"
