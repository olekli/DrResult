# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from typing import Any, Callable, NoReturn, Optional, Type


class BaseResult[T]:
    def __init__(self, value: T):
        self._value = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._value})'

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


class Err[E: Exception](BaseResult[E]):
    __match_args__ = ('error',)

    def __init__(self, error: E) -> None:
        self._value: E = error

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
        raise self._value


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
                        new_exc = AssertionError(f'Unhandled exception: {str(e)}')
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
    expects=[Exception],
    raises=Exception,
    not_expects=LanguageLevelExceptions + SystemLevelExceptions,
) -> Callable[[Callable[..., T]], Callable[..., Result[T]]]:
    expects = set(expects).difference(set(not_expects))
    expects_without_conversion = {e for e in expects if issubclass(e, raises)}
    expects_with_conversion = expects.difference(expects_without_conversion)
    expects_without_conversion_tuple = tuple(expects_without_conversion)
    expects_with_conversion_tuple = tuple(expects_with_conversion)
    assert len(expects_with_conversion) == 0 or callable(getattr(raises, 'from_other', None))

    def decorator(func: Callable[..., T]) -> Callable[..., Result[T]]:
        def wrapper(*args: Any, **kwargs: Any) -> Result[T]:
            try:
                result = func(*args, **kwargs)
                return Ok(result)
            except BaseException as e:
                match e:
                    case AssertionError():
                        raise
                    case _ if isinstance(e, expects_without_conversion_tuple):
                        return Err(e)
                    case _ if isinstance(e, expects_with_conversion_tuple):
                        converted = raises.from_other(e)
                        if not converted:
                            raise AssertionError(f'Cannot convert exception: {str(e)}')
                        return Err(converted.unwrap())
                    case _:
                        new_exc = AssertionError(f'Unhandled exception: {str(e)}')
                        raise new_exc from None

        return wrapper

    return decorator
