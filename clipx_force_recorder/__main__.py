
import sys

import readkeys

from .file_writer import FileWriter
from .force_sensor import ClipXForceSensor
from .lsl import LSLStream, cf_double64
from .settings import RecordingSettings


def run():

    settings_file = "sensor_settings.toml"
    try:
        cfg = RecordingSettings(settings_file)
    except FileNotFoundError:
        print(f"Can not load settings file. Create a default settings file: {settings_file}")
        RecordingSettings().save(settings_file)
        exit()

    print(cfg)

    file_writer = FileWriter("output.csv", float_decimal_places=6)
    file_writer.queue.put("Hello")
    lsl_data_stream = LSLStream()
    if cfg.lsl_stream: # LSL support
        lsl_data_stream.init(
                name=cfg.lsl_stream_name,
                content_type="force",
                n_channels=1,
                stream_id=f"cx",
                freq=1000,
                channel_format=cf_double64,
                metadata={},
            )

        print("LSL stream created")

    sensor = ClipXForceSensor(cfg)
    sensor.start()
    readkeys.flush()

    print(f"recording from {sensor.ip_address} \n")
    k = ""
    while True:
        data = sensor.poll()
        if len(data) > 0:
            if lsl_data_stream.is_init:
                for f in data[:, 1]:
                    lsl_data_stream.outlet.push_sample(f) # type: ignore #
            file_writer.queue.put(data)
            sys.stdout.write(f"{data[-1]} \r")

        k = readkeys.getch(NONBLOCK = True)
        if k == "b":
            sensor.set_baseline()
        elif k == "q":
            break
    print()
    sensor.stop()
    file_writer.close()
    file_writer.join()


if __name__ == "__main__":
    run()
