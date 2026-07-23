from time import sleep
from typing import List

import numpy as np
from numpy.typing import NDArray

from . import api
from .settings import RecordingSettings

import sys
import os

class ClipXForceSensor:

    def __init__(self, rs: RecordingSettings):

        self.signal_id = rs.signal_id
        self.ip_address = rs.ip_address
        self.api = api.ClipXAPI()
        self.last_clipx_data: List[api.ClipXData]= []

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
            return np.asarray([[d.time, d.values[self.signal_id]] for d in dat])
        else:
            return None

    def set_baseline(self):
        print("Setting baseline...") ## TODO not yet implemented