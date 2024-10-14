# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from typing import Sequence

from drresult.result import Result, Ok, Err
from drresult.function_decorators import noexcept, returns_result
from drresult.class_decorators import constructs_as_result
from drresult.option import Some
from drresult.gather_result import gather_result

__all__: Sequence[str] = [
    'Result',
    'Ok',
    'Err',
    'noexcept',
    'returns_result',
    'Some',
    'gather_result',
    'constructs_as_result',
]
