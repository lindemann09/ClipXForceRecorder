
from abc import ABC
from dataclasses import dataclass, field, is_dataclass
from pathlib import Path
from typing import Any

import tomlkit

from .api import get_signal_id


class ABCSettings(ABC):  # must be a dataclass

    def set_properties(self, property_dict: dict[str, Any]) -> bool:
        """return true is a properties of the data class is
        missing in the dict"""
        assert is_dataclass(self)

        for key, values in property_dict.items():
            if hasattr(self, key):
                setattr(self, key, values)
        # check all properties in dataclass have been set
        for class_property in self.__dataclass_fields__.keys():  # type: ignore
            if class_property not in property_dict:
                return True
        return False


@dataclass
class RecordingSettings(ABCSettings):

    ip_address: str = '10.144.71.141'
    signal_label: str  = "Field Value"
    lsl_stream: bool = True
    lsl_stream_name: str = "ClipXForce"
    save_data: bool = True
    data_folder: str = "data"
    add_local_time: bool = False
    file_path: Path = field(default_factory=lambda: Path().parent / "NO_SETTINGS_FILE.TXT")

    @property
    def signal_id(self) -> int:
        return get_signal_id(self.signal_label)

    def asdict(self) -> dict:
        rtn = dict(self.__dict__)
        del rtn["file_path"]
        return rtn

    @staticmethod
    def load(filepath: str| Path):
        filepath = Path(filepath)
        rtn = RecordingSettings(file_path=filepath)
        with open(filepath, "r", encoding="utf-8") as fl:
            d = tomlkit.load(fl)

        changes = rtn.set_properties(d)
        if changes:
            # missing property in settings file
            rtn.save()

        return rtn

    def save(self):
        with open(self.file_path, "w", encoding="utf-8") as fl:
            tomlkit.dump(self.asdict(), fl)

    def absolute_path_data(self, working_dir: str | Path) -> Path:
        fld = Path(self.data_folder)
        if fld.is_absolute():
            return fld
        else:
            return Path(working_dir).absolute() / fld

