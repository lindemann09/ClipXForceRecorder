from time import asctime, localtime, time

import PySimpleGUI as sg
import readkeys

from . import APPNAME, LOGFILE, __version__
from .file_writer import FileWriter, unique_file_path
from .force_sensor_process import SensorProcess
from .settings import RecordingSettings

GUI_UPDATE_INTERVAL = 0.3  # seconds

class Recorder:
    """Sensor and a file writer to record data from the ClipX Force Sensor."""

    def __init__(self, cfg: RecordingSettings):
        self.cfg = cfg
        self.file_writer = None
        self.sensor = None

    def start(self, filename: str = "", lsl_stream: bool | None=None):

        self.cfg.save_data = len(filename) > 0
        if lsl_stream is not None:
            self.cfg.lsl_stream = lsl_stream

        if self.cfg.save_data:
            data_path = self.cfg.absolute_path_data(self.cfg.file_path.parent)
            self.file_writer = FileWriter(filepath=data_path / filename,
                                          write_local_time=self.cfg.add_local_time,
                                          append_mode=False)
            self.file_writer.start()
            self.file_writer.queue.put(self.cfg.asdict())

            txt = f"# Recorded at {asctime(localtime())} with {APPNAME} {__version__}\n"
            txt += "clipx_time,"
            if self.cfg.add_local_time:
                txt += "local_time,"
            txt += "force\n"
            self.file_writer.queue.put(txt)
            self.sensor = SensorProcess(self.cfg, self.file_writer.queue)
        else:
            self.file_writer = None
            self.sensor = SensorProcess(self.cfg, None)

        self.sensor.start()
        self.sensor.flag_sensor_bias_is_determined.wait()  # Wait until the sensor bias is determined

        if isinstance(self.file_writer, FileWriter):
            self.sensor.start_saving()

    def quit(self):

        if isinstance(self.sensor, SensorProcess):
            self.sensor.quit()
            self.sensor.join()
            self.sensor = None

        if isinstance(self.file_writer, FileWriter):
            self.file_writer.close_file()
            self.file_writer.join()
            self.file_writer = None

    def is_recording(self) -> bool:
        return isinstance(self.sensor, SensorProcess)

class RecorderGUI:
    FLOAT_FORMAT = "{0:.4f}"

    def __init__(self, cfg: RecordingSettings):

        self.ip_address = cfg.ip_address
        fr_settings = sg.Frame(
            "Settings",
            [
                [
                    sg.Checkbox("Save Data", cfg.save_data, key="save_data"),
                    sg.Checkbox("LSL stream", cfg.lsl_stream, key="lsl"),
                ],
                [
                    sg.Text("Filename:", size=(8, 1)),
                    sg.Input(default_text="clipx_data.csv", size=(24, 1), key="datafilename"),
                ],
            ],            size=(310, 80),

        )
        fr_info = sg.Frame(
            "Not recording",
            [
                [sg.Text("", key="DATA")],  # Text element
            ],
            size=(310, 50),
            key="INFO",
        )

        fr_buttons = sg.Frame("",
            [
                [
                    sg.Button(
                        "Start Recording",
                        size=(35, 1),
                        button_color=("black", "lightgreen"),
                        disabled_button_color=("black", "lightgrey"),
                        key="StartStop",
                    )
                ],
                [
                    sg.Button(
                        "Baseline",
                        size=(16, 1),
                        key="Baseline",
                    ),
                    sg.Button(
                        "Quit",
                        size=(16, 1),
                        key="QuitApp",
                    ),
                ]

            ],
        )
        self.layout = [
            [fr_settings],
            [fr_info],
            [fr_buttons],
        ]
        self.window = sg.Window(f"ClipX Force Recorder {__version__}", self.layout)
        self.event, self.values = self.window.read(
            timeout=0
        )  # Non-blocking read with timeout

        self.make_filename_unique()

    def set_recording_status(self, is_recording: bool):

        if is_recording:
            self.window["StartStop"].update(
                text="Stop", button_color=("black", "orange"), disabled=False)
            self.update(infodata=f"Recording from {self.ip_address}")
        else:
            self.window["StartStop"].update(
                text="Start Recording", button_color=("black", "lightgreen"), disabled=False)
            self.make_filename_unique()
            self.update(infodata="Recording Stopped")

    def update(self, infodata=None, data=None, timeout: float = 0):
        """Update the GUI with new data and return the event and values from the window.read() call."""
        self.event, self.values = self.window.read(
            timeout=timeout
        )  # Non-blocking read with timeout
        if infodata is not None:
            self.window["INFO"].update(infodata)  # type: ignore
        if data is not None:
            txt = (
                f" cnt: {data[0]} "
                + "      force: "
                + RecorderGUI.FLOAT_FORMAT.format(data[1])
            )
            self.window["DATA"].update(txt)  # type: ignore

    def close(self):
        self.window.close()

    def make_filename_unique(self):
        """Generate a unique file path by appending a number if the file already exists."""
        flname = unique_file_path(self.values["datafilename"])
        self.window["datafilename"].update(flname)  # type: ignore


def run(settings_file: str = "clipx_sensor.settings.toml"):

    print(f"ClipX Force Recorder {__version__}")
    print(f"Log file: {LOGFILE}")
    try:
        cfg = RecordingSettings.load(settings_file)
    except FileNotFoundError:
        print(
            f"\nCannot load settings file. Create a default settings file: {settings_file}"
            "\nPlease RESTART the program after editing the settings file."
        )
        RecordingSettings().save(settings_file)
        exit()

    recorder = Recorder(cfg)
    gui = RecorderGUI(cfg)

    cfg_info = str(cfg.asdict())[1:-1].replace(", ", "\n")
    if cfg.mock_sensor:
        cfg_info += "\n\nUSING MOCK FORCE SENSOR!"
    print(cfg_info)

    k = ""
    t = time()
    while True:
        if time() - t > GUI_UPDATE_INTERVAL:
            t = time()
            if isinstance(recorder.sensor, SensorProcess):
                cnt = recorder.sensor.get_total_sample_cnt()
                f = recorder.sensor.get_force()
                gui.update(data=[cnt, f])
        else:
            gui.update(timeout=GUI_UPDATE_INTERVAL * 1000.0)  # milliseconds

        if gui.event == "StartStop":

            if recorder.is_recording():
                answer = sg.popup_ok_cancel("Stop recording?", keep_on_top=True)
                if answer != "OK":
                    continue
                recorder.quit()
                gui.set_recording_status(False)
            else:
                if gui.values["save_data"]:
                    filename = gui.values["datafilename"]
                else:
                    filename = ""
                recorder.start(filename, gui.values["lsl"])
                gui.set_recording_status(True)

        elif gui.event == "Baseline":
            if recorder.is_recording():
                recorder.sensor.determine_bias()  # type: ignore

        elif gui.event == "QuitApp":
            if recorder.is_recording():
                answer = sg.popup_ok_cancel("Quit recording?", keep_on_top=True)
                if answer != "OK":
                    continue
            break

        elif gui.event == sg.WIN_CLOSED:
            break

        k = readkeys.getch(NONBLOCK=True)
        if k == "b":
            pass
            # sensor.bias = sensor.last_clipx_data[-1][cfg.signal_id]
        elif k == "q":
            break

    recorder.quit()
    gui.close()


if __name__ == "__main__":
    run()
