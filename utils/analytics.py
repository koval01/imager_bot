import logging
import time

from static.config import GA_ID, GA_SECRET
from aiogram.types import Message
from aiogram import Dispatcher
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import current_handler
from aiohttp import ClientSession


class Analytics:
    def __init__(self, message: Message, alt_action: str = None) -> None:
        self.id = GA_ID
        self.secret = GA_SECRET

        self.message = message
        self.alt_action = alt_action

        self.host = "www.google-analytics.com"
        self.path = "mp/collect"

    async def _request(self, params: dict, json: dict) -> None:
        async with ClientSession() as session:
            try:
                async with session.post(
                        f"https://{self.host}/{self.path}", json=json, params=params
                ) as response:
                    if response.status >= 200 < 300:
                        logging.debug("OK code Google Analytics")
                    else:
                        logging.warning(f"Error code Google Analytics: {response.status}. "
                                        f"Detail response: {response.text[:512]}")
            except Exception as e:
                logging.error(
                    f"Error sending request to Google Analytics. "
                    f"Error name: {e.__class__.__name__}. Error details: {e}"
                )

    @property
    def _build_payload(self) -> dict:
        user_id = self.message.from_user.id
        return {
            'client_id': str(user_id),
            'user_id': str(user_id),
            'events': [{
                'name': self.message.get_command()[1:]
                if not self.alt_action else self.alt_action,
                'params': {
                    'language': self.message.from_user.language_code,
                    'engagement_time_msec': '1',
                }
            }],
        }

    @property
    async def send(self) -> None:
        await self._request({
            "measurement_id": self.id, "api_secret": self.secret
        }, self._build_payload)

    def __str__(self) -> str:
        return self.id


class AnalyticsMiddleware(BaseMiddleware):
    def __init__(self):
        super(AnalyticsMiddleware, self).__init__()

    def check_timeout(self, obj):
        start = obj.conf.get('_start', None)
        if start:
            del obj.conf['_start']
            return round((time.time() - start) * 1000)
        return -1

    async def on_process_message(self, message: Message, data: dict):
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        _debug_data = [handler.__name__, dispatcher, message, data]
        await Analytics(message=message, alt_action=handler.__name__).send