import base64
from .localmodules import LocalModules
from .remotemodules import modulesmanager


BOOTSTRAP_TMPL = """
    import base64


    SERIALIZED_SIMPLE_MANAGER = {serialized_simple_manager}
    SERIALIZED_MANAGER = {serialized_manager}
    SERIALIZED_MODULE = {serialized_module}
    SERIALIZED_CALL = {serialized_call}

    simple_source = base64.b64decode(SERIALIZED_SIMPLE_MANAGER)

    simple_ns = {{}}
    c = compile(simple_source, filename='__bootstrapping', mode='exec')
    exec(c, ns)

    simple_remotemodules = simple_ns['RemoteModules']
    modulesmanager = simple_remotemodules.import_serialized_module(SERIALIZED_MANAGER)
    remotemodules = modulesmanager.RemoteModules()
    remotemodules.import_serialized_module(SERIALIZED_MODULE)
    remotemodules.call_serialized(SERIALIZED_CALL)
"""


def create_serialized_bootstrap(module, function):
    """Create bootstrap string which can be executed in Python shell in
    the following fashion:

    >>> s = create_serialized_bootstrap(mymodule, myfunction)
    >>> import base64
    >>> ns = {}
    >>> exec(compile(base64.b64decode(s), filename='myfile', mode='exec'), ns)

    This calls *function* of *module* via
    :class:`crl.interactivesessions.shells.remotemodules.RemoteModules`.
    """
    l = LocalModules()
    man = l.import_module(modulesmanager)
    source_structs = l.get_source_structs(man.__name__)
    m = l.import_module(module)

    return base64.b64encode(BOOTSTRAP_TMPL.format(
        serialize_simple_manager=base64.b64encode(source_structs.root.source),
        serialized_manager=l.serialize_module(man),
        serialized_module=l.serialize_module(m),
        serialized_call=l.serialize_call(m, function)))
