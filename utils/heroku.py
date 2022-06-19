from datetime import datetime

import aioredis
from aiohttp import ClientSession

from dispatcher import bot
from static.config import HEROKU_API_KEY, HEROKU_APP_NAME, REDIS_URL_ORG
from static.messages import dictionary as dict_reply
from utils.log_module import logger
from utils.moderator import CheckModerator


class Heroku:
    def __init__(self) -> None:
        self.host = "api.heroku.com"
        self.path = "apps/%s/%s"
        self.key = HEROKU_API_KEY
        self.app = HEROKU_APP_NAME
        self.redis = aioredis.from_url(
            REDIS_URL_ORG, encoding="utf-8",
            decode_responses=True, max_connections=100)

        self.headers = {
            "Accept": "application/vnd.heroku+json; version=3",
            "Authorization": "Bearer %s" % self.key,
            "Range": "created_at ..; order=desc",
        }

    async def _request(self, func: str) -> dict or None:
        """
        Request to Heroku API
        """
        async with ClientSession() as session:
            try:
                async with session.get(
                    f"https://{self.host}/{self.path % (self.app, func)}",
                    headers=self.headers
                ) as response:
                    if response.status >= 200 < 300:
                        await logger.debug("Heroku response success.")
                        json_body = await response.json()
                        return json_body
                    else:
                        await logger.warning(
                            f"Error code Heroku API: {response.status}. "
                            f"Detail response: {response.text[:512]}")
            except Exception as e:
                await logger.error(
                    "Error send request to Heroku API. Details: %s" % e)

    @property
    async def build_check(self) -> bool:
        """
        Check build data
        """

        _redis_key = "last_build_id"

        async def _set_key(value: str = "null") -> None:
            await self.redis.set(_redis_key, value)
            await self.redis.close()

        async def _get_key() -> str:
            try:
                value = await self.redis.get(_redis_key)
                await self.redis.close()
                return value
            except Exception as e:
                await logger.warning(
                    "Error get key from Redis. Details: %s" % e)
                await _set_key()

        _heroku_build_id = await self.get_build
        if not _heroku_build_id:
            await logger.warning(
                "Skip build notify, error data get.")
            return False

        _redis_build_id = await _get_key()

        await logger.info(
            "Build check. Last build ID from Heroku API - %s. "
            "Last build ID from Redis storage - %s" % (
                _heroku_build_id["id"], _redis_build_id
            ))
        return False if _heroku_build_id["id"] == _redis_build_id \
            else (True, await _set_key(_heroku_build_id["id"]))[0]

    @property
    async def get_build(self) -> dict:
        """
        Check and return build data in dict type
        """

        async def _check_build(data_: dict) -> bool:
            return True if data_["status"] == "succeeded" \
                else False

        async def _format_time(time_stamp: str) -> str:
            return datetime.strptime(
                time_stamp, '%Y-%m-%dT%H:%M:%SZ'
            ).strftime("%Y-%m-%d %H:%M:%S")

        async def _get_body(data_: dict) -> dict:
            return {
                "id": data_["id"],
                "created_at": await _format_time(data_["created_at"]),
                "updated_at": await _format_time(data_["updated_at"]),
                "description": data_["source_blob"]["version_description"].strip(),
                "output_stream_url": data_["output_stream_url"]
            }

        data = await self._request("builds")
        await logger.info(
            "Heroku builds count: %d, data type: %s" % (
                len(data), type(data)))
        try:
            data[0]
        except Exception as e:
            await logger.error(
                "Error get data of build from Heroku API. Details: %s" % e)
            return {}
        return await _get_body(data[0]) \
            if await _check_build(data[0]) else {}

    async def send_build_for_moderators(self) -> None:
        """
        Function for send all moderators build data
        """

        get_moderators = await CheckModerator().get_moderators
        build_check = await self.build_check
        if build_check:
            build_data = await self.get_build
            template = dict_reply["build_data_template"] % (
                dict_reply["build_updated"], *(v for k, v in build_data.items())
            )
            for m in get_moderators:
                try:
                    await bot.send_message(m, template)
                except Exception as e:
                    _ = e
