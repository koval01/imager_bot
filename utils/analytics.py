from aiogram.dispatcher.handler import current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message
from aiohttp import ClientSession

from content.manager import Manager
from static.config import GA_ID, GA_SECRET
from utils.decorators import async_timer
from utils.log_module import logger


class Analytics:
    def __init__(self, message: Message, alt_action: str = None) -> None:
        self.id = GA_ID
        self.secret = GA_SECRET

        self.message = message
        self.alt_action = alt_action

        self.host = "www.google-analytics.com"
        self.path = "mp/collect"

    @async_timer
    async def _request_ga_server(self, params: dict, json: dict) -> None:
        """
        Request to Google Analytics API
        """
        async with ClientSession() as session:
            try:
                async with session.post(
                        f"https://{self.host}/{self.path}", json=json, params=params
                ) as response:
                    if response.status >= 200 < 300:
                        await logger.debug("OK code Google Analytics")
                    else:
                        await logger.warning(
                            f"Error code Google Analytics: {response.status}. "
                            f"Detail response: {response.text[:512]}")
            except Exception as e:
                await logger.error(
                    "Error send request to Google Analytics. Details: %s" % e)

    @property
    def _build_payload(self) -> dict:
        """
        Build body for request to Google Analytics
        """
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
    async def send(self) -> _request_ga_server:
        """
        Method for send data
        """
        return await self._request_ga_server({
            "measurement_id": self.id, "api_secret": self.secret
        }, self._build_payload)

    def __str__(self) -> str:
        return self.id


class AnalyticsMiddleware(BaseMiddleware):
    def __init__(self):
        super(AnalyticsMiddleware, self).__init__()

    @staticmethod
    async def _update_user(message: Message) -> None:
        user_check = await Manager(message=message).check_user()
        await logger.debug(
            "Error check user. (Google Analytics middleware)") \
            if not user_check else None

    async def on_process_message(self, message: Message, data: dict):
        handler = current_handler.get()
        _ = data
        await self._update_user(message)
        await Analytics(message=message, alt_action=handler.__name__).send
