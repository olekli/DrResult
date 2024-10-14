# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from types import TracebackType
from typing import Any, Callable, NoReturn, Type, List
import sys
import traceback

from drresult.result import Result, Err, format_exception, format_traceback


def noexcept[T](func: Callable[..., T]) -> Callable[..., T]:
    def wrapper(*args: Any, **kwargs: Any) -> T:
        try:
            return func(*args, **kwargs)
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


def excepthook(type, e, traceback):
    print(f'{format_traceback(e)}{format_exception(e)}')


sys.excepthook = excepthook
