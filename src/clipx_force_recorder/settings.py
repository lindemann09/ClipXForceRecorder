
from dataclasses import dataclass
from pathlib import Path

import tomlkit

from .api import get_signal_id


@dataclass
class RecordingSettings(object):

    ip_address: str = "0.0.0.0.0"
    signal_label: str  = "Field Value"
    lsl_stream: bool = False
    lsl_stream_name: str = "ClipXForce"
    save_data: bool = False

    @property
    def signal_id(self) -> int:
        return get_signal_id(self.signal_label)

    def asdict(self) -> dict:
        return {"ip_address": self.ip_address,
                "signal_label": self.signal_label,
                "lsl_stream": self.lsl_stream,
                "lsl_stream_name": self.lsl_stream_name,
                "save_data": self.save_data}

    @staticmethod
    def load(filename: str| Path):
        rtn = RecordingSettings()
        with open(Path(filename), "r", encoding="utf-8") as fl:
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
        return rtn

    def save(self, filename: str| Path):
        with open(Path(filename), "w", encoding="utf-8") as fl:
            tomlkit.dump(self.asdict(), fl)

