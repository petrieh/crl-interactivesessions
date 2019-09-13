import logging
import pexpect
from .mockstrcommbase import MockStrCommBase


__copyright__ = 'Copyright (C) 2019, Nokia'


LOGGER = logging.getLogger(__name__)


class LostStrComm(MockStrCommBase):

    def __init__(self, probability_of_trouble, modifier=None):
        super(LostStrComm, self).__init__(probability_of_trouble)
        self._modifier = modifier or self._default_modifier
        self._write_empty = False

    @staticmethod
    def _default_modifier(*_):
        return b''

    def write_str(self, s):
        self._strcomm.comm.clear()
        self._strcomm.write_str(s)
        written = self._strcomm.comm.written
        new_written = self._modified_s(written)
        if new_written or self._write_empty:
            LOGGER.debug('===== writing: %s', repr(new_written))
            self._strcomm.comm.write_direct(new_written)

    def read_str(self):
        ret = self._strcomm.read_str()
        modified_ret = self._modified_s(ret)
        LOGGER.debug('==== Received: %s, is lost: %d', ret, not modified_ret)
        LOGGER.debug('==== Modified return %s', modified_ret)
        if not modified_ret:
            raise pexpect.TIMEOUT('==== Message is lost: {!r}'.format(ret))

        return ret

    def _modified_s(self, s):
        if self._is_in_trouble():
            new_s = self._modifier(s)
            LOGGER.debug('==== Msg modified, count=%s, s=%s, new_s=%s',
                         self._count, s, repr(new_s))
            s = new_s
        else:
            LOGGER.debug('==== Msg success, count=%s, %s', self._count, s)
        return s
