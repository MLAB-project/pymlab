#!/usr/bin/python
# -*- coding: utf-8 -*-
"""fry.utils module.

Author: Jan Milík <milikjan@fit.cvut.cz>
"""


import sys


def args_repr(*args, **kwargs):
    """
    Returns human-readable string representation of both positional and
    keyword arguments passed to the function.

    This function uses the built-in :func:`repr()` function to convert
    individual arguments to string.

    >>> args_repr("a", (1, 2), some_keyword = list("abc"))
    "'a', (1, 2), some_keyword = ['a', 'b', 'c']"
    """
    items = [repr(a) for a in args]
    items += ["%s = %r" % (k, v) for k, v in iter(kwargs.items())]
    return ", ".join(items)


def obj_repr(obj, *args, **kwargs):
    """
    Returns human-readable string representation of an object given that it has
    been created by calling constructor with the specified positional and
    keyword arguments.

    This is a convenience function to help implement custom `__repr__()`
    methods. For example:

    >>> class Animal(object):
    ...    def __init__(self, hit_points, color, **kwargs):
    ...       self.hit_points = hit_points
    ...       self.color = color
    ...       self.hostile = kwargs.get("hostile", False)
    ...    def __repr__(self):
    ...       return obj_repr(self, self.hit_points, self.color, hostile = self.hostile)
    >>> dog = Animal(2.3, "purple")
    >>> repr(dog)
    "Animal(2.3, 'purple', hostile = False)"
    """
    cls_name = type(obj).__name__
    return "%s(%s)" % (cls_name, args_repr(*args, **kwargs), )


class PrettyPrinter(object):
    INDENT = object()
    CURRENT = object()

    def __init__(self, output = None):
        if output is None:
            output = sys.stdout
        self.output = output
        self._indent = []
        self._current_indent = 0

        self._mode_stack = []
        self.new_line = True
        self.max_level = None

    @property
    def mode(self):
        if len(self._mode_stack) == 0:
            return None
        return self._mode_stack[-1]

    def push_mode(self, value):
        self._mode_stack.append(value)

    def pop_mode(self):
        return self._mode_stack.pop()

    def write(self, value):
        if value is self.INDENT:
            self.output.write("".join(self._indent))
            self.new_line = False
            return
        if self.new_line:
            self.write(self.INDENT)
            self.new_line = False
        value = str(value)
        if "\n" in value:
            lines = value.splitlines()
            for line in lines:
                self.writeln(line)
        else:
            self._current_indent += len(value)
            self.output.write(value)

    def writeln(self, value = ""):
        self.write(value)
        self.output.write("\n")
        self.new_line = True
        self._current_indent = 0

    def writef(self, value, *args, **kwargs):
        self.write(value.format(*args, **kwargs))

    def flush(self):
        self.output.flush()

    def close(self):
        self.output.close()

    def indent(self, indent = "   "):
        if indent is self.CURRENT:
            self._indent.append(" " * self._current_indent)
            self._current_indent = 0
            return
        self._indent.append(indent)

    def unindent(self):
        self._indent.pop()

    def format_list(self, value, level = 0):
        if (self.max_level is not None) and (level >= self.max_level):
            self.write("[ ... ]")
            return

        if len(value) < 10:
            self.write("[ ")
            self.indent(self.CURRENT)
            for item in value:
                self.format_inner(item, level + 1)
                self.write(", ")
            self.unindent()
            self.write("]")
            return

        self.writeln("[")
        self.indent()
        for item in value:
            self.format_inner(item, level + 1)
            self.writeln(",")
        self.unindent()
        self.write("]")

    def format_inner(self, value, level = 0):
        if value in self.visited:
            self.write("<recursion>")
            return

        if self.mode is None:
            meth = getattr(value, "__pprint__", None)
        else:
            meth = getattr(value, "__pprint_%s__" % (self.mode, ), None)
            if meth is None:
                meth = getattr(value, "__pprint__", None)
        if meth:
            self.visited.append(value)
            meth(self, level)
            self.visited.pop()
            return

        if isinstance(value, list):
            self.format_list(value, level)
            return

        if isinstance(value, basestring):
            if "\n" in value:
                self.indent()
                lines = value.splitlines()
                for line in lines:
                    self.format_inner(line, level + 1)
                self.unindent()
                return

        self.write(repr(value))

    def format(self, value):
        self.visited = []
        self.format_inner(value)
        self.visited = None


