import os
from multiprocessing import (
    Process,
    Queue)
from contextlib import contextmanager
from collections import namedtuple
import pytest
from crl.interactivesessions.shells.remotemodules.modulesmanager import RemoteModules
from crl.interactivesessions.shells.localmodules import LocalModules

from .exampleremotemodules import mainexample


THISDIR = os.path.dirname(__file__)
MAINEXAMPLE_PATH = os.path.join(THISDIR, 'exampleremotemodules', 'mainexample.py')


class ImportMsg(namedtuple('ImportMsg', ['serialized_module'])):
    pass


class CallMsg(namedtuple('CallMsg', ['serialized_call'])):
    pass


class ExitMsg(object):
    pass


class ExceptionMsg(namedtuple('ExceptionMsg', ['exception'])):
    pass


class ResultMsg(namedtuple('ResultMsg', ['result'])):
    pass


class ModulesServer(object):
    def __init__(self):
        self._inq = Queue()
        self._outq = Queue()
        self._process = Process(target=self._start)
        self._remotemodules = RemoteModules()

    @contextmanager
    def running(self):
        try:
            self._process.start()
            yield None
        finally:
            self._send_msg(ExitMsg())
            self._process.join()

    def import_serialized(self, serialized_module):
        self._inq.put(ImportMsg(serialized_module))
        return self._outq.get()

    def call_serialized(self, serialized_call):
        self._inq.put(CallMsg(serialized_call))
        ret = self._outq.get()
        if isinstance(ret, ExceptionMsg):
            assert 0, ret.exception
        return ret.result

    def _start(self):
        try:
            self._run()
        except Exception as e:  # pylint: disable=broad-except
            self._outq.put(ExceptionMsg(e))

    def _send_msg(self, msg):
        self._inq.put(msg)

    def _run(self):
        while True:
            m = self._inq.get()
            if isinstance(m, ExitMsg):
                break
            self._handle(m)

    def _handle(self, m):
        if isinstance(m, ImportMsg):
            self._import(m.serialized_module)

        if isinstance(m, CallMsg):
            self._call(m.serialized_call)

    def _import(self, serialized_module):
        mod = self._remotemodules.import_serialized_module(serialized_module)
        self._outq.put(dir(mod))

    def _call(self, serialized_call):
        self._outq.put(ResultMsg(self._remotemodules.call_serialized(serialized_call)))


@pytest.fixture(scope='module')
def local(modulesserver):
    modules = LocalModules()
    module = modules.import_module(mainexample)
    serialized_module = modules.serialize_module(module)
    remotedir = modulesserver.import_serialized(serialized_module)
    assert remotedir == dir(module)
    return Local(modules=modules, module=module)


@pytest.fixture(scope='module')
def modulesserver():
    s = ModulesServer()
    with s.running():
        yield s


class Local(namedtuple('Local', ['modules', 'module'])):
    pass


def test_modulesmanager(modulesserver, local):
    arg = local.module.ExampleArgs(arg1=1, arg2=2)
    kwargs = {'arg3': '\narg3\n'}
    serialized_call = local.modules.serialize_call(local.module,
                                                   'call_descendants',
                                                   arg, **kwargs)
    assert '\n' not in serialized_call

    serialized_ret = modulesserver.call_serialized(serialized_call)

    ret = local.module.call_descendants(arg, **kwargs)

    assert local.modules.deserialize_return(serialized_ret) == ret
    assert ret.arg1 == 1
    assert ret.arg2 == 2
    assert ret.arg3 == '\narg3\n'


def test_modulesmanager_raises(modulesserver, local):
    serialized_call = local.modules.serialize_call(local.module,
                                                   'raise_example_exception')
    ret = modulesserver.call_serialized(serialized_call)
    with pytest.raises(local.module.ExampleException) as excinfo:
        local.modules.deserialize_return(ret)

    assert str(excinfo.value) == 'example'
