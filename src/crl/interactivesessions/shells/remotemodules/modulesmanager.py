import json
import types
import base64
import pickle
import sys
from collections import namedtuple


class ModulesManager(object):
    def __init__(self):
        self._expanded_sources_dict = {}
        self._source_structs_dict = {}

    def create_module(self, source_structs):
        self._source_structs_dict[source_structs.root.modulename] = source_structs
        if source_structs.root.modulename not in self._expanded_sources_dict:
            es = self._expanded_sources_dict[
                source_structs.root.modulename] = ExpandedSources(source_structs)
            self._create_modules_for_expanded(es)
        return sys.modules[source_structs.root.modulename]

    def get_source_structs(self, modulename):
        return self._source_structs_dict[modulename]

    def _create_modules_for_expanded(self, expanded_sources):
        for _, e in expanded_sources.expanded_sources.items():
            self._create_module_for_expanded_if_needed(e)

    def _create_module_for_expanded_if_needed(self, expanded_source):
        if expanded_source.modulename not in sys.modules:
            self._create_module_for_expanded(expanded_source)
        return sys.modules[expanded_source.modulename]

    def _create_module_for_expanded(self, expanded_source):
        n = str(expanded_source.modulename)
        m = sys.modules[n] = types.ModuleType(n)
        self._add_child_modules_to_module_globals(m, expanded_source)
        self._compile_and_exec(m, expanded_source)
        return m

    def _add_child_modules_to_module_globals(self, module, expanded_source):
        for c_name, c_e in expanded_source.child_expanded_sources.items():
            c_m = self._create_module_for_expanded_if_needed(c_e)
            module.__dict__[c_name] = c_m

    @staticmethod
    def _compile_and_exec(module, expanded_source):
        c = compile(expanded_source.source,
                    filename=expanded_source.filename,
                    mode='exec')
        exec(c, module.__dict__)


class RemoteModules(ModulesManager):

    def import_serialized_module(self, serialized_module):
        return self.create_module(SourceStructs.deserialize(serialized_module))

    @classmethod
    def call_serialized(cls, serialized_call):
        call = Call.deserialize(serialized_call)
        module = sys.modules[call.module]
        f = getattr(module, call.function)
        try:
            return cls._serialize_result(f(*call.args, **call.kwargs))
        except Exception as e:  # pylint: disable=broad-except
            return cls._serialize_result(e)

    @staticmethod
    def _serialize_result(result):
        return base64.b64encode(pickle.dumps(result))


class SourceStructs(namedtuple('SourceStructs', ['root', 'descendants'])):

    def serialize(self):
        d = {}
        d['root'] = self.root.serialize()
        d['descendants'] = [desc.serialize() for _, desc in self.descendants.items()]
        return json.dumps(d)

    @classmethod
    def deserialize(cls, s):
        d = json.loads(s)
        return cls(root=SourceStruct.deserialize(d['root']),
                   descendants=dict(cls._deserialized_tuple_gen(d['descendants'])))

    @staticmethod
    def _deserialized_tuple_gen(descendants):
        for d in descendants:
            deserialized = SourceStruct.deserialize(d)
            yield (deserialized.modulename, deserialized)

    @property
    def source_structs_dict(self):
        return {s.modulename: s for s in self.source_structs_gen()}

    def source_structs_gen(self):
        yield self.root
        for _, s in self.descendants.items():
            yield s


class SourceStruct(namedtuple('SourceStruct', ['modulename',
                                               'filename',
                                               'name',
                                               'source',
                                               'child_tuples'])):

    def serialize(self):
        d = dict(self._asdict())
        d['source'] = base64.b64encode(self.source)
        d['child_tuples'] = [c.asdict() for c in self.child_tuples]
        return d

    @classmethod
    def deserialize(cls, d):
        kwargs = d.copy()
        kwargs['source'] = base64.b64decode(kwargs['source'])
        kwargs['child_tuples'] = [ChildTuple(**k) for k in kwargs['child_tuples']]
        return cls(**kwargs)


class ChildTuple(namedtuple('ChildTuple', ['name', 'filename', 'modulename'])):

    def asdict(self):
        return dict(self._asdict())


class ExpandedSources(object):
    def __init__(self, source_structs):
        self._source_structs = source_structs
        self._source_structs_dict = source_structs.source_structs_dict
        self._expanded_sources = {}
        self._create_expanded_sources()

    @property
    def expanded_sources(self):
        return self._expanded_sources

    @property
    def modulename(self):
        return self._source_structs.root.modulename

    def _create_expanded_sources(self):
        for _, s in self._source_structs_dict.items():
            self._create_expanded_source_if_needed(s)

    def _create_expanded_source_if_needed(self, s):
        if s.modulename not in self._expanded_sources:
            self._expanded_sources[s.modulename] = self._create_expanded_source(s)
        return self._expanded_sources[s.modulename]

    def _create_expanded_source(self, s):
        return ExpandedSource(
            name=s.name,
            modulename=s.modulename,
            filename=s.filename,
            source=s.source,
            child_expanded_sources=self._create_child_expanded_sources(s))

    def _create_child_expanded_sources(self, s):
        return {c.name: self._create_source_for_child_if_needed(c)
                for c in s.child_tuples}

    def _create_source_for_child_if_needed(self, child_tuple):
        return self._create_expanded_source_if_needed(
            self._source_structs_dict[child_tuple.modulename])



class ExpandedSource(namedtuple('ExpandedSource', ['name',
                                                   'modulename',
                                                   'filename',
                                                   'source',
                                                   'child_expanded_sources'])):
    pass


class Call(namedtuple('Call', ['module', 'function', 'args', 'kwargs'])):
    def serialize(self):
        kwargs = self._kwargs_pickle(pickle.dumps, dict(self._asdict()))
        return base64.b64encode(json.dumps(kwargs))

    @classmethod
    def deserialize(cls, serialized):
        kwargs = cls._kwargs_pickle(pickle.loads,
                                    json.loads(base64.b64decode(serialized)))
        return cls(**kwargs)

    @staticmethod
    def _kwargs_pickle(pickle_method, kwargs):
        for a in ['args', 'kwargs']:
            kwargs[a] = pickle_method(kwargs[a])
        return kwargs
