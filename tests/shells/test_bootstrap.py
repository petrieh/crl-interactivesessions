import base64
from crl.interactivesessions.shells.bootstrap import create_serialized_bootstrap
from .remotemodules.exampleremotemodules import mainexample


def test_create_serialized_bootstrap(capsys):

    s = create_serialized_bootstrap(mainexample, 'print_grandchild')
    m = base64.b64decode(s)
    ns = {}
    exec(compile(m, filename='test', mode='exec'), ns)
    o, _ ,_ = capsys.readouterr()
    assert o == 'grandchild'
