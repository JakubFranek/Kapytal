import locale
import logging
from collections.abc import Collection, Sequence
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from src.models.mixins.copyable_mixin import CopyableMixin
from src.models.mixins.json_serializable_mixin import JSONSerializableMixin
from src.views.constants import TransactionTableColumn
from tzlocal import get_localzone_name


class NumberFormat(Enum):
    SEP_COMMA_DECIMAL_POINT = "1,234.5678"
    SEP_POINT_DECIMAL_COMMA = "1.234,5678"
    SEP_SPACE_DECIMAL_POINT = "1\xa0234.5678"  # \xa0 is non-breaking space
    SEP_SPACE_DECIMAL_COMMA = "1\xa0234,5678"
    SEP_NONE_DECIMAL_POINT = "1234.5678"


class UserSettings(JSONSerializableMixin, CopyableMixin):
    """This class is intended to be instantiated only once, within user_settings."""

    __slots__ = (
        "_amount_per_share_decimals",
        "_backup_paths",
        "_backups_max_size_bytes",
        "_check_for_updates_on_startup",
        "_exchange_rate_decimals",
        "_general_date_format",
        "_logs_max_size_bytes",
        "_number_format",
        "_time_zone",
        "_transaction_date_format",
        "_transaction_table_column_order",
    )

    LOGS_DEFAULT_MAX_SIZE = 1_000_000
    BACKUPS_DEFAULT_MAX_SIZE = 100_000_000

    def __init__(self) -> None:
        self._time_zone = ZoneInfo(get_localzone_name())

        self._logs_max_size_bytes = UserSettings.LOGS_DEFAULT_MAX_SIZE
        self._backups_max_size_bytes = UserSettings.BACKUPS_DEFAULT_MAX_SIZE

        self._general_date_format = "%d.%m.%Y"
        self._transaction_date_format = "%d.%m.%Y"

        self._number_format: NumberFormat = _get_number_format_for_locale()

        self._exchange_rate_decimals = 4
        self._amount_per_share_decimals = 4

        self._backup_paths = []

        self._check_for_updates_on_startup = True

        self._transaction_table_column_order = ()

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
            f"{self._logs_max_size_bytes} to {value}"
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
            f"{self._backups_max_size_bytes} to {value}"
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

    @property
    def transaction_date_format(self) -> str:
        return self._transaction_date_format

    @transaction_date_format.setter
    def transaction_date_format(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("UserSettings.transaction_date_format must be a str.")

        try:
            datetime.now(tz=self._time_zone).strftime(value)
        except ValueError as exception:
            raise ValueError(
                "UserSettings.transaction_date_format must be a valid format."
            ) from exception

        if self._transaction_date_format == value:
            return

        logging.info(
            "Changing UserSettings.transaction_date_format from "
            f"{self._transaction_date_format} to {value}"
        )
        self._transaction_date_format = value

    @property
    def general_date_format(self) -> str:
        return self._general_date_format

    @general_date_format.setter
    def general_date_format(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("UserSettings.general_date_format must be a str.")

        try:
            datetime.now(tz=self._time_zone).strftime(value)
        except ValueError as exception:
            raise ValueError(
                "UserSettings.general_date_format must be a valid format."
            ) from exception

        if self._general_date_format == value:
            return

        logging.info(
            "Changing UserSettings.transaction_date_format from "
            f"{self._general_date_format} to {value}"
        )
        self._general_date_format = value

    @property
    def number_format(self) -> NumberFormat:
        return self._number_format

    @number_format.setter
    def number_format(self, value: NumberFormat) -> None:
        if not isinstance(value, NumberFormat):
            raise TypeError("UserSettings.number_format must be a NumberFormat.")
        if self._number_format == value:
            return

        logging.info(
            f"Changing UserSettings.number_format from {self._number_format} to {value}"
        )
        self._number_format = value

    @property
    def exchange_rate_decimals(self) -> int:
        return self._exchange_rate_decimals

    @exchange_rate_decimals.setter
    def exchange_rate_decimals(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError("UserSettings.exchange_rate_decimals must be an integer.")
        if value < 0 or value > 18:
            raise ValueError(
                "UserSettings.exchange_rate_decimals must be between 0 and 18."
            )
        if self._exchange_rate_decimals == value:
            return

        logging.info(
            "Changing UserSettings.exchange_rate_decimals from "
            f"{self._exchange_rate_decimals} to {value}"
        )
        self._exchange_rate_decimals = value

    @property
    def amount_per_share_decimals(self) -> int:
        return self._amount_per_share_decimals

    @amount_per_share_decimals.setter
    def amount_per_share_decimals(self, value: int) -> None:
        if not isinstance(value, int):
            raise TypeError(
                "UserSettings.amount_per_share_decimals must be an integer."
            )
        if value < 0 or value > 18:
            raise ValueError(
                "UserSettings.amount_per_share_decimals must be between 0 and 18."
            )
        if self._amount_per_share_decimals == value:
            return

        logging.info(
            "Changing UserSettings.amount_per_share_decimals from "
            f"{self._amount_per_share_decimals} to {value}"
        )
        self._amount_per_share_decimals = value

    @property
    def check_for_updates_on_startup(self) -> bool:
        return self._check_for_updates_on_startup

    @check_for_updates_on_startup.setter
    def check_for_updates_on_startup(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("UserSettings.check_for_updates_on_startup must be a bool.")
        if self._check_for_updates_on_startup == value:
            return

        logging.info(
            "Changing UserSettings.check_for_updates_on_startup from "
            f"{self._check_for_updates_on_startup} to {value}"
        )
        self._check_for_updates_on_startup = value

    @property
    def transaction_table_column_order(self) -> tuple[TransactionTableColumn, ...]:
        return self._transaction_table_column_order

    @transaction_table_column_order.setter
    def transaction_table_column_order(
        self, columns: Sequence[TransactionTableColumn]
    ) -> None:
        if not isinstance(columns, Sequence):
            raise TypeError(
                "UserSettings.transaction_table_column_order must be a Sequence."
            )
        if not all(isinstance(column, TransactionTableColumn) for column in columns):
            raise TypeError(
                "UserSettings.transaction_table_column_order must be a Sequence "
                "of TransactionTableColumn."
            )
        if len(columns) != 0 and len(columns) != len(TransactionTableColumn):
            raise ValueError(
                "UserSettings.transaction_table_column_order must be a Sequence of "
                f"exactly {len(TransactionTableColumn)} TransactionTableColumns "
                "or empty."
            )
        _column_set = set(columns)
        if len(_column_set) != len(columns):
            raise ValueError(
                "UserSettings.transaction_table_column_order must not contain "
                "duplicate values."
            )
        if self._transaction_table_column_order == tuple(columns):
            return

        logging.info(
            "Changing UserSettings.transaction_table_column_order from "
            f"{self._transaction_table_column_order} to {columns}"
        )
        self._transaction_table_column_order = tuple(columns)

    def __repr__(self) -> str:
        return "UserSettings"

    def serialize(self) -> dict[str, Any]:
        backup_paths = [str(path) for path in self._backup_paths]
        transaction_table_column_names = [
            column.name for column in self._transaction_table_column_order
        ]
        return {
            "datatype": "UserSettings",
            "time_zone": self._time_zone.key,
            "logs_max_size_bytes": self._logs_max_size_bytes,
            "backups_max_size_bytes": self._backups_max_size_bytes,
            "backup_paths": backup_paths,
            "general_date_format": self._general_date_format,
            "transaction_date_format": self._transaction_date_format,
            "number_format": self._number_format.name,
            "exchange_rate_decimals": self._exchange_rate_decimals,
            "amount_per_share_decimals": self._amount_per_share_decimals,
            "check_for_updates_on_startup": self._check_for_updates_on_startup,
            "transaction_table_column_order": transaction_table_column_names,
        }

    @staticmethod
    def deserialize(data: dict[str, Any]) -> "UserSettings":
        time_zone = ZoneInfo(data["time_zone"])
        logs_max_size_bytes: int = data["logs_max_size_bytes"]
        backups_max_size_bytes: int = data["backups_max_size_bytes"]

        backup_path_strings: list[str] = data["backup_paths"]
        backup_paths = [Path(string) for string in backup_path_strings]

        general_date_format: str = data.get("general_date_format", "%d.%m.%Y")
        transaction_date_format: str = data.get("transaction_date_format", "%d.%m.%Y")

        if "number_format" in data:
            number_format = NumberFormat[data["number_format"]]
        else:
            number_format = NumberFormat.SEP_NONE_DECIMAL_POINT

        exchange_rate_decimals: int = data.get("exchange_rate_decimals", 9)
        amount_per_share_decimals: int = data.get("amount_per_share_decimals", 9)

        check_for_updates_on_startup: bool = data.get(
            "check_for_updates_on_startup", True
        )

        transaction_table_column_order: tuple[TransactionTableColumn, ...] = tuple(
            TransactionTableColumn[name]
            for name in data.get("transaction_table_column_order", ())
        )

        obj = UserSettings()
        obj._time_zone = time_zone
        obj._logs_max_size_bytes = logs_max_size_bytes
        obj._backups_max_size_bytes = backups_max_size_bytes
        obj._backup_paths = backup_paths
        obj._general_date_format = general_date_format
        obj._transaction_date_format = transaction_date_format
        obj._number_format = number_format
        obj._exchange_rate_decimals = exchange_rate_decimals
        obj._amount_per_share_decimals = amount_per_share_decimals
        obj._check_for_updates_on_startup = check_for_updates_on_startup
        obj._transaction_table_column_order = transaction_table_column_order

        return obj


def _get_number_format_for_locale() -> NumberFormat:
    # relies on locale.setlocale(locale.LC_ALL, "") being called first in main.py
    point = locale.localeconv().get("decimal_point")
    sep = locale.localeconv().get("thousands_sep")

    format_ = None
    if sep in (" ", "\xa0"):
        if point == ".":
            format_ = NumberFormat.SEP_SPACE_DECIMAL_POINT
        if point == ",":
            format_ = NumberFormat.SEP_SPACE_DECIMAL_COMMA
    if sep == "," and point == ".":
        format_ = NumberFormat.SEP_COMMA_DECIMAL_POINT
    if sep == "." and point == ",":
        format_ = NumberFormat.SEP_POINT_DECIMAL_COMMA
    if sep == "" and point == ".":
        format_ = NumberFormat.SEP_NONE_DECIMAL_POINT

    if format_ is None:
        # default to decimal point, no separator ("C" locale)
        return NumberFormat.SEP_NONE_DECIMAL_POINT

    return format_


def get_locale_code_for_number_format(number_format: NumberFormat) -> str:
    match number_format:
        case NumberFormat.SEP_SPACE_DECIMAL_POINT:
            return "xh_ZA"
        case NumberFormat.SEP_SPACE_DECIMAL_COMMA:
            return "cs_CZ"
        case NumberFormat.SEP_COMMA_DECIMAL_POINT:
            return "en_US"
        case NumberFormat.SEP_POINT_DECIMAL_COMMA:
            return "nl_NL"
        case NumberFormat.SEP_NONE_DECIMAL_POINT:
            return "C"
        case _:
            raise ValueError(f"Unknown number format: {number_format}")
