import asyncio
import time

from utils.log_module import logger
from utils.timer import Timer


def async_timer(func):
    """
    Async decorator for order execute time function
    """

    async def process(func, *args, **params):
        if asyncio.iscoroutinefunction(func):
            await logger.debug('AsyncTimer_ {} coroutine function, all ok.'.format(func.__name__))
            return await func(*args, **params)
        else:
            await logger.error(f"{func.__name__} not coroutine!")
            return func(*args, **params)

    async def helper(*args, **params):
        start = time.time()
        result = await process(func, *args, **params)

        _ = await Timer(func, time.time() - start).write_result
        data = await Timer(func).calc_avg()
        await logger.debug(f"Function {func.__name__} took average {data['avg']:.4f} seconds")
        return result

    return helper
