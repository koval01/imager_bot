from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from static.filters import IsOwnerFilter, IsModeratorFilter, \
    IsBannedFilter, IsFullBannedFilter
from static import config
from utils.throttling import ThrottlingMiddleware
from utils.analytics import AnalyticsMiddleware
from utils.response_wait import ResponseWaitMiddleware

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

# middlewares list
dp.middleware.setup(ResponseWaitMiddleware())
dp.middleware.setup(LoggingMiddleware())
dp.middleware.setup(ThrottlingMiddleware())
dp.middleware.setup(AnalyticsMiddleware())

# activate filters
dp.filters_factory.bind(IsOwnerFilter)
dp.filters_factory.bind(IsModeratorFilter)
dp.filters_factory.bind(IsBannedFilter)
dp.filters_factory.bind(IsFullBannedFilter)
