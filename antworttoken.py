class Token(object):
    def __init__(self, value=None):
        self.value = value

    def type(self):
        return type(self).__name__

    def is_a(self, token_type):
        return isinstance(self, token_type)

    def __str__(self):
        name = self.type().upper()
        return "<'%s', %s>" % (name, self.value or name)

    def __repr__(self):
        return str(self)

class Text(Token): pass
class Identifier(Token): pass
class Number(Token):
    def __init__(self, value):
        super(Number, self).__init__(int(value))

class Radio(Token): pass            # ( )
class Underscore(Token): pass       # _
class Separator(Token): pass        # --
class Asterisk(Token): pass         # *
class Comma(Token): pass            # .
class Period(Token): pass           # .
class LeftParenthesis(Token): pass  # (
class RightParenthesis(Token): pass # )
class LeftBracket(Token): pass      # [
class RightBracket(Token): pass     # ]
class LeftBrace(Token): pass        # {
class RightBrace(Token): pass       # }
class LineBreak(Token): pass        # \n
class Indent(Token): pass           # \t
class EoF(Token): pass              # EOF