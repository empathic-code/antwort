"""
Antwort

Usage: 
    my_program --template=<template> [--in=INFILE] [--out=<outfile>] [--title=TITLE]

Options:
    --title=TITLE                       The title of the document
    -i INFILE, --in=INFILE              The input file written in the ANTWORT language
    -t TEMPLATE, --template=TEMPLATE    The template file that defines the transformations
    -o OUTFILE, --out=OUTFILE           Path of the file you would like to create
"""

import sys
import codecs
from jinja2 import Template
from docopt import docopt

from antwortlexer import AntwortLexer 
from antwortparser import AntwortParser

def parse(input):
    lexer = AntwortLexer(input)
    LOOKAHEAD = 2
    return AntwortParser(lexer, LOOKAHEAD).parse()

#open = open
def read(path):
    with open(path, 'r') as file:
        return file.read()

def read_utf(path):
    with codecs.open(path,'r','utf-8') as file:
        return file.read()

def write_utf(path, content):
    with codecs.open(path,'w', 'utf-8-sig') as file: 
        file.write(content)

def remove_empty_lines(text):
    lines = text.split('\n')
    lines = [line for line in lines if line.strip()]
    return '\n'.join(lines)

def transform(template, title, data):
    template = Template(template)
    template = template.render(title=title, questions=data.questions)
    template = remove_empty_lines(template)
    return template

if __name__ == '__main__':
    arguments = docopt(__doc__)

    infile = arguments['--in']
    content = (read(infile) if infile else sys.stdin.read())
    data = parse(content)

    title = arguments['--title']
    title = (title if title else "Questionnaire - generated with ANTWORT")

    template = arguments['--template']
    template = read_utf(template)
    template = transform(template, title, data)

    outfile = arguments['--out']
    if outfile:
        write_utf(outfile, template)
    else:
        sys.stdout.write(template)