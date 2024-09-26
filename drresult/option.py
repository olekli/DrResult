# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from typing import Type


class Some[T]:
    def __init__(self, value: T) -> None:
        self._value = value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._value})'

    def __str__(self) -> str:
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        if other is None:
            return False
        if not isinstance(other, Some):
            return NotImplemented
        return type(self) is type(other) and self._value == other._value

    def __hash__(self) -> int:
        return hash((self.__class__, self._value))

    def __bool__(self) -> bool:
        return True

    def unwrap(self) -> T:
        return self._value


type Option[T] = Some[T] | None
