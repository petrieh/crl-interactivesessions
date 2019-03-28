"""Example module main
"""
from collections import namedtuple

if 'childexample' not in globals():
    from . import (
        childexample,
        grandchildexample)


__copyright__ = 'Copyright (C) 2019, Nokia'

CHILD_MODULES = [childexample, grandchildexample]


class ExampleResult(namedtuple('ExampleResult', ['arg1',
                                                 'arg2',
                                                 'arg3',
                                                 'child',
                                                 'grandchild'])):
    pass


class ExampleArgs(namedtuple('ExampeArgs', ['arg1', 'arg2'])):
    pass


class ExampleException(Exception):
    pass


def call_descendants(exampleargs, arg3):
    return ExampleResult(arg1=exampleargs.arg1,
                         arg2=exampleargs.arg2,
                         arg3=arg3,
                         child=childexample.child_func(),
                         grandchild=grandchildexample.grandchild_func())


def call_descendants_simple(arg1, arg2):
    return 'args={args}, child: {child}, grandchild: {grandchild}'.format(
        args=(arg1, arg2,),
        child=childexample.child_func(),
        grandchild=grandchildexample.grandchild_func())


def raise_example_exception():
    raise ExampleException('example')


def print_grandchild():
    print(grandchildexample.grandchild_func())
