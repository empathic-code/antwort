# encoding: utf-8
from nose.tools import *
from antwort.lexer import AntwortLexer
from antwort.token_ import *


def all_tokens(lexer):
    tokens = []
    token = lexer.next_token()
    while not token.is_a(EoF):
        tokens.append(token)
        token = lexer.next_token()
    tokens.append(token)
    return tokens


def print_expected(items):
    return "[%s]" % ', '.join([item.__name__ for item in items])


def print_actual(items):
    return "[%s]" % ', '.join([item.type() for item in items])


def throw(actual, expected):
    message = ("Sequence missmatch!\n"
               "Expected: %s\n"
               "but got : %s' ")
    message = message % (print_expected(expected), print_actual(actual))
    raise AssertionError(message)


def compare_sequence(actual, expected):
    if len(actual) != len(expected):
        throw(actual, expected)
    for token, expected_type in zip(actual, expected):
        if not token.is_a(expected_type):
            throw(actual, expected)


def test_asterisk():
    "Tokenize an asterisk *"
    string = "*"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Asterisk, EoF]
    compare_sequence(tokens, expected)


def test_number():
    "Tokenize a number 1123."
    string = "1123."
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Digits, Period, EoF]
    compare_sequence(tokens, expected)


def test_text():
    "Tokenize a text"
    string = "Hello, how are you doing?"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Text, EoF]
    compare_sequence(tokens, expected)


def test_text_with_umlaut():
    "Tokenize a text"
    string = u"Änderung"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Text, EoF]
    compare_sequence(tokens, expected)


def test_linebreak():
    "Tokenize a text with linebreaks"
    string = "Hello, how are you doing? \n Hello, I'm good, thank you!"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Text, LineBreak, Text, EoF]
    compare_sequence(tokens, expected)


def test_windows_line_breaks():
    "Tokenize a text with CRLF linebreaks"
    string = "Hello, how are you doing? \r\n Hello, I'm good, thank you!"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Text, LineBreak, Text, EoF]
    compare_sequence(tokens, expected)


def test_indentation():
    "Should ignore indentation in text"
    string = "\tHello"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Text, EoF]
    compare_sequence(tokens, expected)
    assert_equals(tokens[0].value, 'Hello')


def test_parens():
    "Tokenize identifier: (parenthesis)"
    string = "( text )"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Identifier, EoF]
    compare_sequence(tokens, expected)


def test_identifier():
    "Tokenize identifier with underscore: (under_score)"
    string = "( text_text )"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Identifier, EoF]
    compare_sequence(tokens, expected)


def test_identifier_with_type():
    "Tokenize identifier with underscore: (identifier)"
    string = "( identifier )"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Identifier, EoF]
    compare_sequence(tokens, expected)


def test_number_range():
    "Tokenize number range: (0-100)"
    string = "(0-100)"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Digits, Digits, EoF]
    compare_sequence(tokens, expected)


def test_number_with_spaces_range():
    "Tokenize number range: ( 0 - 100 )"
    string = "( 0 - 100 )"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Digits, Digits, EoF]
    compare_sequence(tokens, expected)


def test_brackets():
    "Tokenize a text in [brackets]"
    string = "[ text ]"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [LeftBracket, Text, RightBracket, EoF]
    compare_sequence(tokens, expected)


def test_braces():
    "Tokenize a text in {braces}"
    string = "{ text }"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [LeftBrace, Text, RightBrace, EoF]
    compare_sequence(tokens, expected)


def test_checkbox():
    "Tokenize a checkbox"
    string = "[] Hello"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [LeftBracket, RightBracket, Text, EoF]
    compare_sequence(tokens, expected)


def test_radio_buttons():
    "Tokenize a radio button"
    string = "() Hello"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Radio, Text, EoF]
    compare_sequence(tokens, expected)


def test_underscore():
    "Tokenize an underscore"
    string = "___"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Underscore, EoF]
    compare_sequence(tokens, expected)


def test_separator():
    "Tokenize an list separator --"
    string = "-- --"
    lexer = AntwortLexer(string)
    tokens = all_tokens(lexer)
    expected = [Separator, Separator, EoF]
    compare_sequence(tokens, expected)


def test_input_field():
    "Tokenize an input field (example)"
    _input = ("2. Alter (age)\n"
              "\t[__Alter__]")
    lexer = AntwortLexer(_input)
    tokens = all_tokens(lexer)
    expected = [Digits, Period, Text, Identifier, LineBreak,
                LeftBracket, Underscore, Text, Underscore, RightBracket, EoF]
    compare_sequence(tokens, expected)


def test_scale():
    "Tokenize a scale definition (example)"
    _input = ("{ Sehr gut (1) -- Gut (2) -- Befriedigend (3) }")
    lexer = AntwortLexer(_input)
    tokens = all_tokens(lexer)
    expected = [
        LeftBrace,

        Text,
        Identifier,

        Separator,

        Text,
        Identifier,

        Separator,

        Text,
        Identifier,

        RightBrace,
        EoF]
    compare_sequence(tokens, expected)
