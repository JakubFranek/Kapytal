import logging
from collections.abc import Collection
from pathlib import Path
from typing import Any, Self
from zoneinfo import ZoneInfo

from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from tzlocal import get_localzone_name

# TODO: add setting for default datetime filter?


class UserSettings(JSONSerializableMixin):
    """This class is intended to be instantiated only once, within user_settings."""

    __slots__ = (
        "_time_zone",
        "_logs_max_size_bytes",
        "_backups_max_size_bytes",
        "_backup_paths",
    )

    LOGS_DEFAULT_MAX_SIZE = 1_000_000
    BACKUPS_DEFAULT_MAX_SIZE = 10_000_000

    def __init__(self) -> None:
        self._time_zone = ZoneInfo(get_localzone_name())

        self._logs_max_size_bytes = UserSettings.LOGS_DEFAULT_MAX_SIZE
        self._backups_max_size_bytes = UserSettings.BACKUPS_DEFAULT_MAX_SIZE

        self._backup_paths = []

    @property
    def time_zone(self) -> ZoneInfo:
        return self._time_zone

    @time_zone.setter
    def time_zone(self, time_zone: ZoneInfo) -> None:
        if not isinstance(time_zone, ZoneInfo):
            raise TypeError("UserSettings.time_zone must be a ZoneInfo.")

        if self._time_zone == time_zone:
            return

        logging.info(
            f"Changing UserSettings.time_zone from {self._time_zone} to {time_zone}"
        )
        self._time_zone = time_zone

    @property
    def logs_max_size_bytes(self) -> int:
        return self._logs_max_size_bytes

    @logs_max_size_bytes.setter
    def logs_max_size_bytes(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("UserSettings.logs_max_size_bytes must be an int.")
        if value < 0:
            raise ValueError("UserSettings.logs_max_size_bytes must be positive.")
        if self._logs_max_size_bytes == value:
            return

        logging.info(
            "Changing UserSettings.logs_max_size_bytes from "
            f"{self._logs_max_size_bytes:,} to {value:,}"
        )
        self._logs_max_size_bytes = value

    @property
    def backups_max_size_bytes(self) -> int:
        return self._backups_max_size_bytes

    @backups_max_size_bytes.setter
    def backups_max_size_bytes(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("UserSettings.backups_max_size_bytes must be an int.")
        if value < 0:
            raise ValueError("UserSettings.backups_max_size_bytes must be positive.")
        if self._backups_max_size_bytes == value:
            return

        logging.info(
            "Changing UserSettings.backups_max_size_bytes from "
            f"{self._backups_max_size_bytes:,} to {value:,}"
        )
        self._backups_max_size_bytes = value

    @property
    def backup_paths(self) -> tuple[Path, ...]:
        return tuple(self._backup_paths)

    @backup_paths.setter
    def backup_paths(self, values: Collection[Path]) -> None:
        if any(not isinstance(value, Path) for value in values):
            raise TypeError("UserSettings.backup_paths must be a Collection of Paths.")

        values_set = set(values)
        if len(values_set) < len(values):
            raise ValueError(
                "UserSettings.backup_paths must not contain duplicate Paths."
            )

        for value in values:
            if not value.is_dir():
                raise ValueError(
                    f"Path {value} does not point to an existing directory."
                )

        new_values = [value for value in values if value not in self._backup_paths]
        deleted_values = [value for value in self._backup_paths if value not in values]

        for new_value in new_values:
            logging.info(f"Adding backup path: {new_value}")
        for deleted_value in deleted_values:
            logging.info(f"Removing backup path: {deleted_value}")

        self._backup_paths: list[Path] = list(values)

    def __repr__(self) -> str:
        return "UserSettings"

    def serialize(self) -> dict[str, Any]:
        backup_paths = [str(path) for path in self._backup_paths]
        return {
            "datatype": "UserSettings",
            "time_zone": self._time_zone.key,
            "logs_max_size_bytes": self._logs_max_size_bytes,
            "backups_max_size_bytes": self._backups_max_size_bytes,
            "backup_paths": backup_paths,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> Self:
        time_zone = ZoneInfo(data["time_zone"])
        logs_max_size_bytes: int = data["logs_max_size_bytes"]
        backups_max_size_bytes: int = data["backups_max_size_bytes"]

        backup_path_strings: list[str] = data["backup_paths"]
        backup_paths = [Path(string) for string in backup_path_strings]

        obj = UserSettings()
        obj._time_zone = time_zone  # noqa: SLF001
        obj._logs_max_size_bytes = logs_max_size_bytes  # noqa: SLF001
        obj._backups_max_size_bytes = backups_max_size_bytes  # noqa: SLF001
        obj._backup_paths = backup_paths  # noqa: SLF001

        return obj
