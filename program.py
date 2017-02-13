"""
Antwort

Usage:
    program.py --template=<template> [--in=INFILE] [--out=<outfile>] [--title=TITLE]

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

from antwortlexer import AntwortLexer
from antwortparser import AntwortParser

def parse(input):
    lexer = AntwortLexer(input)
    LOOKAHEAD = 2
    return AntwortParser(lexer, LOOKAHEAD).parse()

#open = open
def read(path):
    with codecs.open(path, 'r', encoding='utf-8') as file:
        return file.read()

def write_utf(path, content):
    with open(path, 'w') as file:
        file.write(content)

def remove_empty_lines(text):
    lines = text.split('\n')
    lines = [line for line in lines if line.strip()]
    return '\n'.join(lines)

def transform(path, title, data):
    path, filename = os.path.split(path)
    template = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path)
        ).get_template(filename)
    template = template.render(title=title, questions=data.questions)
    template = remove_empty_lines(template)
    return template

class String(object):
    def __init__(self, string):
        self.string = string

    def decode(self, *args, **kwargs):
        return self.string

if __name__ == '__main__':
    arguments = docopt(__doc__)

    infile = arguments['--in']
    content = (read(infile) if infile else sys.stdin.read())
    data = parse(content)

    title = arguments['--title']
    title = (title if title else "Questionnaire - generated with ANTWORT")

    templatepath = arguments['--template']
    #template = read(template)
    template = transform(templatepath, title, data)

    outfile = arguments['--out']
    if outfile:
        write_utf(outfile, template)
    else:
        sys.stdout.write(template)