from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message


class ResponseWaitMiddleware(BaseMiddleware):
    def __init__(self):
        super(ResponseWaitMiddleware, self).__init__()

    async def on_process_message(self, message: Message, data: dict):
        await message.answer_chat_action("typing")
