import json
from typing import Callable, Dict

import numpy as np
import aioredis

from static.config import REDIS_URL_ORG
from static.messages import dictionary as reply_dict
from utils.log_module import logger
from utils.system_data import SystemData


class Timer:
    def __init__(self, function: Callable = None, time: float = 0) -> None:
        self.r = aioredis.from_url(REDIS_URL_ORG)
        self.redis_var_name = "timerDataDict"
        self.function = function
        self.name: str = function.__name__ if function else None
        self.time = round(time, 4)
        self.max_key_len = 1000

    @property
    async def _read_data(self) -> Dict[str, int] or None:
        try:
            value = await self.r.get(self.redis_var_name)
            return json.loads(
                value.decode("utf-8")
            )
        except Exception as e:
            await logger.warning(
                "Error get key %s in Redis storage. Details: %s" %
                (self.redis_var_name, e))

    async def _write_data(self, data: dict) -> bool:
        try:
            await self.r.set(self.redis_var_name, json.dumps(data))
            return True
        except Exception as e:
            await logger.error(
                "Error write data to Redis in timer. Details: %s" % e)
            return False

    @property
    async def _check_key(self) -> bool:
        data = await self._read_data
        return True if len([
            key for key, data in data.items()
            if key == self.name
        ]) else False

    @property
    async def _add_key(self) -> bool:
        data = await self._read_data
        data.update({self.name: [self.time]}) \
            if not await self._check_key else None
        return await self._write_data(data)

    async def _check_len(self, name: str) -> bool:
        data = await self._read_data
        return True \
            if len(data[name]) <= self.max_key_len \
            else False

    @property
    async def _all_data(self) -> list:
        data = await self._read_data
        return [
            (key, len(data)) for key, data in data.items()
        ]

    @property
    async def write_result(self) -> bool:
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
        _data = await self._all_data
        return {key: {
            "time": await self.calc_avg(key), "len": len_
        } for key, len_ in _data}

    @property
    async def build_response(self) -> str:
        async def _modify_template(answer_: list) -> None:
            answer_.insert(0, "-" * 20)
            answer_.insert(0, reply_dict["timings_title_template"])
            answer_.append("-" * 20)
            answer_.append(reply_dict["sys_data_template"] % (
                _system_data["cpu"], _system_data["memory"]["used_space"],
                _system_data["memory"]["total_space"], _system_data["memory"]["used_perc"]
            ))

        async def _build_answer(_data: dict) -> list:
            return [
                _template % (
                    _data[key]["time"]["len"], key, _data[key]["time"]["min"],
                    _data[key]["time"]["avg"], _data[key]["time"]["max"],
                    _data[key]["time"]["percentage"]["50"],
                    _data[key]["time"]["percentage"]["95"]
                ) for key in _data if key != "null"]

        _data = await self.all_handlers()
        _system_data = {
            "memory": await SystemData().memory(),
            "cpu": await SystemData().cpu()}

        _template = reply_dict["timings_template"]
        answer = await _build_answer(_data)
        await _modify_template(answer)
        return "\n".join(answer)
