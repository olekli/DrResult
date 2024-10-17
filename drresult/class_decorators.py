# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from typing import Any, Callable, Type, List
from drresult.result import Result, Ok
from drresult.function_decorators import returns_result, expects_default, not_expects_default

"""
This module provides a decorator for classes whose constructors might raise exceptions.

Decorators:
    - constructs_as_result: Wraps the construction of a class in a `Result` type.
"""


def make_drresult_constructs_as_result_decorator[
    T
](
    expects: List[Type[BaseException]] = expects_default,
    not_expects: List[Type[BaseException]] = not_expects_default,
) -> Callable[[Type[T]], Type[T]]:
    """Creates a decorator to wrap class constructors in a `Result` type.

    Args:
        expects (List[Type[BaseException]]): List of expected exceptions.
        not_expects (List[Type[BaseException]]): List of unexpected exceptions.

    Returns:
        Callable: A decorator for classes.
    """

    def make_drresult_constructs_as_result_wrapper(cls: Type[T]) -> Type[T]:
        Base = type(cls)  # type: Any

        class Meta(Base):
            @returns_result(expects=expects, not_expects=not_expects)
            def __call__(cls, *args, **kwargs) -> Result[T]:
                return cls.drresult_constructs_as_result_wrapper(*args, **kwargs)

            def drresult_constructs_as_result_wrapper(cls, *args, **kwargs) -> Result[T]:
                return Ok(super(Meta, cls).__call__(*args, **kwargs))

        WrapperBase = cls  # type: Any

        class Wrapper(WrapperBase, metaclass=Meta):
            """Wrapper class to construct instances as a `Result`."""

            pass

        return Wrapper

    return make_drresult_constructs_as_result_wrapper


def constructs_as_result[T](*decorator_args: Any, **decorator_kwargs: Any) -> Any:
    """Decorator to wrap class instantiation in a `Result` type.

    Can be used with or without arguments.

    Usage:
        @constructs_as_result
        class MyClass: ...

        @constructs_as_result(expects=[ValueError])
        class MyClass: ...

    Args:
        *decorator_args (Any): Positional arguments.
        **decorator_kwargs (Any): Keyword arguments.

    Returns:
        Any: The decorated class.
    """
    if len(decorator_args) == 1 and callable(decorator_args[0]) and not decorator_kwargs:
        return make_drresult_constructs_as_result_decorator(expects_default, not_expects_default)(
            decorator_args[0]
        )
    else:
        return make_drresult_constructs_as_result_decorator(**decorator_kwargs)
