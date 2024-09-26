# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from typing import Type

from drresult import Ok, Err, returns_result, noexcept

import pytest


def test_equal_ok_is_equal():
    lhs = Ok('foo')
    rhs = Ok('foo')
    assert lhs == rhs


def test_different_ok_is_not_equal():
    lhs = Ok('foo')
    rhs = Ok('bar')
    assert not (lhs == rhs)


def test_equal_err_is_equal():
    lhs = Err('foo')
    rhs = Err('foo')
    assert lhs == rhs


def test_different_err_result_is_not_equal():
    lhs = Err('foo')
    rhs = Err('bar')
    assert not (lhs == rhs)


def test_equal_value_ok_err_is_not_equal():
    lhs = Ok('foo')
    rhs = Err('foo')
    assert not (lhs == rhs)


def test_equal_ok_has_identical_hash():
    lhs = Ok('foo')
    rhs = Ok('foo')
    assert hash(lhs) == hash(rhs)


def test_different_ok_has_different_hash():
    lhs = Ok('foo')
    rhs = Ok('bar')
    assert not (hash(lhs) == hash(rhs))


def test_equal_value_ok_err_has_different_hash():
    lhs = Ok('foo')
    rhs = Err('foo')
    assert not (hash(lhs) == hash(rhs))


def test_ok_is_ok():
    result = Ok('foo')
    assert result.is_ok()


def test_ok_is_not_err():
    result = Ok('foo')
    assert not result.is_err()


def test_ok_is_true():
    result = Ok('foo')
    assert result


def test_err_is_err():
    result = Err('foo')
    assert result.is_err()


def test_err_is_not_ok():
    result = Err('foo')
    assert not result.is_ok()


def test_err_is_false():
    result = Err('foo')
    assert not result


def test_ok_expects_value():
    result = Ok('foo')
    assert result.expect('bar') == 'foo'


def test_ok_unwraps_value():
    result = Ok('foo')
    assert result.unwrap() == 'foo'


def test_ok_not_expects_err():
    result = Ok('foo')
    with pytest.raises(AssertionError):
        result.expect_err('bar')


def test_ok_not_unwraps_err():
    result = Ok('foo')
    with pytest.raises(AssertionError):
        result.unwrap_err()


def test_ok_unwraps_value_not_or():
    result = Ok('foo')
    assert result.unwrap_or('bar') == 'foo'


def test_ok_unwraps_value_not_raises():
    @returns_result()
    def func() -> str:
        result = Ok('foo')
        result.unwrap_or_raise()
        return 'bar'

    result = func()
    assert result.is_ok() and result.unwrap() == 'bar'


def test_err_not_expects():
    result = Err('foo')
    with pytest.raises(AssertionError):
        result.expect('bar')


def test_err_not_unwraps():
    result = Err('foo')
    with pytest.raises(AssertionError):
        result.unwrap()


def test_err_expects_err_value():
    result = Err('foo')
    assert result.expect_err('bar') == 'foo'


def test_err_unwraps_err_value():
    result = Err('foo')
    assert result.unwrap_err() == 'foo'


def test_err_unwraps_or_value():
    result = Err('foo')
    assert result.unwrap_or('bar') == 'bar'


def test_err_unwraps_raises():
    @returns_result(expects=[RuntimeError])
    def func() -> int:
        result = Err(RuntimeError('foo'))
        result.unwrap_or_raise()
        return 5

    result = func()
    assert (
        result.is_err()
        and isinstance(result.unwrap_err(), RuntimeError)
        and str(result.unwrap_err()) == 'foo'
    )


def test_err_unwraps_raises_assertion_when_not_specified():
    @returns_result(expects=[FileNotFoundError, SyntaxError])
    def func() -> int:
        result = Err(RuntimeError('foo'))
        result.unwrap_or_raise()
        return 5

    with pytest.raises(AssertionError):
        result = func()


def test_result_decorator_catches_exception_specified():
    @returns_result(expects=[SyntaxError, FileNotFoundError])
    def func() -> str:
        raise FileNotFoundError('foo')
        return 'bar'

    result = func()
    assert result.is_err()
    result = result.unwrap_err()
    assert isinstance(result, FileNotFoundError)
    assert str(result) == 'foo'


def test_result_decorator_catches_all_exceptions_by_default():
    @returns_result()
    def func() -> str:
        raise KeyError('foo')
        return 'bar'

    result = func()
    assert result.is_err()
    result = result.unwrap_err()
    assert isinstance(result, KeyError)
    assert str(result) == "'foo'"


def test_result_decorator_not_catches_assert_by_default():
    @returns_result()
    def func() -> str:
        assert False
        return 'bar'

    with pytest.raises(AssertionError):
        result = func()


def test_result_decorator_not_catches_exception_not_specified():
    @returns_result(expects=[SyntaxError, KeyError])
    def func() -> str:
        raise FileNotFoundError('foo')
        return 'bar'

    with pytest.raises(AssertionError):
        result = func()


def test_pattern_matching_ok_matches_ok():
    result = Ok('foo')
    match result:
        case Err(e):
            assert False
        case Ok(v):
            assert v == 'foo'
        case _:
            assert False


def test_pattern_matching_err_matches_err():
    result = Err('foo')
    match result:
        case Ok(v):
            assert False
        case Err(e):
            assert e == 'foo'
        case _:
            assert False


def test_pattern_matching_with_exceptions_works():
    data = [{'foo': 'value-1'}, {'bar': 'value-2'}]

    @returns_result(expects=[IndexError, KeyError, RuntimeError])
    def retrieve_record_entry_backend(index: int, key: str) -> str:
        if key == 'baz':
            raise RuntimeError(123)
        return data[index][key]

    def retrieve_record_entry(index: int, key: str) -> str:
        match retrieve_record_entry_backend(index, key):
            case Ok(v):
                return f'Retrieved: {v}'
            case Err(IndexError()):
                return f'No such record: {index}'
            case Err(KeyError()):
                return f'No entry `{key}` in record {index}'
            case Err(RuntimeError() as e):
                return f'Error: {e}'
            case _:
                assert False

    assert retrieve_record_entry(2, 'foo') == 'No such record: 2'
    assert retrieve_record_entry(1, 'foo') == 'No entry `foo` in record 1'
    assert retrieve_record_entry(1, 'bar') == 'Retrieved: value-2'
    assert retrieve_record_entry(4, 'baz') == 'Error: 123'


def test_noexcept_returns_when_no_exception():
    @noexcept()
    def func() -> str:
        return 'bar'

    result = func()
    assert result == 'bar'


def test_noexcept_raises_assertion_on_exception():
    @noexcept()
    def func() -> str:
        raise RuntimeError('foo')
        return 'bar'

    with pytest.raises(AssertionError):
        result = func()


def test_raises_non_baseclass_needs_conversion():
    class E(Exception):
        pass

    def func() -> str:
        raise FileNotFoundError('foo')
        return 'bar'

    with pytest.raises(AssertionError):
        decorated = returns_result(expects=[FileNotFoundError], raises=E)


def test_raises_non_baseclass_converts_when_conversion_ok():
    class E(Exception):
        def __init__(self, s: str):
            self.s = s

        @classmethod
        @returns_result()
        def from_other[T: E](cls: Type[T], e) -> T:
            return cls(f'E: {str(e)}')

    @returns_result(raises=E)
    def func() -> str:
        raise KeyError('foo')
        return 'bar'

    result = func()
    assert not result
    assert result.unwrap_err().s == 'E: \'foo\''
