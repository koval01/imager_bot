import os

import sentry_sdk
from aiogram import executor, Dispatcher

import handlers
from database.controller import engine as sql_engine
from dispatcher import dp
from utils.log_module import *

_ = handlers.__init__
_ = logging

sentry_sdk.init(
    os.getenv("SENTRY_BOT"),
    traces_sample_rate=1.0
)


async def shutdown_actions(dp_: Dispatcher) -> None:
    await dp_.storage.close()
    await dp_.storage.wait_closed()
    await sql_engine.dispose()


if __name__ == "__main__":
    executor.start_polling(
        dp, skip_updates=True,
        relax=0.05,
        on_shutdown=shutdown_actions)
