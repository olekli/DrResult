# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from drresult import returns_result, constructs_as_result, log_panic, Panic, Err
from drresult.result import filter_traceback, excepthook

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
    except Panic as e:
        exc = e

    assert exc
    tb = filter_traceback(exc)
    assert len(tb) == 4
    assert tb[0].name == 'test_traceback_on_panic'
    assert tb[1].name == 'f1'
    assert tb[2].name == 'f2'
    assert tb[3].name == 'f3'

    msg = exc.trace()
    print(msg)
    assert 'Panic' in msg and 'f1' in msg and 'f2' in msg and 'f3' in msg


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

    msg = result.trace()
    assert 'f1' in msg and 'f2' in msg and 'f3' in msg


def test_traceback_on_panic_in_constructor():
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

    @constructs_as_result
    class A:
        def __init__(self):
            self.result = f1()

    exc = None
    try:
        a = A()
    except Panic as e:
        exc = e

    assert exc
    tb = filter_traceback(exc)
    assert len(tb) == 5
    assert tb[0].name == 'test_traceback_on_panic_in_constructor'
    assert tb[1].name == '__init__'
    assert tb[2].name == 'f1'
    assert tb[3].name == 'f2'
    assert tb[4].name == 'f3'


def test_traceback_from_err_in_constructor():
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

    @constructs_as_result
    class A:
        def __init__(self):
            self.result = f1().unwrap_or_raise()

    a = A()

    assert not a
    tb = filter_traceback(a.unwrap_err())
    assert len(tb) == 4
    assert tb[0].name == '__init__'
    assert tb[1].name == 'f1'
    assert tb[2].name == 'f2'
    assert tb[3].name == 'f3'


def test_log_panic():
    class DummyLogger:
        def __init__(self):
            self.msg = None

        def critical(self, msg):
            self.msg = msg

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

    logger = DummyLogger()
    with pytest.raises(Panic):
        with log_panic(logger):
            f1()
    assert logger.msg
    assert 'SystemError' in logger.msg and 'foo' in logger.msg
    assert 'f3' in logger.msg and 'f2' in logger.msg and 'f1' in logger.msg


def test_excepthook(capsys):
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
    except Panic as e:
        exc = e

    excepthook(None, exc, None)
    captured = capsys.readouterr()
    assert 'Panic' in captured.out
    assert 'SystemError' in captured.out
    assert 'foo' in captured.out
    assert 'f3' in captured.out
    assert 'f2' in captured.out
    assert 'f1' in captured.out
