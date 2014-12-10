import sys
from antwortlexer import *
from antwortparser import *
from visitor import *

class AntwortTestParser(AntwortParser):
    def __init__(self, input):
        lexer = AntwortLexer(input)
        LOOKAHEAD = 2
        super(AntwortTestParser, self).__init__(lexer, LOOKAHEAD)

if __name__ == '__main__':
    stdin = sys.stdin.read()
    parser = AntwortTestParser(stdin)
    tree = parser.parse()
    visitor = HtmlVisitor()
    tree.walk(visitor)
    print visitor.buff.decode('utf-8').encode('cp1252')