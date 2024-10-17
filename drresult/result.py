# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from typing import NoReturn, Optional, List
import sys
import traceback

"""
This module provides a `Result` type similar to Rust's `std::result`, enabling error handling without exceptions.

Classes:
    - BaseResult: Base class for Ok and Err types.
    - Ok: Represents a successful result.
    - Err: Represents an error result.
    - Panic: Exception raised for unexpected errors.

Functions:
    - filter_traceback: Filters traceback frames to exclude internal functions.
    - format_traceback: Formats the traceback of an exception.
    - format_exception: Formats the exception message.
    - format_traceback_exception: Formats the full traceback and exception message.
    - excepthook: Custom exception hook to print formatted exceptions.
"""


class BaseResult[T]:
    """Base class for `Ok` and `Err` result types."""

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
        """Check if the result is `Ok`.

        Returns:
            bool: False by default, overridden in subclasses.
        """
        return False

    def __bool__(self) -> bool:
        """Boolean representation of the result.

        Returns:
            bool: True if `Ok`, False otherwise.
        """
        return self.is_ok()

    def _unexpected(self, msg: Optional[str] = None) -> NoReturn:
        """Raise an `AssertionError` for unexpected method calls.

        Args:
            msg (Optional[str]): Additional message for the error.

        Raises:
            AssertionError: Indicating an unexpected call.
        """
        raise AssertionError(f'{self.__str__()}' + (f': {msg}' if msg else ''))


class Ok[T](BaseResult[T]):
    """Represents a successful result."""

    __match_args__ = ('value',)

    def __init__(self, value: T) -> None:
        """Initialize an `Ok` result with the given value.

        Args:
            value (T): The successful value.
        """
        self._value: T = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._value})'

    @property
    def value(self) -> T:
        return self._value

    def is_ok(self) -> bool:
        """Check if the result is `Ok`.

        Returns:
            bool: True.
        """
        return True

    def is_err(self) -> bool:
        """Check if the result is an `Err`.

        Returns:
            bool: False.
        """
        return False

    def expect(self, msg: str) -> T:
        """Return the value, ignoring the message.

        Args:
            msg (str): Message to display if the result is `Err`.

        Returns:
            T: The successful value.
        """
        return self._value

    def unwrap(self) -> T:
        """Return the successful value.

        Returns:
            T: The value held by `Ok`.
        """
        return self._value

    def expect_err(self, msg: str) -> NoReturn:
        """Raise an `AssertionError` because the result is `Ok`.

        Args:
            msg (str): Error message.

        Raises:
            AssertionError: Indicating unexpected call.
        """
        self._unexpected(msg)

    def unwrap_err(self) -> NoReturn:
        """Raise an `AssertionError` because the result is `Ok`.

        Raises:
            AssertionError: Indicating unexpected call.
        """
        self._unexpected()

    def unwrap_or[U](self, alternative: U) -> T:
        """Return the successful value.

        Args:
            alternative (U): An alternative value (ignored).

        Returns:
            T: The value held by `Ok`.
        """
        return self._value

    def unwrap_or_raise(self) -> T:
        """Return the successful value.

        Returns:
            T: The value held by `Ok`.
        """
        return self._value

    def unwrap_or_return(self) -> T:
        """Return the successful value.

        Returns:
            T: The value held by `Ok`.
        """
        return self._value


class Err[E: BaseException](BaseResult[E]):
    """Represents an error result."""

    __match_args__ = ('error',)

    def __init__(self, error: E) -> None:
        """Initialize an `Err` result with the given error.

        Args:
            error (E): The exception representing the error.
        """
        self._value: E = error

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({format_exception(self._value)})'

    def trace(self) -> str:
        """Get the formatted traceback of the error.

        Returns:
            str: The traceback string.
        """
        return f'{format_traceback(self._value)}{format_exception(self._value)}'

    @property
    def error(self) -> E:
        return self._value

    def is_ok(self) -> bool:
        """Check if the result is `Ok`.

        Returns:
            bool: False.
        """
        return False

    def is_err(self) -> bool:
        """Check if the result is an `Err`.

        Returns:
            bool: True.
        """
        return True

    def expect(self, msg: str) -> NoReturn:
        """Raise an `AssertionError` with the given message.

        Args:
            msg (str): Error message.

        Raises:
            AssertionError: Indicating unexpected call.
        """
        self._unexpected(msg)

    def unwrap(self) -> NoReturn:
        """Raise an `AssertionError` because the result is `Err`.

        Raises:
            AssertionError: Indicating unexpected call.
        """
        self._unexpected()

    def expect_err(self, msg: str) -> E:
        """Return the error exception.

        Args:
            msg (str): Message to display if the result is `Ok`.

        Returns:
            E: The exception held by `Err`.
        """
        return self._value

    def unwrap_err(self) -> E:
        """Return the error exception.

        Returns:
            E: The exception held by `Err`.
        """
        return self._value

    def unwrap_or[U](self, alternative: U) -> U:
        """Return the alternative value.

        Args:
            alternative (U): An alternative value to return.

        Returns:
            U: The alternative value.
        """
        return alternative

    def unwrap_or_raise(self) -> NoReturn:
        """Raise the stored exception.

        Raises:
            BaseException: The exception held by `Err`.
        """
        raise self._value from None

    def unwrap_or_return(self) -> NoReturn:
        """Raise the stored exception.

        Raises:
            BaseException: The exception held by `Err`.
        """
        self.unwrap_or_raise()


type Result[T] = Ok[T] | Err[BaseException]
"""Type alias for `Result`, which can be an `Ok` or an `Err`."""


def filter_traceback(e: BaseException) -> List[traceback.FrameSummary]:
    tb = traceback.extract_tb(e.__traceback__)
    return [
        frame
        for index, frame in enumerate(tb)
        if not (
            frame.name == 'unwrap_or_raise'
            or frame.name == 'drresult_returns_result_wrapper'
            or frame.name == 'drresult_constructs_as_result_wrapper'
            or frame.name == 'log_panic'
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
    """Exception raised for unexpected errors leading to program termination.

    Attributes:
        unhandled_exception (BaseException): The original unhandled exception.
    """

    def __init__(self, unhandled_exception: BaseException):
        """Initialize a `Panic` exception.

        Args:
            unhandled_exception (BaseException): The original exception.
        """
        self.unhandled_exception = unhandled_exception
        self.__traceback__ = self.unhandled_exception.__traceback__

    def __repr__(self) -> str:
        return f'{format_exception(self.unhandled_exception)}'

    def trace(self) -> str:
        """Get the formatted traceback and exception message.

        Returns:
            str: The traceback and exception message.
        """
        return f'{format_traceback(self)}Panic: {format_exception(self.unhandled_exception)}'

    def __str__(self) -> str:
        return self.__repr__()
