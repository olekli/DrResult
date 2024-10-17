# Copyright 2024 Ole Kliemann
# SPDX-License-Identifier: MIT

from contextlib import contextmanager
from drresult.gather_result import gather_result
from drresult.result import Panic
import logging
import sys

"""
This module provides a context manager `log_panic` to log `Panic` exceptions.

Functions:
    - log_panic: Context manager to log `Panic` exceptions using the provided logger.
"""

@contextmanager
def log_panic(logger: logging.Logger):
    """Context manager to log `Panic` exceptions.

    Args:
        logger (logging.Logger): The logger to use for logging.

    Usage:
        with log_panic(logger):
            # Code that might raise a `Panic`
            pass
    """
    excepthook = sys.excepthook
    sys.excepthook = lambda x, y, z: None
    try:
        with gather_result(expects=[], not_expects=[BaseException]) as result:
            yield
    except Panic as e:
        logger.critical(f'{e.trace()}')
        raise
