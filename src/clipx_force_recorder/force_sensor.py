import math
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass
from time import sleep

from numpy import mean

from . import api, lsl
from .settings import RecordingSettings


@dataclass
class ForceSensorData:
    """Data class to hold force data."""
    force: float
    time: float
    clipx_time: float
    sensor_id: int = 0

    def csv(self,
            write_local_time: bool,
            write_device_id: bool=False,
            float_decimal_places: int= 4) -> str:
        """converts data to string."""

        float_format = "{0:." + str(float_decimal_places) + "f},"
        txt = f"{self.clipx_time},"
        if write_local_time:
            txt += f"{self.time},"
        if write_device_id:
            txt += f"{self.sensor_id},"
        txt += float_format.format(self.force)
        return txt[:-1]

class ForceSensor(ABC):

    def __init__(self, rs: RecordingSettings, buffer_size: int):
        self.ip_address = rs.ip_address
        self.signal_id = rs.signal_id
        self.bias = 0
        self._raw_sample_buffer = deque(maxlen=buffer_size)

    def determine_bias(self):
        self.bias = mean(self._raw_sample_buffer)

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def poll(self, n_max_samples:int=1)  -> list[ForceSensorData]:
        """returns last force data.

        Entire block of data can be received afterwards via self.last_clipx_data
        """
        pass


class ClipXForceSensor(ForceSensor):

    SAMPLINGRATE = 100

    def __init__(self, rs: RecordingSettings, buffer_size: int):
        super().__init__(rs, buffer_size)
        self.api = api.ClipXAPI()

    def start(self):
        if not self.api.is_connected():
            self.api.connect(self.ip_address)
            sleep(0.1)
        self.api.start_measurement()

    def stop(self):
        self.api.stop_measurement()
        self.api.disconnect()

    def poll(self, n_max_samples:int=1) -> list[ForceSensorData]:
        """returns last force data.

        Entire block of data can be received afterwards via self.last_clipx_data
        """

        data_clipx = self.api.read_next_block(n_max_samples)
        t = lsl.local_clock()
        rtn = []
        for d in data_clipx:
            f = d.values[self.signal_id]
            self._raw_sample_buffer.append(f)
            rtn.append(ForceSensorData(force=f - self.bias,time=t, clipx_time=d.time))
        return rtn


class MockForceSensor(ForceSensor):

    SAMPLINGRATE = 100

    def __init__(self, rs: RecordingSettings, buffer_size: int):
        super().__init__(rs, buffer_size)

        print("USING MOCK FORCE SENSOR!")
        self._started = False
        self._last_sample_time = 0
        self._cnt = 0

    def start(self):
        self._started = True

    def stop(self):
        self._started = False

    def poll(self, n_max_samples:int=1) -> list[ForceSensorData]:
        """returns (2D) array with [time, force].

        Entire block of data can be received afterwards via self.last_clipx_data
        """

        if not self._started:
            return []

        t = lsl.local_clock()
        if (t - self._last_sample_time) > 1/self.SAMPLINGRATE: # 1ms
            self._cnt += 1
            x = self._cnt / 100
            f = math.sin(x/2) * 10
            self._raw_sample_buffer.append(f)
            self._last_sample_time = t
            return [ForceSensorData(force=f - self.bias, time=t, clipx_time=t)]
        else:
            return []
