import atexit
import ctypes as ct
import os
from abc import ABC, abstractmethod
from collections import deque
from multiprocessing import Event, Process, Queue, Value
from time import sleep
from typing import Optional

import numpy as np
from numpy.typing import NDArray

from . import api, lsl
from .settings import RecordingSettings
from .types import ForceSensorData

EMPTY_ARRAY = np.array([], dtype=np.float64)


class ForceSensor(ABC):

    def __init__(self, rs: RecordingSettings):
        self.ip_address = rs.ip_address
        self.signal_id = rs.signal_id
        self._bias = 0

    @property
    def bias(self) -> float:
        return self._bias

    @bias.setter
    def bias(self, value: float):
        self._bias = value

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def poll(self, n_max_samples:int=1) -> NDArray[np.float64]:
        """returns last force data.

        Entire block of data can be received afterwards via self.last_clipx_data
        """
        pass


class ClipXForceSensor(ForceSensor):

    SAMPLINGRATE = 100

    def __init__(self, rs: RecordingSettings):
        super().__init__(rs)
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
        return [ForceSensorData(force=d.values[self.signal_id] - self._bias,
                          time=t,
                          clipx_time=d.time)
                for d in data_clipx]

class MockForceSensor(ForceSensor):

    SAMPLINGRATE = 100

    def __init__(self, rs: RecordingSettings):
        super().__init__(rs)

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
            dat = np.array((np.sin(x/2), np.cos(x/5), np.sin(x),
                               np.sin(x/2), np.cos(x/5), np.sin(x))) * 10

            self._last_sample_time = t
            return [ForceSensorData(force=dat[self.signal_id] - self._bias, time=t, clipx_time=t)]
        else:
            return []



class SensorProcess(Process):

    DETERMINE_BIAS_SAMPLES = 10


    def __init__(
        self,
        recording_settings: RecordingSettings,
        file_writer_queue: Optional[Queue]
    ):
        """ForceSensorProcess
        """

        # DOC explain usage

        super().__init__()

        self.cfg = recording_settings
        self.stream_id = f"cx_{os.getpid()}"
        self._file_writer_queue = file_writer_queue

        self._dat = Value(ct.c_double, 0)
        self._saved_sample_cnt = Value(ct.c_int64, 0)
        self._total_sample_cnt = Value(ct.c_int64, 0)
        self.flag_sensor_bias_is_determined = Event()
        self._flag_quit_request = Event()
        self.__flag_is_saving = Event()

        atexit.register(self.join)


    def get_force(self) -> float:
        return self._dat.value

    def get_saved_sample_cnt(self) -> int:
        """Return the number of samples that have been written to storage."""
        return self._saved_sample_cnt.value

    def get_total_sample_cnt(self) -> int:
        return self._total_sample_cnt.value

    def determine_bias(self):
        self.flag_sensor_bias_is_determined.clear()

    def start_saving(self):
        if self._file_writer_queue is not None:
            self.__flag_is_saving.set()

    def pause_saving(self):
        self.__flag_is_saving.clear()

    def is_saving(self) -> bool:

        return self._file_writer_queue is not None and self.__flag_is_saving.is_set()

    def quit(self):
        self._flag_quit_request.set()

    def join(self, timeout=None):
        self._flag_quit_request.set()
        super().join(timeout)


    def run(self):

        self.__flag_is_saving.clear()
        self._flag_quit_request.clear()
        self.flag_sensor_bias_is_determined.clear()
        fifo = deque(maxlen=SensorProcess.DETERMINE_BIAS_SAMPLES)
        t = 0.0

        if self.cfg.mock_sensor:
            sensor = MockForceSensor(self.cfg)
        else:
            sensor = ClipXForceSensor(self.cfg)

        ## create init LSL
        if self.cfg.lsl_stream: # LSL support
            lsl_data_stream = lsl.init_stream(
                    name=self.cfg.lsl_stream_name,
                    content_type="force",
                    n_channels=1,
                    stream_id=self.stream_id,
                    freq=sensor.SAMPLINGRATE,
                    channel_format=lsl.cf_double64,
                    metadata={},
                )
            print("LSL stream created")
        else:
            lsl_data_stream = None


        print(f"recording from {sensor.ip_address} \n\n")
        sensor.start()

        # polling loop
        while not self._flag_quit_request.is_set():

            data = sensor.poll() # time, force
            for d in data:
                fifo.append(d.force) # add all force values to fifo for bias determination
                ## LSL
                if lsl_data_stream is not None:
                    for d in data:
                        lsl_data_stream.push_sample([d.force], timestamp=d.time) # local time, force

                # write to shared memory
                self._total_sample_cnt.value += 1
                self._dat.value = d.force  # last sample to shared memory

                # file writer
                if self.is_saving():
                    self._file_writer_queue.put(d)
                    self._saved_sample_cnt.value += 1

                if not self.flag_sensor_bias_is_determined.is_set():
                    # new baseline requested
                    sensor.bias = np.mean(fifo)
                    self.flag_sensor_bias_is_determined.set()

        # stop process
        self.pause_saving()
        sensor.stop()

