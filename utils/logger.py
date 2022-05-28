from utils.moderator import CheckModerator
from aiogram.types import Message
from requests import get as http_get
from static.config import BOT_TOKEN
from typing import Literal, List
import logging as log


class Logger:
    def __init__(
            self, level: Literal["info", "warning", "error"],
            exception: dict, message: Message = None
    ) -> None:
        self.log_level = level
        self.exception = exception
        self.message = message

    @property
    def _get_recipients(self) -> List[int]:
        return CheckModerator().get_moderators

    @staticmethod
    def _send_bot_msg(chat_id: int, message: str) -> bool:
        try:
            response = http_get(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", params={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            })
            return True if response.status_code == 200 else False
        except Exception as e:
            log.error("Error send message to Telegram. Details: %s" % e)
            return False

    @property
    def _python_log(self) -> log:
        log_msg = "%s: %s" % (self.exception["name"], self.exception["details"])
        return eval(f"log.{self.log_level}({log_msg})")

    @property
    def _send_log(self) -> bool:
        try:
            recipients = self._get_recipients
            message = self._build_pattern
            _ = self._python_log
            [self._send_bot_msg(r, message) for r in recipients]
            return True
        except Exception as e:
            log.error("Error send log for administrators. Details: %s" % e)
            return False

    @property
    def _build_pattern(self) -> str:
        return f"TRACE\n{'-'*10}\nLEVEL:\x20{self.log_level}\n" \
               f"In:\x20<code>{self.exception['function']}</code>\n" \
               f"Class:\x20<code>{self.exception['name']}</code>\n" \
               f"Description:\x20\"{self.exception['details']}\""

    def send(self) -> _send_log:
        return self._send_log
