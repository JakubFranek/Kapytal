from datetime import datetime

from PyQt6.QtCore import QDateTime
from PyQt6.QtWidgets import QTableView
from src.models.user_settings import user_settings


def calculate_table_width(table: QTableView) -> int:
    return table.horizontalHeader().length() + table.verticalHeader().width()


def convert_datetime_format_to_qt(datetime_format: str) -> str:
    """Converts Python datetime.strftime format string
    to a QDateTimeEdit format string."""

    datetime_format = datetime_format.replace("%Y", "yyyy")
    datetime_format = datetime_format.replace("%y", "yy")
    datetime_format = datetime_format.replace("%b", "MMM")
    datetime_format = datetime_format.replace("%B", "MMMM")
    datetime_format = datetime_format.replace("%m", "MM")
    datetime_format = datetime_format.replace("%d", "dd")
    datetime_format = datetime_format.replace("%H", "hh")
    datetime_format = datetime_format.replace("%M", "mm")
    datetime_format = datetime_format.replace("%S", "ss")
    datetime_format = datetime_format.replace("%p", "ap")

    now = datetime.now(user_settings.settings.time_zone)
    now_qt = QDateTime(now)
    try:
        now_qt.toString(datetime_format)
    except Exception as exception:  # noqa: BLE001
        raise ValueError("Invalid datetime format specified.") from exception
    return datetime_format
