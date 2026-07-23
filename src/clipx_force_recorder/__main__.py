
import readkeys

from . import __version__
from .file_writer import FileWriter
from .force_sensor import ClipXForceSensor
from .lsl import LSLStream, cf_double64
from .settings import RecordingSettings


def run(settings_file: str = "clipx_sensor.settings.toml"):

    print(f"ClipX Force Recorder {__version__}")
    try:
        cfg = RecordingSettings.load(settings_file)
    except FileNotFoundError:
        print(f"Can not load settings file. Create a default settings file: {settings_file}")
        RecordingSettings().save(settings_file)
        exit()

    print(cfg)

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

    sensor = ClipXForceSensor(cfg)
    sensor.start()
    #readkeys.flush()

    print(f"recording from {sensor.ip_address} \n\n")
    k = ""
    while True:
        data = sensor.poll()
        if data is not None:
            if lsl_data_stream.is_init:
                for d in data:
                    lsl_data_stream.outlet.push_sample(d) # type: ignore #

            file_writer.queue.put(data)

            print(f"-- {data[-1]}")

        k = readkeys.getch(NONBLOCK = True)
        if k == "b":
            sensor.set_baseline()
        elif k == "q":
            break
    print()
    sensor.stop()
    print("Recording stopped")

    file_writer.close_file()
    file_writer.join()


if __name__ == "__main__":
    run()
