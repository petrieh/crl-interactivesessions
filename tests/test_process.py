import mock
import pytest
from crl.interactivesessions._process import _NoCommBackgroudProcess


__copyright__ = 'Copyright (C) 2019, Nokia'


@pytest.fixture
def mock_terminalpools():
    with mock.patch('crl.interactivesessions._process._TerminalPools', spec_set=True) as p:
        yield p



class MockNoCommBackgroundProcess(_NoCommBackgroudProcess):

    def _initialize_terminal(self):
        self.proxies = mock.Mock()
        self.proxies.daemon_popen.return_value = 'pid'
        super(MockNoCommBackgroundProcess, self)._initialize_terminal()

    @staticmethod
    def _nocall_comm():
        assert 0, 'Communicate called eventhough it should not'


def test_nocommbackgroundprocess(mock_terminalpools):
    p = MockNoCommBackgroundProcess('cmd',
                                    executable='executable',
                                    shelldicts=[{'ExampleShell'}],
                                    properties={})
    assert p.run() == 'pid'
    tpools = mock_terminalpools.return_value
    tpools.get.assert_called_once_with()
    tpools.put.assert_called_once_with(p.terminal)


class DaemonError(Exception):
    pass


def test_nocommbackgroundprocess_raises(mock_terminalpools):
    p = MockNoCommBackgroundProcess('cmd',
                                    executable='executable',
                                    shelldicst=[{'ExampleShell'}],
                                    properties={})
    p.proxies.daemon_popen.side_effect = DaemonError
    with pytest.raises(DaemonError):
        p.run()

    tpools = mock_terminalpools.return_value
    tpools.get.assert_called_once_with()
    tpools.put.assert_called_once_with(p.terminal)
