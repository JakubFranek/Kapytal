import logging
import os
from collections.abc import Collection
from typing import Any, Self
from zoneinfo import ZoneInfo

from src.models.mixins.json_serializable_mixin import JSONSerializableMixin


class UserSettings(JSONSerializableMixin):
    """This class is intended to be instantiated only once, within user_settings."""

    def __init__(self) -> None:
        self._time_zone = ZoneInfo("UTC")

        self._logs_max_size_bytes = 1_000_000
        self._backups_max_size_bytes = 10_000_000

        self._backup_paths = []

    @property
    def time_zone(self) -> ZoneInfo:
        return self._time_zone

    @time_zone.setter
    def time_zone(self, time_zone: ZoneInfo) -> None:
        if self._time_zone == time_zone:
            return

        logging.info(
            f"Changing _Settings.time_zone from {self._time_zone} to {time_zone}"
        )
        self._time_zone = time_zone

    @property
    def logs_max_size_bytes(self) -> int:
        return self._logs_max_size_bytes

    @logs_max_size_bytes.setter
    def logs_max_size_bytes(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("_Settings.logs_max_size_bytes must be an int.")
        if value < 0:
            raise ValueError("_Settings.logs_max_size_bytes must be positive.")
        if self._logs_max_size_bytes == value:
            return

        logging.info(
            "Changing _Settings.logs_max_size_bytes from "
            f"{self._logs_max_size_bytes} to {value}"
        )
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
        if self._backups_max_size_bytes == value:
            return

        logging.info(
            "Changing _Settings.backups_max_size_bytes from "
            f"{self._backups_max_size_bytes} to {value}"
        )
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

        new_values = [value for value in values if value not in self._backup_paths]
        deleted_values = [value for value in self._backup_paths if value not in values]

        for new_value in new_values:
            logging.info(f"Adding backup path: '{new_value}'")
        for deleted_value in deleted_values:
            logging.info(f"Removing backup path: '{deleted_value}'")

        self._backup_paths = list(values)

    def __repr__(self) -> str:
        return "UserSettings"

    def serialize(self) -> dict[str, Any]:
        return {
            "datatype": "UserSettings",
            "time_zone": self._time_zone.key,
            "logs_max_size_bytes": self._logs_max_size_bytes,
            "backups_max_size_bytes": self._backups_max_size_bytes,
            "backup_paths": self._backup_paths,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Self:
        time_zone = ZoneInfo(data["time_zone"])
        logs_max_size_bytes = data["logs_max_size_bytes"]
        backups_max_size_bytes = data["backups_max_size_bytes"]
        backup_paths = data["backup_paths"]

        obj = UserSettings()
        obj.time_zone = time_zone
        obj.logs_max_size_bytes = logs_max_size_bytes
        obj.backups_max_size_bytes = backups_max_size_bytes
        obj.backup_paths = backup_paths

        return obj
