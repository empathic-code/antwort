#encoding: utf-8
from baseparser import Parser, UnexpectedTokenException
from expression import *
from antworttoken import *

class UnexpectedTypeConstraint(Exception): pass

class AntwortParser(Parser):
    def __init__(self, lexer, lookahead_size):
        super(AntwortParser, self).__init__(lexer, lookahead_size)

    def match(self, token_type):
        token = self.next()
        super(AntwortParser, self).match(token_type)
        return token

    def unexpected_token(self, token_type):
        message = ('\nError: Expecting <%s> but found <%s>\n'
                   'At   : Line %s, Position %s')
        line, position = self._lexer.location()
        message = message % ( token_type, self.next().type(), line + 1, position)
        raise UnexpectedTokenException(message)

    def unexpected_constraint(self, constraint):
        message = ('Unexpected Type Constraint: Expecting "number" or "string" but found <%s>\n'
                   'At   : Line %s, Position %s')
        line, position = self._lexer.location()
        message = message % ( constraint, line + 1, position)
        raise UnexpectedTypeConstraint(message)

    def parse(self):
        return self.questions()

    def questions(self):
        questions = []
        question = self.question()
        questions.append(question)
        while self.peek(LineBreak):
            self.consume()
        while self.peek(Number):
            question = self.question()
            questions.append(question)
            while self.peek(LineBreak):
                self.consume()
        return QuestionListExpression(questions)

    def question(self):
        header = self.question_head()
        options = self.options()
        return QuestionExpression(header, options)

    def question_head(self):
        number = self.numbering()
        variable = self.string_variable()

        required = False
        if self.peek(Asterisk):
            required = True
            self.match(Asterisk)

        self.match(LineBreak)
        explanation = None
        if self.peek(Text):
            explanation = self.explanation()

        return QuestionHeadExpression(number, variable, explanation, required)

    def explanation(self):
        text = self.match(Text)
        self.match(LineBreak)
        return LabelExpression(text.value)

    def options(self):
        # ( ) Item
        if self.peek(Radio):
            return self.radio_buttons()
        # [ ] Item
        elif self.peek(LeftBracket) and self.peek_at(2, RightBracket):
            return self.checkboxes()
        # [ A \ B \ C ]
        elif self.peek(LeftBracket) and self.peek_at(2, LineBreak):
            return self.list()
        # [__ blah __ ]
        elif self.peek(LeftBracket) and self.peek_at(2, Underscore):
            return self.input_field()
        # { A (1) -- B (2) }
        elif self.peek(LeftBrace):
            scale = self.scale()
            # Optional List of Items [ ... ]
            if self.peek(LineBreak) and self.peek_at(2, LeftBracket):
                self.consume() # kill linebreak
                items = self.matrixlist()
                return MatrixExpression(scale, items)
            return scale
        else:
            self.unexpected_token(self.next())

    def checkboxes(self):
        checkboxes = []
        # At least one
        checkbox = self.checkbox()
        checkboxes.append(checkbox)
        self.match(LineBreak)
        while self.next().is_a(LeftBracket):
            checkbox = self.checkbox()
            checkboxes.append(checkbox)
            self.match(LineBreak)
        return CheckBoxListExpression(checkboxes)

    def checkbox(self):
        self.match(LeftBracket)
        self.match(RightBracket)
        variable = self.string_variable()
        return CheckBoxExpression(variable)

    def radio_buttons(self):
        radios = []
        # At least one
        radio = self.radio()
        radios.append(radio)
        self.match(LineBreak)
        while self.next().is_a(Radio):
            radio = self.radio()
            radios.append(radio)
            self.match(LineBreak)
        return RadioListExpression(radios)

    def radio(self):
        self.match(Radio)
        variable = self.string_variable()
        return RadioButtonExpression(variable)

    def input_field(self):
        placeholder = self.field()

        _range = None
        if self.peek(Number) and self.peek_at(2, Number):
            _range = self.range()

        line_counter = 1
        while self.peek(LineBreak) and self.peek_at(2, LeftBracket):
            self.consume() # get rid of linebreak
            self.field_line()
            line_counter += 1
        return InputFieldExpression(placeholder, line_counter, _range)

    def field(self):
        self.match(LeftBracket)
        placeholder = self.placeholder()
        self.match(RightBracket)
        return placeholder

    def placeholder(self):
        head = self.match(Underscore)
        placeholder = self.match( Text)
        tail = self.match(Underscore)
        return PlaceholderExpression(placeholder.value, len(head.value + tail.value + placeholder.value))

    def field_line(self):
        self.match_all(LeftBracket, Underscore, RightBracket)

    def matrixlist(self):
        self.match(LeftBracket)
        self.match(LineBreak)
        elements = self.matrixelements()
        self.match(RightBracket)
        return MatrixListExpression(elements)

    def matrixelements(self):
        return [MatrixElementExpression(element.variable) for element in self.elements()]

    def list(self):
        self.match(LeftBracket)
        self.match(LineBreak)
        elements = self.elements()
        self.match(RightBracket)
        return ListExpression(elements)

    def elements(self):
        elements = []
        element = self.element()
        elements.append(element)
        while self.peek(LineBreak):
            self.match(LineBreak)
            if self.peek(Text):
                element = self.element()
                elements.append(element)
        return elements

    def element(self):
        variable = self.string_variable()
        return ElementExpression(variable)

    def scale(self):
        self.match(LeftBrace)
        steps = self.steps()
        self.match(RightBrace)
        return ScaleExpression(steps)

    def steps(self):
        # at least two
        steps = []
        step = self.step()
        steps.append(step)
        self.match(Separator)
        step = self.step()
        steps.append(step)
        while self.peek(Separator):
            self.match(Separator)
            step = self.step()
            steps.append(step)
        return steps

    def step(self):
        return self.number_variable()

    def numbering(self):
        number = self.match(Number)
        self.match(Period)
        return NumberExpression(number.value)

    def string_variable(self):
        label = self.label()
        identifier = self.identifier()
        return VariableExpression(label, identifier)

    def number_variable(self):
        label = self.label()
        value = self.number_value()
        return VariableExpression(label, value)

    def range(self):
        _min = self.match(Number).value
        _max = self.match(Number).value
        return RangeExpression(_min, _max)

    def label(self):
        label = self.match(Text)
        return LabelExpression(label.value)

    def identifier(self):
        name = self.match(Identifier).value
        return IdentifierExpression(name)

    def number_value(self):
        token = self.match(Identifier)
        return NumberExpression(token.value)