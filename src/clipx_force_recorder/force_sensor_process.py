import atexit
import ctypes as ct
import os
from multiprocessing import Event, Process, Queue, Value
from typing import Optional

from .force_sensor import ClipXForceSensor, MockForceSensor
from .settings import RecordingSettings
from .tools import lsl


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
        self._total_sample_cnt = Value(ct.c_int64, 0)
        self.flag_sensor_bias_is_determined = Event()
        self._flag_quit_request = Event()
        self.__flag_is_saving = Event()

        atexit.register(self.join)


    def get_force(self) -> float:
        with self._dat.get_lock():
            return self._dat.value

    def get_total_sample_cnt(self) -> int:
        with self._total_sample_cnt.get_lock():
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
        if self.cfg.mock_sensor:
            sensor = MockForceSensor(self.cfg,
                                     buffer_size=SensorProcess.DETERMINE_BIAS_SAMPLES)
        else:
            sensor = ClipXForceSensor(self.cfg,
                                     buffer_size=SensorProcess.DETERMINE_BIAS_SAMPLES)

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
                ## LSL
                if lsl_data_stream is not None:
                    for d in data:
                        lsl_data_stream.push_sample([d.force], timestamp=d.time) # local time, force

                # write to shared memory
                with self._total_sample_cnt.get_lock():
                    self._total_sample_cnt.value += 1
                with self._dat.get_lock():
                    self._dat.value = d.force  # last sample to shared memory

                # file writer
                if self.is_saving() and self._file_writer_queue is not None:
                    self._file_writer_queue.put(d)

                if not self.flag_sensor_bias_is_determined.is_set():
                    # new baseline requested
                    sensor.determine_bias()
                    self.flag_sensor_bias_is_determined.set()

        # stop process
        self.pause_saving()
        sensor.stop()

