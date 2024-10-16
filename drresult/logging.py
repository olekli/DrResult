# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from contextlib import contextmanager
from drresult.gather_result import gather_result
from drresult.result import Panic
import logging
import sys


@contextmanager
def log_panic(logger: logging.Logger):
    excepthook = sys.excepthook
    sys.excepthook = lambda x, y, z: None
    try:
        with gather_result(expects=[], not_expects=[BaseException]) as result:
            yield
    except Panic as e:
        logger.critical(f'{e.trace()}')
        raise
