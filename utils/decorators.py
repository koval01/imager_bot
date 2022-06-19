import asyncio
import logging as log
import time

from utils.timer import Timer


def async_timer(func):
    """
    Async decorator for order execute time function
    """

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

        _ = await Timer(func, time.time() - start).write_result
        data = await Timer(func).calc_avg()
        log.debug(f"Function {func.__name__} took average {data['avg']:.4f} seconds")
        return result

    return helper
