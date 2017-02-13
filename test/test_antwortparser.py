#encoding: utf-8
from nose.tools import *
from antwortlexer import AntwortLexer
from antwortparser import AntwortParser

def assert_not_none(obj):
    assert_not_equal(obj, None)

mute = True
# call tests with -vs

def log(fn):
    if mute:
        return fn
    def w(*args, **kwargs):
        s = args[0]
        print(s.next())
        return fn(*args, **kwargs)
    return w

AntwortParser.match = log(AntwortParser.match)

def test_question_with_checkboxes():
    'Case: Matches a question with a checkbox'
    input_file = ("1. Geschlecht (gender)\n"
                  "[ ] Männlich (m)\n"
                  "[ ] Weiblich (w)\n"
                  "[ ] Andere (o)\n") # Careful: We need this newline at the end!
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    parser.question()

def test_question_with_checkboxes_and_explanation():
    'Case: Matches a question with checkboxes and optional explanatory text'
    input_file = ("1. Geschlecht (gender)\n"
                  "Sag mir, wie du dich fühlst!\n"
                  "[ ] Männlich (m)\n"
                  "[ ] Weiblich (w)\n"
                  "[ ] Andere (o)\n") # Careful: We need this newline at the end!
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    parser.question()

def test_two_questions_with_checkboxes():
    'Case: Matches two questions with checkboxes'
    input_file = ("1. Geschlecht (gender)\n"
                  "[ ] Männlich (m)\n"
                  "[ ] Weiblich (w)\n"
                  "\n"
                  "2. Student (student)\n"
                  "[ ] Ja (y)\n"
                  "[ ] Nein (n)\n")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    parser.questions()

def test_case_question_with_checkboxes():
    'Case: Question with checkboxes'
    input_file = """1. Geschlecht (gender)
    Sag mir, wie du dich fühlst!
    [ ] Männlich (m)
    [ ] Weiblich (w)
    [ ] Andere (o)
    """
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    parser.question()

def test_case_question_with_radio_buttons():
    'Case: Question with radios'
    input_file = """1. Geschlecht (gender)
    Sag mir, wie du dich fühlst!
    ( ) Männlich (m)
    ( ) Weiblich (w)
    ( ) Andere (o)
    """
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    parser.question()

def test_question_with_dropdown():
    'Case: Question with dropdown'
    input_file = """1. Wo wohnst du? (city)
    Bitte gib deinen jetzigen Wohnort an!
    [
        Heidelberg (HD)
        Mannheim (Ma)
    ]
    """
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    parser.question()

def test_question_with_input_field():
    'Case: Question with input_field'
    input_file = """1. Wo wohnst du? (city)
    Bitte gib deinen jetzigen Wohnort an!
    [__Wohnort__]
    """
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    parser.question()

def test_question_with_scale():
    'Case: Question with scale'
    input_file = """1. Wie glücklich bist du an deinem Wohnort? (happy)
    { Sau Geil (1) -- Geil (2) -- Nicht So Geil (3) }
    """
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    expression = parser.question()
    assert_not_none(expression.header)
    assert_not_none(expression.options)


def test_question_head():
    'Matches a question head: 1. Alter (age)'
    input_file = ("1. Alter (age)\n")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.question_head()
    assert_equal(expression.number.value, 1)
    assert_equal(expression.variable.label.text, 'Alter')
    assert_equal(expression.variable.value.name, 'age')
    assert_equal(expression.explanation, None)

def test_question_head_with_number():
    'Matches a question head that contains a number: 1. Hast du im Jahr 2013 schon einmal mitgemacht? (follow_up)'
    input_file = ("1. Hast du im Jahr 2013 schon einmal mitgemacht? (follow_up)\n")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.question_head()
    assert_equal(expression.number.value, 1)
    assert_equal(expression.variable.label.text, 'Hast du im Jahr 2013 schon einmal mitgemacht?')

def test_question_head():
    'Matches a question head with asterisk: 1. Alter (age) *'
    input_file = ("1. Alter (age) *\n")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.question_head()
    assert_equal(expression.number.value, 1)
    assert_equal(expression.variable.label.text, 'Alter')
    assert_equal(expression.variable.value.name, 'age')
    assert_equal(expression.required, True)
    assert_equal(expression.explanation, None)

def test_question_head_with_explanation():
    'Matches a question head with explanation: 1. Alter (age) \ Wie alt bist du?'
    input_file = ("1. Alter (age)\n"
                  "That explains many\n")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.question_head()
    assert_equal(expression.number.value, 1)
    assert_equal(expression.variable.label.text, 'Alter')
    assert_equal(expression.variable.value.name, 'age')
    assert_equal(expression.required, False)
    assert_equal(expression.explanation.text, 'That explains many')

def test_option_checkboxes():
    'Matches checkbox list'
    input_file = ("[ ] Männlich (m)\n"
                  "[ ] Weiblich (w)\n"
                  "[ ] Andere (o)\n")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.checkboxes()
    assert_equal(expression.checkboxes[0].variable.label.text, 'Männlich')
    assert_equal(expression.checkboxes[0].variable.value.name, 'm')
    assert_equal(expression.checkboxes[1].variable.label.text, 'Weiblich')
    assert_equal(expression.checkboxes[1].variable.value.name, 'w')
    assert_equal(expression.checkboxes[2].variable.label.text, 'Andere')
    assert_equal(expression.checkboxes[2].variable.value.name, 'o')

