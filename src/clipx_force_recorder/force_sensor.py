from abc import ABC, abstractmethod
from time import perf_counter, sleep

import numpy as np
from numpy.typing import NDArray

from . import api
from .settings import RecordingSettings

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

    def poll(self, n_max_samples:int=1) -> NDArray[np.float64]:
        """returns last force data.

        Entire block of data can be received afterwards via self.last_clipx_data
        """

        dat = self.api.read_next_block(n_max_samples)
        if len(dat)>0:
            data = np.array([[d.time, d.values[self.signal_id] - self._bias] for d in dat])
            return data
        else:
            return EMPTY_ARRAY


class MockForceSensor(ForceSensor):

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

    def poll(self, n_max_samples:int=1) -> NDArray[np.float64]:
        """returns last time_stamps force data.

        Entire block of data can be received afterwards via self.last_clipx_data
        """

        if not self._started:
            return EMPTY_ARRAY

        if (perf_counter() - self._last_sample_time) > 0.001: # 1ms
            self._cnt += 1
            x = self._cnt / 1000
            dat = 10 + np.array((np.sin(x/2), np.cos(x/5), np.sin(x),
                               np.sin(x/2), np.cos(x/5), np.sin(x))) * 10

            t = perf_counter()
            self._last_sample_time = t
            return np.array([[t, val] for val in dat.tolist()])
        else:
            return EMPTY_ARRAY





import atexit
import ctypes as ct
import logging
from collections import deque
from multiprocessing import Array, Event, Process, Queue, Value
from typing import Optional

import numpy as np
from numpy import typing as npt

from .lsl import LSLStream, cf_double64
from .settings import RecordingSettings

DETERMINE_BIAS_SAMPLES = 100

class SensorProcess(Process):

    def __init__(
        self,
        recording_settings: RecordingSettings,
        file_writer_queue: Optional[Queue],
    ):
        """ForceSensorProcess
        """

        # DOC explain usage

        super(SensorProcess, self).__init__()

        self.cfg = recording_settings
        self._file_writer_queue = file_writer_queue

        self._dat = Array(ct.c_double, 2)
        self._np_dat = np.frombuffer(
            self._dat.get_obj(), dtype=np.float64
        )  # numpy view
        self._saved_sample_cnt = Value(ct.c_int64, 0)
        self._total_sample_cnt = Value(ct.c_int64, 0)
        self.flag_sensor_bias_is_determined = Event()
        self._flag_quit_request = Event()
        self.__flag_is_saving = Event()

        atexit.register(self.join)


    def get_force(self) -> npt.NDArray[np.float64]:
        return self._np_dat

    def get_saved_sample_cnt(self) -> int:
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
        return self.__flag_is_saving.is_set()

    def quit(self):
        self._flag_quit_request.set()

    def join(self, timeout=None):
        self._flag_quit_request.set()
        super(SensorProcess, self).join(timeout)


    def run(self):

        fifo = deque(maxlen=DETERMINE_BIAS_SAMPLES)
        if self.cfg.mock_sensor:
            sensor = MockForceSensor(self.cfg)
            print("recording from Mock sensor \n\n")

        else:
            sensor = ClipXForceSensor(self.cfg)
            print(f"recording from {sensor.ip_address} \n\n")

        ## create init LSL
        lsl_data_stream = LSLStream()
        if self.cfg.lsl_stream: # LSL support
            lsl_data_stream.init(
                    name=self.cfg.lsl_stream_name,
                    content_type="force",
                    n_channels=2,
                    stream_id=f"cx",
                    freq=1000,
                    channel_format=cf_double64,
                    metadata={},
                )

            print("LSL stream created")

        sensor.start()

        # polling loop
        self.pause_saving()
        self._flag_quit_request.clear()
        self.flag_sensor_bias_is_determined.clear()
        init_samples = DETERMINE_BIAS_SAMPLES * 2

        while not self._flag_quit_request.is_set():

            data = sensor.poll()
            n = len(data)
            if n > 0:
                for d in data:
                    if init_samples > 0:
                        # initial samples for bias determination, do not write to LSL or file writer queue
                        init_samples -= n
                        fifo.append(d[1])
                        if init_samples <1:
                            sensor.bias = np.mean(fifo)
                            self.flag_sensor_bias_is_determined.set()
                        continue

                    ## LSL
                    lsl_data_stream.push_sample(d[1])
                    fifo.append(d[1]) # for bias determination

                # write to shared memory and file writer queue
                self._total_sample_cnt.value += n

            if self.is_saving() and self._file_writer_queue is not None:
                self._file_writer_queue.put(data)
                self._saved_sample_cnt.value += n

            if not self.flag_sensor_bias_is_determined.is_set():
                # new baseline requested
                sensor.bias = np.mean(fifo)
                self.flag_sensor_bias_is_determined.set()

        # stop process
        self.pause_saving()
        sensor.stop()

