import math
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from time import sleep

from . import api
from .settings import RecordingSettings
from .tools import lsl
from .tools.data import DataBuffer
from .tools.file_writer import AbstractCSVDataStruct, AbstractFileWriter


@dataclass
class ForceSensorData(AbstractCSVDataStruct):
    """Data class to hold force data."""
    force: float
    time: float
    clipx_time: float
    sensor_id: int = 0


class ForceSensor(ABC):

    def __init__(self, rs: RecordingSettings, buffer_size: int):
        self.ip_address = rs.ip_address
        self.signal_id = rs.signal_id
        self.bias = 0
        self._raw_sample_buffer = DataBuffer(maxlen=buffer_size)

    def determine_bias(self):
        self.bias = self._raw_sample_buffer.buffer_mean()[0]

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
            rtn.append(ForceSensorData(force= f - self.bias, time=t, clipx_time=d.time))
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


class SensorDataWriter(AbstractFileWriter):

    def __init__(
        self,
        filepath: Path|str,
        write_local_time: bool,
        append_mode: bool = False,
        write_deviceid: bool = False,
        float_decimal_places: int = 6):

        super().__init__(filepath, append_mode)

        self._write_local_time = write_local_time
        self._write_deviceid = write_deviceid
        self._decimal_places = float_decimal_places


    def to_csv(self, data: ForceSensorData) -> str:
        """converts data to string."""

        float_format = "{0:." + str(self._decimal_places) + "f},"
        txt = f"{data.clipx_time},"
        if self._write_local_time:
            txt += f"{data.time},"
        if self._write_deviceid:
            txt += f"{data.sensor_id},"
        txt += float_format.format(data.force)
        return txt[:-1]
