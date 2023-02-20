import json
import logging
import os
from collections.abc import Collection
from typing import Any, Self

import pytz

from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.mixins.json_serializable_mixin import JSONSerializableMixin


class _Settings(JSONSerializableMixin):
    def __init__(self) -> None:
        self._time_zone = pytz.utc

        self._logs_max_size_bytes = 1_000_000
        self._backups_max_size_bytes = 10_000_000

        self._backup_paths = []

    @property
    def time_zone(self) -> pytz._UTCclass | pytz.StaticTzInfo | pytz.DstTzInfo:
        return self._time_zone

    @time_zone.setter
    def time_zone(self, value: str) -> None:
        self._time_zone = pytz.timezone(value)

    @property
    def logs_max_size_bytes(self) -> int:
        return self._logs_max_size_bytes

    @logs_max_size_bytes.setter
    def logs_max_size_bytes(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("_Settings.logs_max_size_bytes must be an int.")
        if value < 0:
            raise ValueError("_Settings.logs_max_size_bytes must be positive.")
        self._logs_max_size_bytes = value

    @property
    def backups_max_size_bytes(self) -> int:
        return self._logs_max_size_bytes

    @backups_max_size_bytes.setter
    def backups_max_size_bytes(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("_Settings.backups_max_size_bytes must be an int.")
        if value < 0:
            raise ValueError("_Settings.backups_max_size_bytes must be positive.")
        self._backups_max_size_bytes = value

    @property
    def backup_paths(self) -> tuple[str]:
        return tuple(self._backup_paths)

    @backup_paths.setter
    def backup_paths(self, values: Collection[str]) -> None:
        if any(not isinstance(value, str) for value in values):
            raise TypeError("_Settings.backup_paths must be a Collection of strings.")
        for value in values:
            if not os.path.isdir(value):
                raise ValueError(f"Path '{value}' is not an existing directory.")
        self._backup_paths = list(values)

    def __repr__(self) -> str:
        return "_Settings"

    def serialize(self) -> dict[str, Any]:
        return {
            "datatype": "_Settings",
            "time_zone": self._time_zone.zone,
            "logs_max_size_bytes": self._logs_max_size_bytes,
            "backups_max_size_bytes": self._backups_max_size_bytes,
            "backup_paths": self._backup_paths,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Self:
        time_zone = pytz.timezone(data["time_zone"])
        logs_max_size_bytes = data["logs_max_size_bytes"]
        backups_max_size_bytes = data["backups_max_size_bytes"]
        backup_paths = data["backup_paths"]

        obj = _Settings()
        obj.time_zone = time_zone
        obj.logs_max_size_bytes = logs_max_size_bytes
        obj.backups_max_size_bytes = backups_max_size_bytes
        obj.backup_paths = backup_paths


def load_settings(path: str) -> None:
    if not os.path.isfile(path):
        raise ValueError(f"Path '{path}' does not point to a file.")

    global settings
    logging.debug(f"Loading _Settings: '{path}'")
    settings: _Settings = json.load(path, cls=CustomJSONDecoder)
    logging.info(f"_Settings loaded: '{path}'")


def save_settings(path: str) -> None:
    dirname = os.path.dirname(path)
    if not os.path.isdir(dirname):
        raise ValueError(f"Directory '{dirname}' does not exist.")

    logging.debug(f"Saving _Settings: '{path}'")
    json.dump(settings, path, cls=CustomJSONEncoder)
    logging.info(f"_Settings saved: '{path}'")


settings = _Settings()
