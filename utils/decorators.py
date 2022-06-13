import logging as log
from utils.timer import Timer

import functools
import asyncio
import time


def timer(func):
    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        runtime = time.perf_counter() - start
        _ = Timer(func, runtime).write_result
        data = Timer(func).calc_avg()
        log.debug(f"Function {func.__name__} took average {data['avg']:.4f} seconds")
        return result
    return _wrapper


def async_timer(func):
    async def process(func, *args, **params):
        if asyncio.iscoroutinefunction(func):
            log.debug('AsyncTimer_ {} coroutine function, all ok.'.format(func.__name__))
            return await func(*args, **params)
        else:
            log.error(f"{func.__name__} not coroutine!")
            return func(*args, **params)

    async def helper(*args, **params):
        start = time.time()
        result = await process(func, *args, **params)

        _ = Timer(func, time.time() - start).write_result
        data = Timer(func).calc_avg()
        log.debug(f"Function {func.__name__} took average {data['avg']:.4f} seconds")
        return result

    return helper
