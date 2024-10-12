# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from types import TracebackType
from typing import Any, Callable, NoReturn, Optional, Type, List
import sys
import traceback


class BaseResult[T]:
    def __init__(self, value: T):
        self._value = value

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseResult):
            return NotImplemented
        return type(self) is type(other) and self._value == other._value

    def __hash__(self) -> int:
        return hash((self.__class__, self._value))

    def is_ok(self) -> bool:
        assert False

    def __bool__(self) -> bool:
        return self.is_ok()

    def _unexpected(self, msg: Optional[str] = None) -> NoReturn:
        raise AssertionError(f'{self.__str__()}' + (f': {msg}' if msg else ''))


class Ok[T](BaseResult[T]):
    __match_args__ = ('value',)

    def __init__(self, value: T) -> None:
        self._value: T = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._value})'

    @property
    def value(self) -> T:
        return self._value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def expect(self, msg: str) -> T:
        return self._value

    def unwrap(self) -> T:
        return self._value

    def expect_err(self, msg: str) -> NoReturn:
        self._unexpected(msg)

    def unwrap_err(self) -> NoReturn:
        self._unexpected()

    def unwrap_or[U](self, alternative: U) -> T:
        return self._value

    def unwrap_or_raise(self) -> T:
        return self._value

    def unwrap_or_return(self) -> T:
        return self._value


class Err[E: Exception](BaseResult[E]):
    __match_args__ = ('error',)

    def __init__(self, error: E) -> None:
        self._value: E = error

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({format_exception(self._value)})'

    def trace(self) -> str:
        return f'{format_traceback(self._value)}{format_exception(self._value)}'

    @property
    def error(self) -> E:
        return self._value

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def expect(self, msg: str) -> NoReturn:
        self._unexpected(msg)

    def unwrap(self) -> NoReturn:
        self._unexpected()

    def expect_err(self, msg: str) -> E:
        return self._value

    def unwrap_err(self) -> E:
        return self._value

    def unwrap_or[U](self, alternative: U) -> U:
        return alternative

    def unwrap_or_raise(self) -> NoReturn:
        raise self._value from None

    def unwrap_or_return(self) -> NoReturn:
        self.unwrap_or_raise()


type Result[T] = Ok[T] | Err[Exception]


def noexcept[T]() -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                match e:
                    case AssertionError():
                        raise
                    case _:
                        new_exc = AssertionError(f'Unhandled exception: {str(e)}').with_traceback(
                            e.__traceback__
                        )
                        raise new_exc from None

        return wrapper

    return decorator


LanguageLevelExceptions = [
    AttributeError,
    ImportError,
    NameError,
    SyntaxError,
    TypeError,
]

SystemLevelExceptions = [
    MemoryError,
    SystemError,
]


def returns_result[
    T
](
    expects: List[Type[Exception]] = [Exception],
    not_expects: List[Type[Exception]] = LanguageLevelExceptions + SystemLevelExceptions,
) -> Callable[[Callable[..., Result[T]]], Callable[..., Result[T]]]:
    expects_tuple = tuple(expects)
    not_expects_tuple = tuple(not_expects)

    def decorator(func: Callable[..., Result[T]]) -> Callable[..., Result[T]]:
        def drresult_wrapper(*args: Any, **kwargs: Any) -> Result[T]:
            try:
                result = func(*args, **kwargs)
                return result
            except BaseException as e:
                match e:
                    case AssertionError():
                        raise
                    case _ if isinstance(e, expects_tuple) and not isinstance(e, not_expects_tuple):
                        return Err(e)
                    case _:
                        new_exc = AssertionError(f'Panic: {format_exception(e)}').with_traceback(
                            e.__traceback__
                        )
                        raise new_exc from None

        return drresult_wrapper

    return decorator


def format_traceback(e: BaseException) -> str:
    tb = traceback.extract_tb(e.__traceback__)
    new_tb_list = [
        frame
        for frame in tb
        if frame.name != 'unwrap_or_raise' and frame.name != 'drresult_wrapper'
    ]
    trace_to_print = ''.join(traceback.format_list(new_tb_list))
    return trace_to_print


def format_exception(e: BaseException) -> str:
    return ''.join(traceback.format_exception_only(e))[:-1]


def excepthook(type, e, traceback):
    print(f'{format_traceback(e)}{format_exception(e)}')


sys.excepthook = excepthook
