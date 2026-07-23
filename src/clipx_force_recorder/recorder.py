
import PySimpleGUI as sg
import readkeys

from . import __version__
from .file_writer import FileWriter
from .force_sensor import ClipXForceSensor, MockForceSensor
from .lsl import LSLStream, cf_double64
from .settings import RecordingSettings


class RecorderGUI:

    FLOAT_FORMAT = "{0:.4f}"

    def __init__(self):

        self.layout = [
            [sg.Text("", key="INFO")],  # Text element
            [sg.Multiline("This is a non-editable\nmultiline text box", disabled=True, size=(30, 10), key="CFG_INFO")],  # Non-editable
            [sg.Text("", key="DATA")],  # Text element
            [sg.Button("Close")],     # Button element
        ]
        self.window = sg.Window("ClipX Force Recorder", self.layout)
        self.event, self.values = self.window.read(timeout=0)  # Non-blocking read with timeout

    def update(self, infodata=None, cfg_info=None, data=None):
        """Update the GUI with new data and return the event and values from the window.read() call."""
        self.event, self.values = self.window.read(timeout=0)  # Non-blocking read with timeout
        if infodata is not None:
            self.window["INFO"].update(infodata) # type: ignore
        if cfg_info is not None:
            self.window["CFG_INFO"].update(cfg_info) # type: ignore
        if data is not None:
            txt = f" {data[0]}, " + RecorderGUI.FLOAT_FORMAT.format(data[1]) + ", " + \
                        RecorderGUI.FLOAT_FORMAT.format(data[2])
            self.window["DATA"].update(txt) # type: ignore

    def close(self):
        self.window.close()


def run(settings_file: str = "clipx_sensor.settings.toml", mock_sensor: bool = False):

    gui = RecorderGUI()

    print(f"ClipX Force Recorder {__version__}")
    try:
        cfg = RecordingSettings.load(settings_file)
    except FileNotFoundError:
        print(f"Can not load settings file. Create a default settings file: {settings_file}")
        RecordingSettings().save(settings_file)
        exit()

    cfg_info = str(cfg.asdict())[1:-1].replace(", ", "\n")

    print(cfg_info)

    file_writer = FileWriter("output.csv", float_decimal_places=6)
    file_writer.start()
    #file_writer.queue.put("#Hello")

    lsl_data_stream = LSLStream()
    if cfg.lsl_stream: # LSL support
        lsl_data_stream.init(
                name=cfg.lsl_stream_name,
                content_type="force",
                n_channels=2,
                stream_id=f"cx",
                freq=1000,
                channel_format=cf_double64,
                metadata={},
            )

        print("LSL stream created")

    if mock_sensor:
        sensor = MockForceSensor(cfg)
        cfg_info += "\n\nUSING MOCK FORCE SENSOR!"
    else:
        sensor = ClipXForceSensor(cfg)
    sensor.start()
    #readkeys.flush()

    print(f"recording from {sensor.ip_address} \n\n")

    gui.update(infodata=f"Recording from {sensor.ip_address}", cfg_info=cfg_info)
    k = ""
    while True:
        data = sensor.poll()
        if data is not None:
            if lsl_data_stream.is_init:
                for d in data:
                    lsl_data_stream.outlet.push_sample(d) # type: ignore #

            file_writer.queue.put(data)
            gui.update(data=[sensor.cnt] + data[-1].tolist())
        else:
            gui.update()

        k = readkeys.getch(NONBLOCK = True)
        if k == "b":
            sensor.set_baseline()
        elif k == "q" or gui.event == sg.WIN_CLOSED or gui.event == "Close":
            break

    sensor.stop()
    print("Recording stopped")
    gui.close()
    file_writer.close_file()
    file_writer.join()


if __name__ == "__main__":
    run()
