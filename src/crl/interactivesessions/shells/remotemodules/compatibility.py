import sys


__copyright__ = 'Copyright (C) 2019, Nokia'


try:
    RANGE = xrange
except NameError:
    RANGE = range


PY3 = (sys.version_info.major == 3)


def string_conversion_to_bytes(value):
    return to_bytes(str(value))


def to_bytes(s):
    return s.encode('utf-8') if PY3 and isinstance(s, str) else s


def to_string(b):
    return b.decode('utf-8') if PY3 and isinstance(b, bytes) else b
