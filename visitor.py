#encoding: utf-8
from expression import *

PRETTY = True
TAB_WIDTH = 4

_ = nothing = lambda o,d,ctx: None

def indent(depth, width):
    return ((' ' * width) * depth if PRETTY else '')

def optional(template, key, value):
    value = str(value or '')
    if not value: return ''
    return template.format(**{key: value})

def identifier(ctx):
    return str(ctx['identifier'])

def required(ctx):
    if ctx and ctx.get('required', False):
        return 'required'
    return ''

''' 
Oooh, wow. Sorry, I have no idea what's wrong with me. The code here is really horrible. Clever but really complicated. 
After all, it is the first parser like program I ever wrote. 

In here you will find a visitor, that can be passed to the expression.walk method.
expression.walk does 3 things, it executes 
    - visitor.pre
    - Walks its children, passing them the visitor
    - visitor.post

The HTML Visitor visits each node and its pre and post visitation methods get executed. 
It looks into the 'make_html' map to see whether any transformation has been defined for 
the current node of the expression tree. It is a map of tuples that define pre and post as 
lambdas or a string for each node type. If a string is found it is simply returned. Like 
this I can just drop simple HTML Code.

Other Nodes require more complex actions. This is when I use a lambda.
The function receives the current expression, the depth within the tree (for formatting purposes)
and a context map. 

The first one is clear - this is where you find properties of the currently visited node.
The depth is an integer that you may increase for formatting purposes.
The CTX object is a map. Before descending into its children, each 'expression'-node 
may update the context. This is usefull for passing info between parent and child nodes without having 
to rewrite the whole tree. 
'''

def input_field_to_html(field, depth, ctx):
    if field.lines > 1:
        template = '<textarea name="{name}" placeholder="{placeholder}" rows="{rows}" {required}></textarea>'
        data = dict(
            name=str(ctx['identifier']), 
            placeholder=field.placeholder.placeholder, 
            rows=field.lines,
            required=required(ctx)
        )
    else:
        template = '<input name="{name}" placeholder="{placeholder}" type="{type}" {range} {required}>'
        data = dict(
            name=identifier(ctx), 
            placeholder=field.placeholder.placeholder, 
            type=('number' if field.type == 'number' else 'text'), 
            range=('min="%s" max="%s"' % (field.range.min, field.range.max) if field.type=='number' else ''),
            required=required(ctx)
        )
    return template.format(**data)

def matrix_header(scale, depth, ctx):
    html = '<thead><tr><th></th>\n'
    for step in scale.steps:
        html += '{indent}<th>{label}</th>\n'.format(
            indent=indent(depth+1, TAB_WIDTH),
            label=str(step.label)
        )
    html += '{indent}</tr></thead>'.format(
        indent=indent(depth, TAB_WIDTH)
    )
    return html

def radio_button(name, value, label, required):
    return '<input type="radio" name="{name}" value="{value}" {required}>{label}'.format(
        name=name,
        value=value,
        required=required,
        label=label,
    )

def matrix_row(element, depth, ctx):
    html = '<tr>\n{indent}<td>{name}</td>\n'.format(
        indent=indent(depth+1, TAB_WIDTH), 
        name=element.variable.label
    )
    for step in ctx['scale'].steps:
        radio = radio_button(
            name=element.variable.value,
            value=step.value,
            label='',
            required=required(ctx)
        )       
        html += '{indent}<td>{radio}</td>\n'.format(
            indent=indent(depth+1, TAB_WIDTH), 
            radio=radio, 
            label=step.label
        )
    html += "{indent}</tr>".format(
        indent=indent(depth, TAB_WIDTH)
    )
    return html

make_html = {
    QuestionListExpression: ('<html>','</html>'),
    QuestionExpression: ('<div>', '</div>'),
    QuestionHeadExpression: (
        lambda o,d,ctx: '<h2>{number}. {label}</h2>'.format(
            number=o.number, 
            label=o.variable.label
        ), 
        lambda o,d,ctx: optional('<blockquote>{explanation}</blockquote>', 'explanation', o.explanation)
    ),
    RadioButtonExpression: (
        lambda o,d,ctx: '<input type="radio" name="{name}" value="{value}" {required}>{label}'.format(
            name=identifier(ctx),
            value=o.variable.value,
            required=required(ctx),
            label=o.variable.label
        ), 
        _
    ),
    CheckBoxExpression: (
        lambda o,d,ctx: '<input type="checkbox" name="{name}" value="" {required}>{label}'.format(
            name=o.variable.value, 
            required=required(ctx),
            label=o.variable.label
        ), 
        _
    ),
    ListExpression: (
        lambda o,d,ctx: '<select name="{name}" {required}><option selected="selected" value="">Bitte auswählen</option>'.format(
            name=identifier(ctx), 
            required=required(ctx)
        ),
        '</select>'
    ),
    ElementExpression: (
        lambda o,d,ctx: '<option value="{value}">{label}</option>'.format(
            value=o.variable.value, 
            label=o.variable.label
        ),
        _
    ),
    MatrixExpression:           ('<table>', '</table>'),
    MatrixListExpression:       ('<tbody>', '</tbody>'),
    MatrixElementExpression:    (matrix_row, _),
    ScaleExpression:            (matrix_header, _),
    InputFieldExpression:       (input_field_to_html, _),
}

class Visitor(object):
    def pre(self, object, depth, ctx): pass
    def post(self, object, depth, ctx): pass

class PlainVisitor(Visitor):
    def pre(self, object, depth, ctx):
        print ('\t' * depth) + type(object).__name__

class HtmlVisitor(Visitor):
    def __init__(self, tab_with = TAB_WIDTH):
        self.buff = ''
        assert tab_with > 0
        self.tab_with = tab_with

    def pre(self, expression, depth, context):
        actions = self._get_action(expression, depth, context)
        action = actions[0]
        tag = self._invoke(action, expression, depth, context)
        self._append(tag, depth)
    
    def post(self, expression, depth, context): 
        actions = self._get_action(expression, depth, context)
        action = actions[1]
        tag = self._invoke(action, expression, depth, context)
        self._append(tag, depth)

    def _get_action(self, expression, depth, context):
        no_actions = (_,_)
        key = type(expression)
        actions = make_html.get(key, no_actions)
        return actions

    def _invoke(self, action, expression, depth, context):
        if isinstance(action, basestring):
            return action
        return action(expression, depth, context)

    def _append(self, message, depth):
        if not message: 
            return
        global PRETTY
        if PRETTY:
            self.buff += '\n' + (' ' * self.tab_with * depth)
        self.buff += message