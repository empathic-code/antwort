class Expression(object):
    def __str__(self):
        return type(self).__name__

    def walk(self, visitor, depth=0, context={}):
        visitor.pre(self, depth, context)
        self._children(visitor, depth, context)
        visitor.post(self, depth, context)

    def _children(self, visitor, depth, context):
        # Update the context on the way down.
        # This is used to provide data from deeply nested nodes
        # to other nodes on a similar level
        context = self._context(context)
        for key, attribute in self._properties().items():
            if isinstance(attribute, Expression):
                attribute.walk(visitor, depth + 1, context)
            elif hasattr(attribute, '__iter__'):
                for expression in attribute:
                    if not isinstance(expression, Expression):
                        continue
                    expression.walk(visitor, depth + 1, context)

    def _context(self, context):
        return context

    def _properties(self):
        return {key: value for key, value
                in self.__dict__.items()
                if not key.startswith('_')}


class QuestionListExpression(Expression):
    def __init__(self, question_expressions):
        self.questions = question_expressions


class QuestionExpression(Expression):
    def __init__(self, header_expression, option_expression):
        self.header = header_expression
        self.options = option_expression

    def _context(self, context):
        context.update({
            'identifier': self.header.variable.value,
            'required': self.header.required
        })
        return context


class QuestionHeadExpression(Expression):
    def __init__(self, number_expression, variable_expression, label_expression, required=False):
        self.number = number_expression
        self.variable = variable_expression
        self.explanation = label_expression
        self.required = required


class MatrixExpression(Expression):
    def __init__(self, scale_expression, list_expression):
        self.scale = scale_expression
        self.list = list_expression

    def _context(self, context):
        context.update({
            'scale': self.scale
        })
        return context


class CheckBoxListExpression(Expression):
    def __init__(self, checkbox_expressions):
        self.checkboxes = checkbox_expressions


class RadioListExpression(Expression):
    def __init__(self, checkbox_expressions):
        self.radios = checkbox_expressions


class InputFieldExpression(Expression):
    def __init__(self, placeholder_expression, lines, range_expression=None):
        self.placeholder = placeholder_expression
        self.lines = lines
        self.range = range_expression
        self.type = ('number' if range_expression else 'string')


class ListExpression(Expression):
    def __init__(self, element_expressions):
        self.elements = element_expressions


class MatrixListExpression(ListExpression):
    pass


class PlaceholderExpression(Expression):
    def __init__(self, placeholder, length):
        self.placeholder = placeholder
        self.length = int(length)


class RadioButtonExpression(Expression):
    def __init__(self, variable_expression):
        self.variable = variable_expression


class CheckBoxExpression(Expression):
    def __init__(self, variable_expression):
        self.variable = variable_expression


class MatrixElementExpression(Expression):
    def __init__(self, variable_expression):
        self.variable = variable_expression


class ElementExpression(Expression):
    def __init__(self, variable_expression):
        self.variable = variable_expression


class ScaleExpression(Expression):
    def __init__(self, step_expressions):
        self.steps = step_expressions


class VariableExpression(Expression):
    def __init__(self, label_expression, value_expression):
        self.label = label_expression
        self.value = value_expression


class RangeExpression(Expression):
    def __init__(self, _min, _max):
        self.min = _min
        self.max = _max


class IdentifierExpression(Expression):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class LabelExpression(Expression):
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


class NumberExpression(Expression):
    def __init__(self, value):
        self.value = int(value)

    def __str__(self):
        return str(self.value)