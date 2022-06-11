import logging as log
from utils.timer import Timer

import functools
import time


def timer(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        runtime = time.perf_counter() - start
        _ = Timer(func, runtime).write_result
        data = Timer(func).calc_avg()
        log.info(f"Function {func.__name__} took average {data} seconds")
        return result
    return _wrapper
