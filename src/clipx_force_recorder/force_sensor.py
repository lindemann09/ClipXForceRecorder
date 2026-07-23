from time import perf_counter, sleep
from typing import List

import numpy as np
from numpy.typing import NDArray

from . import api
from .settings import RecordingSettings


class ClipXForceSensor:

    def __init__(self, rs: RecordingSettings):

        self.signal_id = rs.signal_id
        self.ip_address = rs.ip_address
        self.api = api.ClipXAPI()
        self.last_clipx_data: List[api.ClipXData]= []
        self.cnt = 0

    def start(self):
        if not self.api.is_connected():
            self.api.connect(self.ip_address)
            sleep(0.1)
        self.api.start_measurement()

    def stop(self):
        self.api.stop_measurement()
        self.api.disconnect()

    def poll(self, n_max_samples:int=1) -> NDArray[np.float64] | None:
        """returns last time_stamps force data.

        Entire block of data can be received afterwards via self.last_clipx_data
        """

        dat = self.api.read_next_block(n_max_samples)
        if len(dat)>0:
            self.last_clipx_data = dat
            self.cnt += len(dat)
            return np.array([[d.time, d.values[self.signal_id]] for d in dat])
        else:
            return None

    def set_baseline(self):
        print("Setting baseline...") ## TODO not yet implemented


class MockForceSensor:

    def __init__(self, rs: RecordingSettings):
        print("USING MOCK FORCE SENSOR!")
        self.signal_id = rs.signal_id
        self.ip_address = rs.ip_address
        self.api = None
        self.last_clipx_data: List[api.ClipXData]= []
        self._started = False
        self.cnt = 0

    def start(self):
        self._started = True

    def stop(self):
        self._started = False

    def poll(self, n_max_samples:int=1) -> NDArray[np.float64] | None:
        """returns last time_stamps force data.

        Entire block of data can be received afterwards via self.last_clipx_data
        """

        if not self._started:
            return None

        if len(self.last_clipx_data) == 0:
            last_sample_time = 0
        else:
            last_sample_time = self.last_clipx_data[-1].time

        if (perf_counter() - last_sample_time) > 0.001: # 1ms
            self.cnt += 1
            x = self.cnt / 1000
            dat = 10 + np.array((np.sin(x/2), np.cos(x/5), np.sin(x),
                               np.sin(x/2), np.cos(x/5), np.sin(x))) * 10

            t = perf_counter()
            self.last_clipx_data = [api.ClipXData(t, dat.tolist())]

            return np.array([[t, dat[3]]])
        else:
            return None

    def set_baseline(self):
        print("Setting baseline...") ## TODO not yet implemented