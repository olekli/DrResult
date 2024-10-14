# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from drresult import returns_result
from drresult.result import filter_traceback

import traceback
import pytest


def test_traceback_on_panic():
    @returns_result()
    def f1():
        return f2().unwrap_or_raise()

    @returns_result()
    def f2():
        return f3().unwrap_or_raise()

    @returns_result()
    def f3():
        a = {}
        raise SystemError('foo')
        a['bar'] = 'baz'

    exc = None
    try:
        result = f1()
    except AssertionError as e:
        exc = e

    assert exc
    tb = filter_traceback(exc)
    assert len(tb) == 4
    assert tb[0].name == 'test_traceback_on_panic'
    assert tb[1].name == 'f1'
    assert tb[2].name == 'f2'
    assert tb[3].name == 'f3'


def test_traceback_from_err():
    @returns_result()
    def f1():
        return f2().unwrap_or_raise()

    @returns_result()
    def f2():
        return f3().unwrap_or_raise()

    @returns_result()
    def f3():
        a = {}
        a['bar'] = a['baz']

    result = f1()

    assert not result
    tb = filter_traceback(result.unwrap_err())
    assert len(tb) == 3
    assert tb[0].name == 'f1'
    assert tb[1].name == 'f2'
    assert tb[2].name == 'f3'
