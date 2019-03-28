import os
import base64
import pickle
import itertools
from .remotemodules.modulesmanager import (
    ModulesManager,
    SourceStructs,
    SourceStruct,
    ChildTuple,
    Call)


class LocalModules(ModulesManager):

    def import_module(self, module, module_name=None):
        s = SourceModule.get_or_create(module, module_name)
        return self.create_module(s.source_structs)

    def serialize_module(self, module):
        s = self.get_source_structs(module.__name__)
        return s.serialize()

    @staticmethod
    def serialize_call(module, function, *args, **kwargs):
        return Call(module=module.__name__,
                    function=function,
                    args=args,
                    kwargs=kwargs).serialize()

    @staticmethod
    def deserialize_return(serialized_ret):
        ret = pickle.loads(base64.b64decode(serialized_ret))
        if isinstance(ret, Exception):
            raise ret
        return ret


class SourceModule(object):

    _counter = itertools.count()
    _source_modules = {}

    def __init__(self, module, name=None):
        self._module = module
        self._name = name
        self._seqnumber = self._counter.next()
        self._source = self._read_source()
        self._child_source_modules = {s.path: s
                                      for s in self._child_creator_gen()}
        self._source_struct = self._create_source_struct()
        self._source_structs = self._create_source_structs()
        self._serialized = None

    @classmethod
    def get_or_create(cls, m, name=None):
        path = cls._get_path(m)
        if path not in cls._source_modules:
            cls._source_modules[path] = cls(m, name=name)
        return cls._source_modules[path]

    def _read_source(self):
        with open(self.path) as f:
            return f.read()

    @property
    def source_struct(self):
        return self._source_struct

    @property
    def source_structs(self):
        return self._source_structs

    @property
    def child_tuples(self):
        return [ChildTuple(name=m.name, modulename=m.modulename, filename=m.filename)
                for _, m in self._child_source_modules.items()]

    @property
    def modulename(self):
        # Module names may not contain path separators or dots as they won't
        # work with __import__ statement which is called by pickle.  We ensure
        # that module name is unique as modules are exposed globally to
        # sys.modules in both local and remote systems.
        # escaped_path is needed only for debugging purposes
        escaped_path = self.path.replace(os.path.sep, '_')
        escaped_path = ''.join([c for c in escaped_path
                                if c.isalnum() or c in ['_', '-']])
        return 'seq{seqnumber}_{escaped_path}'.format(seqnumber=self._seqnumber,
                                                      escaped_path=escaped_path)

    @property
    def path(self):
        return self._get_path(self._module)

    @staticmethod
    def _get_path(m):
        return '.'.join([os.path.abspath(
            os.path.splitext(m.__file__)[0]), 'py'])

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def source(self):
        return self._source

    @property
    def name(self):
        return self._name if self._module is None else self._name_from_module

    @property
    def _name_from_module(self):
        return self._module.__name__.split('.')[-1]

    def _child_creator_gen(self):
        try:
            for m in self._module.CHILD_MODULES:
                yield self.get_or_create(m)
        except AttributeError:
            pass

    def _create_source_struct(self):
        return SourceStruct(
            modulename=self.modulename,
            filename=self.filename,
            name=self.name,
            source=self.source,
            child_tuples=self.child_tuples)

    def _create_source_structs(self):
        return SourceStructs(
            root=self.source_struct,
            descendants={d.source_struct.modulename: d.source_struct
                         for d in self._descendants_gen()})

    def serialize(self):
        if self._serialized is None:
            self._serialized = self._serialize()
        return self._serialized

    def _serialize(self):
        return self._source_structs.serialize()

    def tree_gen(self):
        yield self
        for c in self._child_gen():
            yield c

    def _child_gen(self):
        for _, m in self._child_source_modules.items():
            yield m

    def _descendants_gen(self):
        for m in self._child_gen():
            for mm in m.tree_gen():
                yield mm
