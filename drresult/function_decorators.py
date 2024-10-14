# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from types import TracebackType
from typing import Any, Callable, NoReturn, Type, List
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

expects_default = [Exception]
not_expects_default = LanguageLevelExceptions + SystemLevelExceptions


def make_drresult_returns_result_decorator[
    T
](
    expects: List[Type[Exception]] = expects_default,
    not_expects: List[Type[Exception]] = not_expects_default,
) -> Callable[[Callable[..., Result[T]]], Callable[..., Result[T]]]:
    expects_tuple = tuple(expects)
    not_expects_tuple = tuple(not_expects)

    def make_drresult_returns_result_wrapper(
        func: Callable[..., Result[T]]
    ) -> Callable[..., Result[T]]:
        def drresult_returns_result_wrapper(*args: Any, **kwargs: Any) -> Result[T]:
            try:
                return func(*args, **kwargs)
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

        return drresult_returns_result_wrapper

    return make_drresult_returns_result_wrapper


def returns_result[
    T
](*decorator_args: Any, **decorator_kwargs: Any) -> (
    Callable[..., Result[T]] | Callable[[Callable[..., Result[T]]], Callable[..., Result[T]]]
):
    if len(decorator_args) == 1 and callable(decorator_args[0]) and not decorator_kwargs:
        return make_drresult_returns_result_decorator(expects_default, not_expects_default)(
            decorator_args[0]
        )
    else:
        return make_drresult_returns_result_decorator(**decorator_kwargs)
