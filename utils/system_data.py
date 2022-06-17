import psutil
from utils.math_ops import Math


class SystemData:
    @staticmethod
    async def memory() -> dict:
        _data = psutil.virtual_memory()
        return {
            "used_perc": _data.percent,
            "used_space": await Math.convert_size_data(_data.used),
            "total_space": await Math.convert_size_data(_data.total)
        }

    @staticmethod
    async def cpu() -> float:
        return psutil.cpu_percent()
