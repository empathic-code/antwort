from baselexer import Lexer
from antworttoken import *

from collections import namedtuple
Location = namedtuple('Location', ['Line', 'Position'])

class AntwortLexer(Lexer):
    def __init__(self, input_file):
        super(AntwortLexer, self).__init__(input_file)
        self._lines_counter = 0
        self._position_in_line = 0

    def location(self):
        return Location(self._lines_counter, self._position_in_line)

    def linebreak(self):
        self._position_in_line = 0
        self._lines_counter += 1
        self.consume()
        return LineBreak('\\n')

    def whitespace(self):
        while self.is_space(self._current_character):
            self.consume()

    def consume_while(self, test_fn):
        string = self._current_character
        self.consume()
        while test_fn(self._current_character):
            string += self._current_character
            self.consume()
        return string

    def text(self):
        string = self._current_character
        self.consume()
        while self.is_text(self._current_character) or self.is_digit(self._current_character):

            # handle escaping
            if self._current_character == '\\':
                self.consume() # Eat SLASH
                string += self._current_character
                self.consume() # EAT NEXT CHAR

            string += self._current_character
            self.consume()

        # don't strip!
        return Text(string.strip())

    def number(self):
        num = self.consume_while(self.is_digit)
        return Number(num)

    def underscore(self):
        score = self.consume_while(lambda c: c=='_')
        return Underscore(score)

    def is_identifier(self, c):
        c = str(c)
        return c in (self.letters + self.UNDERSCORE)

    def identifier(self):
        self.consume() # remove '('
        string = None
        self.whitespace()

        if self._current_character == ')':
            self.consume()
            return Radio('()')

        if self.is_digit(self._current_character):
            string = self.consume_while(self.is_digit)
            self.whitespace()
            if self._current_character == '-':
                return Number(string)

        elif self.is_identifier(self._current_character):
            string = self.consume_while(self.is_identifier)

        self.whitespace()
        self.match(')')
        return Identifier(string)

    def ident_post(self):
        return self.identifier()

    def separator(self):
        self.consume() # removes first -
        if self._current_character == '-':
            self.consume()
            return Separator('--')

        self.whitespace()
        if self.is_digit(self._current_character):
            token = self.number()
            self.whitespace()
            self.match(')')
            return token

        raise Exception('Invalid Character: %s' % self._current_character)

    def match_character(self, c):
        character_map = {
            '*': Asterisk,
            '.': Period,
            '[': LeftBracket,
            ']': RightBracket,
            '{': LeftBrace,
            '}': RightBrace,
        }
        token_ctor = character_map.get(c, None)
        if not token_ctor:
            raise Exception('Invalid Character: %s' % self._current_character)
        c = self._current_character
        self.consume()
        return token_ctor(c)

    def next_token(self):
        self._position_in_line += 1
        while self._current_character != Lexer.EOF:
            if self.is_space(self._current_character):
                self.whitespace()
                continue

            if self.is_linebreak(self._current_character):
                return self.linebreak()

            if self._current_character == '-':
                return self.separator()

            if self._current_character in '(':
                return self.identifier()

            if self.is_digit(self._current_character):
                return self.number()

            if self.is_letter(self._current_character):
                return self.text()

            if self._current_character == '_':
                return self.underscore()

            return self.match_character(self._current_character)
        return EoF('EOF')