class Enum(object):
    def __init__(self, *args, **kwargs):
        self._names = {}
        self._indicies = {}
        self._items = []

        self.max_value = 0
        index = 0
        for arg in args:
            if isinstance(arg, int):
                index = arg
            else:
                self.max_value = max(self.max_value, index)
                self._indicies[arg] = index
                self._names[index] = arg
                self._items.append(index)
                index += 1

    def __len__(self):
        return len(self._indicies)

    def __setitem__(self, key, value):
        self._names[key] = value
        self._indicies[value] = key

        if isinstance(key, int):
            self.max_value = max(self.max_value, key)

    def __getattr__(self, name):
        try:
            return self._indicies[name]
        except KeyError:
            raise AttributeError

    def __in__(self, value):
        return value in self._indicies

    def __iter__(self):
        return iter(self._items)

    def to_string(self, value):
        try:
            return self._names[value]
        except KeyError:
            return "<undefined enum %r>" % (value, )

    def get_name(self, value):
        try:
            return self._names[value]
        except KeyError:
            raise ValueError("%r is not a valid enum value." % (value, ))

    def from_name(self, name):
        try:
            return self._indicies[name]
        except KeyError:
            raise ValueError("Unknown enum name: %r." % (name, ))

    def decorate(self, name):
        def decorator(cls):
            self[name] = cls
            return cls
        return decorator


class Enum2(object):
    INDEX = object()

    class Sequence(object):
        def __iter__(self):
            return self

    @classmethod
    def range(cls, start = 0, step = 1):
        class IntegerSequence(cls.Sequence):
            def __init__(self, start, step):
                self._next = start
                self._step = step

            def __iter__(self):
                return self

            def next(self):
                value = self._next
                self._next += self._step
                return value

        return IntegerSequence(start, step)

    def __init__(self, attributes, defaults, items):
        self._attributes = attributes
        self._defaults = defaults

        self._item_class = collections.namedtuple("EnumItem", attributes)

        self._name_map = {}
        self._items = []

        for item in items:
            if isinstance(item, basestring):
                item = (item, )
            name = str(item[0])

            attributes = [(a or b) for a, b in itertools.izip_longest(item, self._defaults)]
            attributes = [(a.next() if isinstance(a, self.Sequence) else a) for a in attributes]

            value = self._item_class(*attributes)
            setattr(self, name, value)

            self._name_map[name] = value
            self._items.append(value)

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, key):
        if isinstance(key, int):
            if key >= len(self._items):
                raise KeyError
            return self._items[key]
        if isinstance(key, basestring):
            return self._name_map[key]
        raise KeyError


class UserException(Exception):
    def __init__(self, message = None, *args, **kwargs):
        Exception.__init__(self, message, *args)

        self.message    = str(message)
        self.underlying = kwargs.pop("underlying", None)

        self.kwargs = kwargs

    def __str__(self):
        return self.message

    def __repr__(self):
        if self.underlying is None:
            return obj_repr(self, self.message)
        return obj_repr(self, self.message, underlying = self.underlying)

    def __pprint__(self, printer, level = 0):
        printer.writef("Message: {}\n\n", self.message)

        printer.writeln("Keywords:")
        printer.indent()
        for key, value in self.kwargs.iteritems():
            printer.writef("{}: ", key)
            printer.indent(printer.CURRENT)
            printer.format_inner(value, level + 1)
            printer.unindent()
        printer.unindent()


def replace_ext(file_name, extension = None):
    if "." in file_name:
        parts = file_name.split(".")
        if extension:
            parts[-1] = extension
        else:
            parts.pop()
        return ".".join(parts)
    else:
        if extension:
            return file_name + "." + extension
        return file_name


def main():
    print(__doc__)


if __name__ == "__main__":
    main()
