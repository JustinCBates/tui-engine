import importlib.util
import os


def _load_utils_module():
    path = os.path.join(os.path.dirname(__file__), '..', 'src', 'questionary_extended', 'utils.py')
    path = os.path.abspath(path)
    # Load as a submodule of the package so relative imports work
    spec = importlib.util.spec_from_file_location('questionary_extended._utils_file', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_format_and_parse_number_and_date():
    u = _load_utils_module()
    assert u.format_number(1234, thousands_sep=True) == '1,234'
    assert u.parse_number('1,234') == 1234.0
    from datetime import date

    d = date(2020, 1, 2)
    assert u.format_date(d, '%Y-%m-%d') == '2020-01-02'
    assert u.parse_date('2020-01-02', '%Y-%m-%d') == d


def test_text_helpers_and_progress_bar():
    u = _load_utils_module()
    txt = 'hello world'
    assert u.truncate_text(txt, 5).endswith('...')
    wrapped = u.wrap_text('a b c', 2)
    assert isinstance(wrapped, list)
    assert u.center_text('a', 3) == ' a '

    bar = u.create_progress_bar(1, 4, width=4)
    assert '[' in bar and '1/4' in bar


def test_sanitize_and_fuzzy_and_validators():
    u = _load_utils_module()
    assert u.sanitize_input('abc\x00') == 'abc'
    matches = u.fuzzy_match('a', ['abc', 'b'])
    assert any(m[0] == 'abc' for m in matches)
    assert u.validate_email('x@y.com')
    assert not u.validate_email('notanemail')
    assert not u.validate_url('ftp://x')
    assert u.validate_url('http://example.com')


def test_generate_choices_from_range():
    u = _load_utils_module()
    choices = u.generate_choices_from_range(1, 3)
    assert choices == ['1', '2', '3']
