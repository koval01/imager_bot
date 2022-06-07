import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from static.filters import IsOwnerFilter, IsModeratorFilter, \
    IsBannedFilter, IsFullBannedFilter
from static import config
from utils.throttling import ThrottlingMiddleware
from utils.analytics import AnalyticsMiddleware

# env init
_is_debug_run = True if "debug_run" in sys.argv else False

# Configure logging
_logging_mode = logging.DEBUG if _is_debug_run else logging.INFO
logging.basicConfig(level=_logging_mode)

# prerequisites
if not config.BOT_TOKEN:
    exit("No token provided")

# init
storage = RedisStorage2(
    host=config.REDIS_URL["host"], port=config.REDIS_URL["port"],
    password=config.REDIS_URL["password"], ssl=False, pool_size=5000
) if config.REDIS_STORAGE else MemoryStorage()

bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(ThrottlingMiddleware())
dp.middleware.setup(AnalyticsMiddleware())

# activate filters
dp.filters_factory.bind(IsOwnerFilter)
dp.filters_factory.bind(IsModeratorFilter)
dp.filters_factory.bind(IsBannedFilter)
dp.filters_factory.bind(IsFullBannedFilter)
