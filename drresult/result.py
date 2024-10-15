# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from typing import NoReturn, Optional, List
import sys
import traceback


class BaseResult[T]:
    def __init__(self):  # pragma: no cover
        self._value: T

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, BaseResult):
            return NotImplemented
        return type(self) is type(other) and self._value == other._value

    def __hash__(self) -> int:
        return hash((self.__class__, self._value))

    def is_ok(self) -> bool:  # pragma: no cover
        return False

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


class Err[E: BaseException](BaseResult[E]):
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


type Result[T] = Ok[T] | Err[BaseException]


def filter_traceback(e: BaseException) -> List[traceback.FrameSummary]:
    tb = traceback.extract_tb(e.__traceback__)
    return [
        frame
        for index, frame in enumerate(tb)
        if not (
            frame.name == 'unwrap_or_raise'
            or frame.name == 'drresult_returns_result_wrapper'
            or frame.name == 'drresult_constructs_as_result_wrapper'
            or (
                frame.name == '__call__'
                and (index + 1) < len(tb)
                and tb[index + 1].name == 'drresult_constructs_as_result_wrapper'
            )
        )
    ]


def format_traceback(e: BaseException) -> str:
    new_tb_list = filter_traceback(e)
    trace_to_print = ''.join(traceback.format_list(new_tb_list))
    return trace_to_print


def format_exception(e: BaseException) -> str:
    return ''.join(traceback.format_exception_only(e))[:-1]


def format_traceback_exception(e: BaseException) -> str:
    return f'{format_traceback(e)}{format_exception(e)}'


def excepthook(type, e, traceback):
    print(f'{format_traceback_exception(e)}')


sys.excepthook = excepthook


class Panic(Exception):
    def __init__(self, unhandled_exception: BaseException):
        self.unhandled_exception = unhandled_exception
        self.__traceback__ = self.unhandled_exception.__traceback__

    def __repr__(self) -> str:
        return f'{format_exception(self.unhandled_exception)}'

    def trace(self) -> str:
        return f'{format_traceback(self)}Panic: {format_exception(self.unhandled_exception)}'

    def __str__(self) -> str:
        return self.__repr__()
