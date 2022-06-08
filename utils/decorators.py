import logging as log

import functools
import time


def timer(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        runtime = time.perf_counter() - start
        log.debug(f"{func.__name__} took {runtime:.4f} secs")
        return result
    return _wrapper
