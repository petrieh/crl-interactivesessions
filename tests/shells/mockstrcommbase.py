import logging
import abc
from contextlib import contextmanager
from fractions import Fraction
import six


LOGGER = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class MockStrCommBase(object):

    def __init__(self, probability_of_trouble):
        self._probability_of_trouble = probability_of_trouble
        self._strcomm = None
        self._count = 0
        self._in_trouble_context = False

    def set_strcomm(self, strcomm):
        self._strcomm = strcomm

    @property
    def comm(self):
        return self._strcomm.comm

    @contextmanager
    def in_trouble(self):
        self._in_trouble_context = True
        try:
            yield None
        finally:
            self._in_trouble_context = False

    def _is_in_trouble(self):
        p = Fraction(self._probability_of_trouble)
        self._count += 1
        trouble = self._count % p.denominator < p.numerator and self._in_trouble_context
        LOGGER.debug('Messaging in trouble' if trouble else 'Messaging normal')
        return trouble
