from aiogram import executor
from dispatcher import dp
import handlers


async def shutdown_actions(dp) -> None:
    await dp.storage.close()
    await dp.storage.wait_closed()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown_actions)
