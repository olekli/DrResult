# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from drresult import constructs_as_result

import pytest


class DummyException(Exception):
    def __init__(self, payload: str):
        self.payload = payload

    def __eq__(lhs, rhs) -> bool:
        if not isinstance(rhs, DummyException):
            return NotImplemented
        return lhs.payload == rhs.payload

    def __hash__(self) -> int:
        return hash(self.payload)


@constructs_as_result
class A:
    def __init__(self, to_throw=None):
        if to_throw:
            raise to_throw

    def value(self):
        return 123


def test_no_exception_produces_ok_instance():
    a = A()

    assert a
    a = a.unwrap()
    assert isinstance(a, A)
    assert a.value() == 123


def test_standard_exceptions_produce_err():
    a = A(DummyException('foo'))

    assert not a
    a = a.unwrap_err()
    assert a == DummyException('foo')


def test_non_standard_exception_panics():
    with pytest.raises(AssertionError):
        a = A(SystemError('foo'))


@constructs_as_result(expects=[RuntimeError, DummyException, ValueError])
class B:
    def __init__(self, to_throw=None):
        if to_throw:
            raise to_throw

    def value(self):
        return 123


def test_no_exception_produces_ok_instance_with_expects():
    b = B()

    assert b
    b = b.unwrap()
    assert isinstance(b, B)
    assert b.value() == 123


def test_standard_exceptions_produce_err_with_expects():
    b = B(DummyException('foo'))

    assert not b
    b = b.unwrap_err()
    assert b == DummyException('foo')


def test_not_expected_exception_panics_with_expects():
    with pytest.raises(AssertionError):
        b = B(KeyError('foo'))


def test_non_standard_exception_panics_with_expects():
    with pytest.raises(AssertionError):
        b = B(SystemError('foo'))
