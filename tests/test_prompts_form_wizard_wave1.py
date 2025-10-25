import questionary
from questionary_extended import prompts
from questionary_extended.components import ProgressStep


def test_prompts_form_and_wizard_and_color(monkeypatch):
    captured = {}

    def fake_prompt(questions, **kwargs):
        captured['questions'] = questions
        return {'ok': True}

    def fake_text(message, **kwargs):
        captured['text_message'] = message
        return {'message': message}

    monkeypatch.setattr(questionary, 'prompt', fake_prompt)
    monkeypatch.setattr(questionary, 'text', fake_text)

    # form should call questionary.prompt
    out = prompts.form([{'type': 'text', 'name': 'a', 'message': 'm'}])
    assert out == {'ok': True}

    # wizard converts steps to questions then prompts
    steps = [ProgressStep(name='s1', description='d1')]
    out2 = prompts.wizard(steps)
    assert out2 == {'ok': True}

    # color with default formats
    c = prompts.color('pick')
    # color returns a Question (our fake_text returns dict)
    built = c
    assert built is not None
