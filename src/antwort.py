"""
Antwort

Usage:
    antwort.py [--template=<template>] [--in=INFILE] [--out=<outfile>] [--title=TITLE]

Options:
    --title=TITLE                       The title of the document
    -i INFILE, --in=INFILE              The input file written in the ANTWORT language
    -t TEMPLATE, --template=TEMPLATE    The template file that defines the transformations
    -o OUTFILE, --out=OUTFILE           Path of the file you would like to create
"""

import sys
import os
import codecs
import jinja2
from docopt import docopt


from antwort.lexer import AntwortLexer
from antwort.parser import AntwortParser
from antwort.expression import Expression


def parse(input):
    lexer = AntwortLexer(input)
    LOOKAHEAD = 2
    return AntwortParser(lexer, LOOKAHEAD).parse()


def read(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        return file.read()


def utf(path, content):
    with open(path, 'w') as file:
        file.write(content)


def remove_empty_lines(text):
    lines = text.split('\n')
    lines = [line for line in lines if line.strip()]
    return '\n'.join(lines)


def render(path, title, data):
    path, filename = os.path.split(path)
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path)
    ).get_template(filename)
    template = template.render(title=title, questions=data.questions)
    template = remove_empty_lines(template)
    return template


class Kwargs(object):
    def __init__(self, expression):
        self._expression = expression

    def __str__(self):

        fields = { key:value
                    for key, value in self._expression.__dict__.items()
                    if not key.startswith('_')
                    and not key == 'walk'
                    and not isinstance(value, Expression)
                }

        fields = [
            '%s=%s' % (key, value) for key,value in fields.items()
        ]
        return ', '.join(fields) + ','



class Constructor(object):
    def __init__(self, expression):
        self._expression = expression

    def __str__(self):
        return self._expression.__class__.__name__


class PythonVisitor(object):
        def pre(self, expression, depth, context):
            print('    ' * (depth), Constructor(expression), '(')
            print('    ' * (depth + 1), Kwargs(expression))

        def post(self, expression, depth, context):
            print('    ' * depth, ')')


def ast(data):
    data.walk(PythonVisitor())


# class String(object):
#     def __init__(self, string):
#         self.string = string

#     def decode(self, *args, **kwargs):
#         return self.string


if __name__ == '__main__':
    arguments = docopt(__doc__)

    infile = arguments['--in']
    content = (read(infile) if infile else sys.stdin.read())
    data = parse(content)

    title = arguments['--title']
    title = (title if title else "Questionnaire - generated with ANTWORT")

    templatepath = arguments['--template']
    if not templatepath:
        ast(data)

    else:
        document = render(templatepath, title, data)
        outfile = arguments['--out']
        if outfile:
            utf(outfile, document)
        else:
            sys.stdout.write(document)