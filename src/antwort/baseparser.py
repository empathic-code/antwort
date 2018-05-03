# encoding: utf-8
"""
I apologize for the name of this module. 'base' is just another weasel word.
I would have called it parser, but Python started bitching because there already is a parser.py module in the standard lib.
"""


class UnexpectedTokenException(Exception):
    pass


class BaseParser(object):
    def __init__(self, lexer, k):
        self._lexer = lexer
        self._k = k
        self._markers = []
        self._p = 0
        self.lookahead = [None] * self._k
        for i in range(k):
            self.consume()  # Prime lookahead

    def consume(self):
        self._p += 1
        if self._p == len(self.lookahead) and not self.is_speculating():
            self._p = 0
            self.lookahead = []
        self.sync(1)

    def mark(self):
        self._markers.append(self._p)
        return self._p

    def release(self):
        marker = self._markers.pop()
        self.seek(marker)

    def seek(self, index):
        self._p = index

    def is_speculating(self):
        return len(self._markers) > 0

    def sync(self, i):
        if (self._p + i - 1) > (len(self.lookahead) - 1):
            n = (self._p + i - 1) - (len(self.lookahead) - 1)
            self.fill(n)

    def fill(self, n):
        for i in range(n):
            self.lookahead.append(self._lexer.next_token())

    # Look Ahead Token
    def LT(self, i):
        if i > self._k:
            raise Exception("Trying to look further than the buffer can see")
        self.sync(i)
        return self.lookahead[(self._p + i - 1) % self._k]

    def next(self):
        return self.LT(1)

    def peek(self, token_type):
        return self.next().is_a(token_type)

    def peek_at(self, i, token_type):
        return self.LT(i).is_a(token_type)

    def unexpected_token(self, token_type):
        message = ('\nError: Expecting <%s> but found <%s>\n')
        message = message % (token_type.__name__, self.next().type())
        raise UnexpectedTokenException(message)

    def match(self, token_type):
        if self.next().is_a(token_type):
            self.consume()
        else:
            self.unexpected_token(token_type)

    def match_all(self, *args):
        for arg in args:
            self.match(arg)
