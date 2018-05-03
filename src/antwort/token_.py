# Underscore added to end of script name to prevent
# name shadowing of python's token module
# See
# http://python-notes.curiousefficiency.org/en/latest/python_concepts/import_traps.html#the-name-shadowing-trap

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

class Asterisk(Token): pass         # *
class Comma(Token): pass            # ,
class EoF(Token): pass              # EOF
class Identifier(Token): pass
class Indent(Token): pass           # \t
class LeftBrace(Token): pass        # {
class LeftBracket(Token): pass      # [
class LeftParenthesis(Token): pass  # (
class LineBreak(Token): pass        # \n
class Digits(Token):
    def __init__(self, value):
        super(Digits, self).__init__(int(value))
class Period(Token): pass           # .
class Radio(Token): pass            # ( )
class RightBrace(Token): pass       # }
class RightBracket(Token): pass     # ]
class RightParenthesis(Token): pass # )
class Separator(Token): pass        # --
class Text(Token): pass             # abcde123
class Underscore(Token): pass       # _