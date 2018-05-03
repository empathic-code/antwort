from .expression import Expression

class Constructor(object):
    def __init__(self, expression):
        self._expression = expression

    def __str__(self):
        return self._expression.__class__.__name__


class Kwargs(object):
    def __init__(self, expression):
        self._expression = expression

    def __iter__(self):
        fields = {key: value
                  for key, value in self._expression.__dict__.items()
                  if not key.startswith('_')
                  and not key == 'walk'
                  and not isinstance(value, Expression)
                  and not isinstance(value, list)
                }

        yield from fields.items()


class PythonVisitor(object):
    def pre(self, expression, depth, context):
        print("%s%s:" % (depth * '    ', Constructor(expression)))
        for key,value in Kwargs(expression):
            print('%s%s: %s' % ((depth + 1) * '    ' , key, value))

    def post(self, expression, depth, context):
        pass