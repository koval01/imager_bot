from aiogram import executor
from utils.log_module import logger
from database.controller import engine as sql_engine
from dispatcher import dp
import handlers
import sentry_sdk
import os

sentry_sdk.init(
    os.getenv("SENTRY_BOT"),
    traces_sample_rate=1.0
)


async def shutdown_actions(dp) -> None:
    await dp.storage.close()
    await dp.storage.wait_closed()
    await logger.shutdown()
    await sql_engine.dispose()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown_actions)
