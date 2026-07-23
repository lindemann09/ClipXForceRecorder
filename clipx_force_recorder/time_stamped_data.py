from time import perf_counter


def get_time():
    """Get high-resolution time stamp (float) """
    return perf_counter()


class TSData(object):
    """Time stamped data"""

    _init_time_high_res = get_time()

    def __init__(self, val, time:int|None=None):
        if time is None:
            self.time = int((get_time() - TSData._init_time_high_res) * 1000)
        else:
            self.time = time
        self.val = val

    @classmethod
    def set_init_time(cls, time:int):
        """set init time in milliseconds"""
        cls._init_time_high_res = time / 1000

    @classmethod
    def get_init_time(cls) -> int:
        return int(cls._init_time_high_res * 1000)

    def csv(self, decimals:int=2, extra_column:float | int | str | None=None):
        if isinstance(self.val, float):
            v = round(self.val, decimals)
        else:
            v = self.val
        if extra_column is None:
            return f"{self.time}, {v}"
        else:
            return f"{self.time}, {extra_column}, {v}"

class TSFloat(TSData):
    """Time stamped float"""
    def __init__(self, val: float, time:int|None=None) -> None:
        super().__init__(val, time)


class TSInt(TSData):
    """Time stamped integer"""

    def __init__(self, val: int, time:int|None=None) -> None:
        super().__init__(val, time)




