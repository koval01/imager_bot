from typing import Callable
from static.config import REDIS_URL
import logging as log
import redis
import json


class Timer:
    def __init__(self, function: Callable = None, time: float = 0) -> None:
        self.r = redis.Redis(
            host=REDIS_URL["host"], port=REDIS_URL["port"],
            password=REDIS_URL["password"], ssl=False, max_connections=5000
        )
        self.redis_var_name = "timerDataDict"
        self.function = function
        self.name: str = function.__name__ if function else None
        self.time = round(time, 4)
        self.max_key_len = 1000

    def _decode_redis(self, src):
        if isinstance(src, list):
            rv = list()
            for key in src:
                rv.append(self._decode_redis(key))
            return rv
        elif isinstance(src, dict):
            rv = dict()
            for key in src:
                rv[key.decode()] = self._decode_redis(src[key])
            return rv
        elif isinstance(src, bytes):
            return src.decode()
        else:
            raise Exception("type not handled: " + type(src))

    @property
    def _read_data(self) -> dict:
        return json.loads(
            self._decode_redis(
                self.r.hgetall(self.redis_var_name)
            )[self.redis_var_name]
        )

    def _write_data(self, data: dict) -> bool:
        try:
            self.r.hset(self.redis_var_name, self.redis_var_name, json.dumps(data))
            return True
        except Exception as e:
            log.error("Error write data to Redis in timer. Details: %s" % e)
            return False

    @property
    def _check_key(self) -> bool:
        return True if len([
            key for key, data in self._read_data.items() if key == self.name
        ]) else False

    @property
    def _add_key(self) -> bool:
        data = self._read_data
        data.update({self.name: [self.time]}) \
            if not self._check_key else None
        return self._write_data(data)

    def _check_len(self, name: str) -> bool:
        return True if len(self._read_data[name]) < self.max_key_len else False

    @property
    def _all_data(self) -> list:
        return [(key, len(data)) for key, data in self._read_data.items()]

    @property
    def write_result(self) -> bool:
        if not self.name:
            return False
        _ = self._add_key
        data = self._read_data
        if not self._check_len(self.name):
            data[self.name] = data[self.name][-abs(self.max_key_len):]
        data[self.name].append(self.time)
        return self._write_data(data)

    def calc_avg(self, custom_handler: str = None) -> dict:
        _ = self._add_key
        _name = self.name if not custom_handler else custom_handler
        _data = self._read_data[_name]
        return {
            "avg": sum(_data) / len(_data), "len": len(_data),
            "min": min(_data), "max": max(_data)
        } if _data else 0

    @property
    def all_handlers(self) -> dict:
        _data = self._all_data
        return {key: {
            "time": self.calc_avg(key), "len": len_
        } for key, len_ in _data}
