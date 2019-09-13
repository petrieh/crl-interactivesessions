from crl.interactivesessions.shells.terminalclient import TerminalComm


class CustomTerminalComm(TerminalComm):
    def __init__(self, *args, **kwargs):
        super(CustomTerminalComm, self).__init__(*args, **kwargs)
        self._written = b''

    @property
    def written(self):
        return self._written

    def clear(self):
        self._written = b''

    def _write(self, s):
        self._written += s

    def write_direct(self, s):
        super(CustomTerminalComm, self)._write(s)
