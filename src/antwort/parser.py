# encoding: utf-8
from .baseparser import BaseParser, UnexpectedTokenException
from .expression import *
from .token_ import *


class UnexpectedTypeConstraint(Exception):
    pass


class AntwortParser(BaseParser):
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
        message = message % (
            token_type.__name__, self.next().type(), line + 1, position)
        raise UnexpectedTokenException(message)

    def unexpected_constraint(self, constraint):
        message = ('Unexpected Type Constraint: '
                   'Expecting "number" or "string" but found <%s>\n'
                   'At   : Line %s, Position %s')
        line, position = self._lexer.location()
        message = message % (constraint, line + 1, position)
        raise UnexpectedTypeConstraint(message)

    def parse(self):
        return self.questions()

    def questions(self):
        questions = []
        question = self.question()
        questions.append(question)

        while self.peek(LineBreak):
            self.consume()

        while self.peek(Digits):
            question = self.question()
            questions.append(question)

            while self.peek(LineBreak):
                self.consume()

        return QuestionList(questions)

    def question(self):
        header = self.question_head()
        options = self.options()
        return Question(header, options)

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

        return QuestionHead(number, variable, explanation, required)

    def explanation(self):
        text = self.match(Text)
        self.match(LineBreak)
        return Label(text.value)

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
                self.consume()  # kill linebreak
                items = self.matrixlist()
                return Matrix(scale, items)
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
        return CheckBoxList(checkboxes)

    def checkbox(self):
        self.match(LeftBracket)
        self.match(RightBracket)
        variable = self.string_variable()
        return CheckBox(variable)

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
        return RadioList(radios)

    def radio(self):
        self.match(Radio)
        variable = self.string_variable()
        return RadioButton(variable)

    def input_field(self):
        placeholder = self.field()

        _range = None
        if self.peek(Digits) and self.peek_at(2, Digits):
            _range = self.range()

        line_counter = 1
        while self.peek(LineBreak) and self.peek_at(2, LeftBracket):
            self.consume()  # get rid of linebreak
            self.field_line()
            line_counter += 1
        return InputField(placeholder, line_counter, _range)

    def field(self):
        self.match(LeftBracket)
        placeholder = self.placeholder()
        self.match(RightBracket)
        return placeholder

    def placeholder(self):
        head = self.match(Underscore)
        placeholder = self.match(Text)
        tail = self.match(Underscore)
        return Placeholder(placeholder.value, len(head.value + tail.value + placeholder.value))

    def field_line(self):
        self.match_all(LeftBracket, Underscore, RightBracket)

    def matrixlist(self):
        self.match(LeftBracket)
        self.match(LineBreak)
        elements = self.matrixelements()
        self.match(RightBracket)
        return MatrixList(elements)

    def matrixelements(self):
        return [MatrixElement(element.variable) for element in self.elements()]

    def list(self):
        self.match(LeftBracket)
        self.match(LineBreak)
        elements = self.elements()
        self.match(RightBracket)
        return List(elements)

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
        return Element(variable)

    def scale(self):
        self.match(LeftBrace)
        steps = self.steps()
        self.match(RightBrace)
        return Scale(steps)

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
        number = self.match(Digits)
        self.match(Period)
        return Number(number.value)

    def string_variable(self):
        label = self.label()
        identifier = self.identifier()
        return Variable(label, identifier)

    def number_variable(self):
        label = self.label()
        value = self.number_value()
        return Variable(label, value)

    def range(self):
        _min = self.match(Digits).value
        _max = self.match(Digits).value
        return Range(_min, _max)

    def label(self):
        label = self.match(Text)
        return Label(label.value)

    def identifier(self):
        name = self.match(Identifier).value
        return Name(name)

    def number_value(self):
        token = self.match(Identifier)
        return Number(token.value)
