# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from typing import Type

from drresult import Some


def test_equal_some_is_equal():
    lhs = Some('foo')
    rhs = Some('foo')
    assert lhs == rhs


def test_different_some_is_not_equal():
    lhs = Some('foo')
    rhs = Some('bar')
    assert not (lhs == rhs)


def test_some_is_not_equal_none():
    lhs = Some('foo')
    rhs = None
    assert not (lhs == rhs)


def test_some_is_not_none():
    lhs = Some('foo')
    rhs = None
    assert not (lhs is rhs)


def test_some_is_not_equal_anything():
    lhs = Some('foo')
    rhs = int(12)
    assert not (lhs == rhs)


def test_some_prints_correctly():
    lhs = Some('foo')
    assert str(lhs) == 'Some(foo)'


def test_equal_some_has_identical_hash():
    lhs = Some('foo')
    rhs = Some('foo')
    assert hash(lhs) == hash(rhs)


def test_different_some_has_different_hash():
    lhs = Some('foo')
    rhs = Some('bar')
    assert not (hash(lhs) == hash(rhs))


def test_some_has_different_hash_than_none():
    lhs = Some('foo')
    rhs = None
    assert not (hash(lhs) == hash(rhs))


def test_some_is_true():
    some = Some('foo')
    assert some


def test_some_unwraps_value():
    some = Some('foo')
    assert some.unwrap() == 'foo'
