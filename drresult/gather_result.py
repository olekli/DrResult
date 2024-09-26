# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from typing import List, Type, Tuple

from drresult.result import Result, Ok, Err


class ResultContainer[T]:
    def __init__(self) -> None:
        self._result: Result[T] | Result[None] = Ok(None)
        self._finalized: bool = False

    def set(self, result: Result[T]) -> None:
        assert not self._finalized, "Cannot set result when already finalized"
        self._result = result

    def get(self) -> Result[T] | Result[None]:
        assert self._finalized, "Cannot get result when not finalized"
        return self._result


class gather_result[T]:
    def __init__(self, expects: List[Type[Exception]] = [Exception]):
        self._expects: Tuple[Type[Exception], ...] = tuple(expects)
        self._container: ResultContainer[T] = ResultContainer[T]()

    def __enter__(self):
        return self._container

    def __exit__(self, exc_type, exc_value, traceback):
        match exc_value:
            case None:
                pass
            case AssertionError():
                return False
            case _ if isinstance(exc_value, self._expects):
                self._container.set(Err(exc_value))
            case _:
                new_exc = AssertionError(f'Unhandled exception: {str(exc_value)}')
                new_exc = new_exc.with_traceback(traceback)
                raise new_exc from None
        self._container._finalized = True
        return True
