import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from static.filters import IsOwnerFilter, IsModeratorFilter, IsAdminFilter, MemberCanRestrictFilter
from static import config

# Configure logging
logging.basicConfig(level=logging.INFO)

# prerequisites
if not config.BOT_TOKEN:
    exit("No token provided")

# init
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=RedisStorage2(
    host=config.REDIS_URL["host"], port=config.REDIS_URL["port"],
    password=config.REDIS_URL["password"], ssl=False
))
dp.middleware.setup(LoggingMiddleware())

# activate filters
dp.filters_factory.bind(IsOwnerFilter)
dp.filters_factory.bind(IsModeratorFilter)
dp.filters_factory.bind(IsAdminFilter)
dp.filters_factory.bind(MemberCanRestrictFilter)
