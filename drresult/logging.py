# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from contextlib import contextmanager
from drresult.gather_result import gather_result
from drresult.result import format_traceback_exception


@contextmanager
def log_panic(logger):
    try:
        with gather_result(expects=[], not_expects=[BaseException]):
            yield
    except AssertionError as e:
        logger.critical(f'{format_traceback_exception(e)}')
        raise
