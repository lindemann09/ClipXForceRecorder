from time import sleep, time

import PySimpleGUI as sg
import readkeys

from . import __version__
from .file_writer import FileWriter, unique_file_path
from .force_sensor import SensorProcess
from .settings import RecordingSettings

GUI_UPDATE_INTERVAL = 0.1  # seconds


class RecorderGUI:
    FLOAT_FORMAT = "{0:.4f}"

    def __init__(self, cfg: RecordingSettings):

        if cfg.save_data:
            flname = unique_file_path("output.csv")
        else:
            flname = ""

        fr_settings = sg.Frame(
            "Settings",
            [
                [
                    sg.Checkbox("Save Data", cfg.save_data, key="save_data"),
                    sg.Checkbox("LSL stream", cfg.lsl_stream, key="lsl"),
                ],
                [
                    sg.Text("Filename:", size=(8, 1)),
                    sg.Input(default_text=flname, size=(24, 1), key="datafilename"),
                ],
            ],            size=(310, 80),

        )
        fr_info = sg.Frame(
            "Recording",
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
                        size=(17.5, 1.2),
                        button_color=("black", "lightgreen"),
                        disabled_button_color=("black", "lightgrey"),
                        key="Start",
                    ),
                    sg.Button(
                        "Quit",
                        size=(8, 1.2),
                        disabled_button_color=("grey", "lightgrey"),
                        disabled=True,
                        key="Quit",
                    ),
                ]
            ],
        )
        self.layout = [
            [fr_settings],
            [fr_info],
            [fr_buttons],
        ]
        self.window = sg.Window("ClipX Force Recorder", self.layout)
        self.event, self.values = self.window.read(
            timeout=0
        )  # Non-blocking read with timeout

    def update(self, infodata=None, data=None):
        """Update the GUI with new data and return the event and values from the window.read() call."""
        self.event, self.values = self.window.read(
            timeout=0
        )  # Non-blocking read with timeout
        if infodata is not None:
            self.window["INFO"].update(infodata)  # type: ignore
        if data is not None:
            txt = (
                f" {data[0]}, "
                + RecorderGUI.FLOAT_FORMAT.format(data[1])
                + ", "
                + RecorderGUI.FLOAT_FORMAT.format(data[2])
            )
            self.window["DATA"].update(txt)  # type: ignore

    def close(self):
        self.window.close()


def run(settings_file: str = "clipx_sensor.settings.toml"):

    print(f"ClipX Force Recorder {__version__}")
    try:
        cfg = RecordingSettings.load(settings_file)
    except FileNotFoundError:
        print(
            f"Can not load settings file. Create a default settings file: {settings_file}"
        )
        RecordingSettings().save(settings_file)
        exit()

    gui = RecorderGUI(cfg)

    cfg_info = str(cfg.asdict())[1:-1].replace(", ", "\n")
    if cfg.mock_sensor:
        cfg_info += "\n\nUSING MOCK FORCE SENSOR!"
    print(cfg_info)

    file_writer = FileWriter()
    sensor = SensorProcess(cfg, file_writer.queue)

    k = ""
    t = time()
    while True:
        if time() - t > GUI_UPDATE_INTERVAL:
            if sensor.is_alive():
                cnt = sensor.get_total_sample_cnt()
                data = sensor.get_force().tolist()
                gui.update(data=[cnt] + data)
            else:
                gui.update(infodata="Not recording!")

        if gui.event == "Start" and not sensor.is_alive():
            sensor.cfg.save_data = gui.values["save_data"]
            sensor.cfg.lsl_stream = gui.values["lsl"]
            sensor.start()
            sleep(0.1)  # give file writer time to start

            if sensor.cfg.save_data:
                file_writer.set_file(gui.values["datafilename"], append_mode=False)
                file_writer.start()
                sensor.start_saving()

            gui.window["Start"].update(disabled=True)
            gui.window["Quit"].update(disabled=False)
            gui.update(infodata=f"Recording from {cfg.ip_address}")

        k = readkeys.getch(NONBLOCK=True)
        if k == "b":
            pass
            # sensor.bias = sensor.last_clipx_data[-1][cfg.signal_id]
        elif k == "q" or gui.event == sg.WIN_CLOSED or gui.event == "Quit":
            break

    gui.update(infodata="Stopping")
    sensor.quit()
    sensor.join()

    if file_writer.is_alive():
        file_writer.close_file()
        file_writer.join()


    gui.close()


if __name__ == "__main__":
    run()