def test_option_radios():
    'Matches checkbox list'
    input_file = ("() Männlich (m)\n"
                  "() Weiblich (w)\n"
                  "() Andere (o)\n")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.radio_buttons()
    assert_equal(expression.radios[0].variable.label.text, 'Männlich')
    assert_equal(expression.radios[0].variable.value.name, 'm')
    assert_equal(expression.radios[1].variable.label.text, 'Weiblich')
    assert_equal(expression.radios[1].variable.value.name, 'w')
    assert_equal(expression.radios[2].variable.label.text, 'Andere')
    assert_equal(expression.radios[2].variable.value.name, 'o')

def test_option_radio():
    'Matches a radio button: '
    input_file = ("( ) Männlich (m)")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.radio()
    assert_equal(expression.variable.label.text, 'Männlich')
    assert_equal(expression.variable.value.name, 'm')

def test_option_checkbox():
    'Matches a checkbox: '
    input_file = ("[ ] Männlich (m)")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.checkbox()
    assert_equal(expression.variable.label.text, 'Männlich')
    assert_equal(expression.variable.value.name, 'm')

def test_input_field():
    'Matches an input field: [__test__] \ [__ __]'
    input_file = ("[__ placeholder __]\n"
                  "[_________________]")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    expression = parser.input_field()
    assert_equal(expression.placeholder.placeholder, 'placeholder')
    assert_equal(expression.placeholder.length, 2 + len('placeholder') + 2)
    assert_equal(expression.lines, 2)

def test_field():
    'Matches a field placeholder: [__test__]'
    input_file = "[__ placeholder __]"
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.field()
    assert_equal(expression.placeholder, 'placeholder')
    assert_equal(expression.length, 2 + len('placeholder') + 2)

def test_input_field_with_range():
    'Matches a field with range: [__test__] (1 - 5)'
    input_file = "[__ placeholder __] (1 - 999)"
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    expression = parser.input_field()
    assert_equal(expression.type, 'number')
    assert_equal(expression.range.min, 1)
    assert_equal(expression.range.max, 999)

def test_matrix():
    'Matches a matrix (Scale and List of Items)'
    input_file = """{ Sau Geil (1) -- Geil (2) -- Nicht So Geil (3) }
    [
        Mannheim (MA)
        Heidelberg (HD)
    ]
    """
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    expression = parser.options()
    assert_equal(expression.scale.steps[0].label.text, 'Sau Geil')
    assert_equal(expression.list.elements[0].variable.label.text, 'Mannheim')

def test_scale():
    'Matches a scale: { Sehr gut (1) -- Gut (2) }'
    input_file = ("{ Sehr gut (1) -- Gut (2) }")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.scale()
    assert_equal(expression.steps[0].label.text, 'Sehr gut')
    assert_equal(expression.steps[0].value.value, 1)
    assert_equal(expression.steps[1].label.text, 'Gut')
    assert_equal(expression.steps[1].value.value, 2)

def test_list():
    'Matches a list of items: [ A (a) \ B (b) ...]'
    input_file = ("[\n"
                  "Sehr gut (sg)\n"
                  "Gut (g)\n"
                  "]\n")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.list()
    assert_equal(expression.elements[0].variable.label.text, 'Sehr gut')
    assert_equal(expression.elements[0].variable.value.name, 'sg')
    assert_equal(expression.elements[1].variable.label.text, 'Gut')
    assert_equal(expression.elements[1].variable.value.name, 'g')

def test_element():
    'Matches an element in a list'
    input_file = "Sehr gut (sg)\n"
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.element()
    assert_equal(expression.variable.label.text, 'Sehr gut')
    assert_equal(expression.variable.value.name, 'sg')

def test_string_variable():
    'Matches a string variable: Hauptschule (hs)'
    input_file = ("Hauptschule (hs)")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.string_variable()
    assert_equal(expression.label.text, 'Hauptschule')
    assert_equal(expression.value.name, 'hs')

def test_string_variable():
    'Matches a number variable: Verhandlungssicher (5)'
    input_file = ("Verhandlungssicher (5)")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.number_variable()
    assert_equal(expression.label.text, 'Verhandlungssicher')
    assert_equal(expression.value.value, 5)

def test_numbering():
    'Matches a numbering: 123.'
    input_file = ("123.")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.numbering()
    assert_equal(expression.value, 123)

def test_identifier():
    'Matches an identifier: (m)'
    input_file = ("(m)")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.identifier()
    assert_equal(expression.name, 'm')

def test_range():
    'Matches a range: (1 - 2)'
    input_file = ("(1 - 2)")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.range()
    assert_equal(expression.min, 1)
    assert_equal(expression.max, 2)

def test_identifier_with_type_constraint():
    'Matches an identifier with type constraint: (m)'
    input_file = ("(m)")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 1)
    expression = parser.identifier()
    assert_equal(expression.name, 'm')

def test_identifire_with_underscores():
    'Matches an identifier with underscores: (years_active)'
    input_file = ("(years_active)")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    expression = parser.identifier()
    assert_equal(expression.name, 'years_active')

def test_value():
    'Matches a value: (12)'
    input_file = ("(12)")
    lexer = AntwortLexer(input_file)
    parser = AntwortParser(lexer, 2)
    expression = parser.number_value()
    assert_equal(expression.value, 12)