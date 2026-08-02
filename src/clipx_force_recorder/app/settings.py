
from dataclasses import dataclass, field
from pathlib import Path

import tomlkit

from .api import get_signal_id


@dataclass
class RecordingSettings:

    ip_address: str = '10.144.71.141'
    signal_label: str  = "Field Value"
    lsl_stream: bool = True
    lsl_stream_name: str = "ClipXForce"
    save_data: bool = True
    data_folder: str = "data"
    mock_sensor: bool = False
    add_local_time: bool = False
    file_path: Path = field(default_factory=lambda: Path().parent / "NO_SETTINGS_FILE.TXT")

    @property
    def signal_id(self) -> int:
        return get_signal_id(self.signal_label)

    def asdict(self) -> dict:
        return {"ip_address": self.ip_address,
                "signal_label": self.signal_label,
                "lsl_stream": self.lsl_stream,
                "lsl_stream_name": self.lsl_stream_name,
                "save_data": self.save_data,
                "data_folder": self.data_folder,
                "mock_sensor": self.mock_sensor,
                "add_local_time": self.add_local_time}

    @staticmethod
    def load(filepath: str| Path):
        filepath = Path(filepath)
        rtn = RecordingSettings(file_path=filepath)
        with open(filepath, "r", encoding="utf-8") as fl:
            d = tomlkit.load(fl)
        if "ip_address" in d:
            rtn.ip_address = d["ip_address"]
        if "signal_label" in d:
            rtn.signal_label = d["signal_label"]
        if "lsl_stream" in d:
            rtn.lsl_stream = d["lsl_stream"]
        if "lsl_stream_name" in d:
            rtn.lsl_stream_name = d["lsl_stream_name"]
        if "save_data" in d:
            rtn.save_data = d["save_data"]
        if "data_folder" in d:
            rtn.data_folder = d["data_folder"]
        if "mock_sensor" in d:
            rtn.mock_sensor = d["mock_sensor"]
        if "add_local_time" in d:
            rtn.add_local_time = d["add_local_time"]
        return rtn

    def save(self, filename: str| Path):
        with open(Path(filename), "w", encoding="utf-8") as fl:
            tomlkit.dump(self.asdict(), fl)

    def absolute_path_data(self, working_dir: str | Path) -> Path:
        fld = Path(self.data_folder)
        if fld.is_absolute():
            return fld
        else:
            return Path(working_dir).absolute() / fld

