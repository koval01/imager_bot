import os

import sentry_sdk
from aiogram import executor, Dispatcher

from database.controller import engine as sql_engine
from dispatcher import dp
from utils.log_module import logger
from utils.heroku import Heroku

import handlers

_ = handlers.__init__

sentry_sdk.init(
    os.getenv("SENTRY_BOT"),
    traces_sample_rate=1.0
)


async def startup_actions(dp_: Dispatcher) -> None:
    await Heroku().send_build_for_moderators()


async def shutdown_actions(dp_: Dispatcher) -> None:
    await dp_.storage.close()
    await dp_.storage.wait_closed()
    await logger.shutdown()
    await sql_engine.dispose()


if __name__ == "__main__":
    executor.start_polling(
        dp, skip_updates=True,
        on_startup=startup_actions,
        on_shutdown=shutdown_actions)
