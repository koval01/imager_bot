import json
import logging as log
from typing import Callable, Dict

import aioredis
import numpy as np

from static.config import REDIS_URL_ORG
from static.messages import dictionary as reply_dict
from utils.system_data import SystemData


class Timer:
    def __init__(self, function: Callable = None, time: float = 0) -> None:
        self.r = aioredis.from_url(
            REDIS_URL_ORG, encoding="utf-8",
            decode_responses=True, max_connections=5000)
        self.redis_var_name = "timerDataDict"
        self.function = function
        self.name: str = function.__name__ if function else None
        self.time = round(time, 4)
        self.max_key_len = 1000

    @property
    async def _read_data(self) -> Dict[str, int] or None:
        """
        Read timer data from Redis
        """
        try:
            value = await self.r.hget(
                *tuple([self.redis_var_name] * 2))
            await self.r.close()
            return json.loads(value)
        except Exception as e:
            log.warning(
                "Error get key %s in Redis storage. Details: %s" %
                (self.redis_var_name, e))

    async def _write_data(self, data: dict) -> bool:
        """
        Write timer data to Redis
        """
        try:
            await self.r.hset(
                *tuple([self.redis_var_name] * 2),
                json.dumps(data))
            await self.r.close()
            return True
        except Exception as e:
            log.error("Error write data to Redis in timer. Details: %s" % e)
            return False

    @property
    async def _check_key(self) -> bool:
        """
        Method for validate key
        """
        data = await self._read_data
        return True if len([
            key for key, data in data.items()
            if key == self.name
        ]) else False

    @property
    async def _add_key(self) -> bool:
        """
        Add key to dict
        """
        data = await self._read_data
        data.update({self.name: [self.time]}) \
            if not await self._check_key else None
        return await self._write_data(data)

    async def _check_len(self, name: str) -> bool:
        """
        Check key value len
        """
        data = await self._read_data
        return True \
            if len(data[name]) <= self.max_key_len \
            else False

    @property
    async def _all_data(self) -> list:
        """
        All keys timer
        """
        data = await self._read_data
        return [
            (key, len(data)) for key, data in data.items()
        ]

    @property
    async def write_result(self) -> bool:
        """
        Write result execute function
        """
        if not self.name:
            return False
        _ = await self._add_key
        data = await self._read_data
        if not await self._check_len(self.name):
            data[self.name] = \
                data[self.name][-abs(self.max_key_len):]
        data[self.name].append(self.time)
        return await self._write_data(data)

    async def calc_avg(self, custom_handler: str = None) -> dict:
        """
        Calc average execution function time
        """
        _ = await self._add_key
        _name = self.name \
            if not custom_handler \
            else custom_handler
        _data = await self._read_data
        _data = _data[_name]
        _np_data = np.array(_data)
        return {
            "avg": sum(_data) / len(_data), "len": len(_data),
            "min": min(_data), "max": max(_data), "percentage": {
                "50": np.percentile(_np_data, 50),
                "95": np.percentile(_np_data, 95)
            }
        } if _data else 0

    async def all_handlers(self) -> dict:
        """
        All keys with values
        """
        _data = await self._all_data
        return {key: {
            "time": await self.calc_avg(key), "len": len_
        } for key, len_ in _data}

    @property
    async def build_response(self) -> str:
        """
        Formatted response with statistics
        """

        def _modify_template(answer_: list) -> None:
            answer_.insert(0, "-" * 20)
            answer_.insert(0, reply_dict["timings_title_template"])
            answer_.append("-" * 20)
            answer_.append(reply_dict["sys_data_template"] % (
                _system_data["cpu"], _system_data["memory"]["used_space"],
                _system_data["memory"]["total_space"], _system_data["memory"]["used_perc"]
            ))

        def _build_answer(_data: dict) -> list:
            return [
                _template % (
                    _data[key]["time"]["len"], key, _data[key]["time"]["min"],
                    _data[key]["time"]["avg"], _data[key]["time"]["max"],
                    _data[key]["time"]["percentage"]["50"],
                    _data[key]["time"]["percentage"]["95"]
                ) for key in _data if key != "null"]

        _data = await self.all_handlers()
        _system_data = {
            "memory": SystemData().memory(),
            "cpu": SystemData().cpu()}

        _template = reply_dict["timings_template"]
        answer = _build_answer(_data)
        _modify_template(answer)
        return "\n".join(answer)
