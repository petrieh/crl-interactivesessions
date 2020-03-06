from crl.interactivesessions.shells.remotemodules.compatibility import py23_unic

__copyright__ = 'Copyright (C) 2020, Nokia'


def string_should_contain(a, b):
    return py23_unic(b) in py23_unic(a)
