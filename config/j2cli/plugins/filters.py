import re
from collections import Sequence


def uppercase_identifier(value):
    """ :param str value: The value to transform.  """
    return re.sub(r'[^a-zA-Z0-9]+', '_', value.upper())


def _cmake_escape_atom(value):
    return (str(value).encode('unicode-escape').replace(';', r'\;')
            .replace('$', r'\$'))


def cmake_escape(value):
    if isinstance(value, Sequence) and not isinstance(value, basestring):
        seq = value
    else:
        seq = [value]
    return '"%s"' % ';'.join(_cmake_escape_atom(x) for x in seq)


def setup(jinja_env):
    """ :type jinja_env: jinja2.Environment """
    jinja_env.filters.update(
        uppercase_identifier=uppercase_identifier,
        cmake_literal=cmake_escape)
