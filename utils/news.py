from content.manager import Manager
from aiogram import types, Bot
from typing import Tuple
from static.menu import dictionary as dict_reply
import logging as log


class NewsSend:
    def __init__(self, message: types.Message, bot: Bot) -> None:
        self.message = message
        self.bot = bot

    async def _send_messages(self) -> Tuple[int, str]:
        users = await Manager().get_all_users_ids
        text = self.message.get_args()
        if len(text) > 3500:
            return 0, ""
        if not len(text):
            return 0, "/news текст"
        successes = 0
        for user_id in users:
            try:
                await self.bot.send_message(user_id, dict_reply["news_template"] % (
                    text, self.message.from_user.full_name), disable_web_page_preview=False)
                successes += 1
            except Exception as e:
                log.info("Error send message. Details: %s" % e)
        return successes, ""

    async def execute(self) -> types.Message:
        await self.message.reply(dict_reply["init_news_send"])
        successes_count, text_result = \
            await self._send_messages()
        if not successes_count:
            if text_result:
                return await self.message.reply(text_result)
            return await self.message.reply(dict_reply["news_send_error"])
        return await self.message.reply(dict_reply["finish_news_send"] % successes_count)
