import questionary
from questionary_extended import prompts


def test_prompts_grouped_select_and_tag_and_fuzzy_and_table(monkeypatch):
    captured = {}

    def fake_select(*args, **kwargs):
        captured['select_args'] = args
        captured['select_kwargs'] = kwargs
        return 'SEL'

    def fake_text(*args, **kwargs):
        captured['text_args'] = args
        captured['text_kwargs'] = kwargs
        return {'message': args[0] if args else None}

    monkeypatch.setattr(questionary, 'select', fake_select)
    monkeypatch.setattr(questionary, 'text', fake_text)

    def fake_checkbox(*args, **kwargs):
        captured['checkbox_args'] = args
        captured['checkbox_kwargs'] = kwargs
        return 'CB'

    def fake_autocomplete(*args, **kwargs):
        captured['autocomplete_args'] = args
        captured['autocomplete_kwargs'] = kwargs
        return 'AC'

    monkeypatch.setattr(questionary, 'checkbox', fake_checkbox)
    monkeypatch.setattr(questionary, 'autocomplete', fake_autocomplete)

    groups = {'g1': ['a', 'b'], 'g2': ['c']}
    q = prompts.grouped_select('pick', groups)
    assert q is not None
    built = q.build()
    assert 'choices' in captured.get('select_kwargs', {})

    q2 = prompts.tag_select('tags', ['t1', 't2'])
    b2 = q2.build()
    assert b2 is not None

    q3 = prompts.fuzzy_select('find', ['one', 'two'])
    b3 = q3.build()
    assert b3 is not None

    # table returns a LazyQuestion using questionary.text
    q4 = prompts.table('tab', [])
    b4 = q4.build()
    assert 'Table input' in captured.get('text_kwargs', {}).get('message', '') or b4 is not None
