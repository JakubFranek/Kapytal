import locale
from datetime import datetime
from decimal import Decimal

from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QDateTimeEdit, QSpinBox, QTableView
from src.models.user_settings import user_settings


def calculate_table_width(table: QTableView) -> int:
    return table.horizontalHeader().length() + table.verticalHeader().width()


def get_spinbox_value_as_decimal(spinbox: QSpinBox) -> Decimal:
    text = spinbox.cleanText()
    text_delocalized = locale.delocalize(text)
    return Decimal(text_delocalized)


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
    except Exception as exception:
        raise ValueError("Invalid datetime format specified.") from exception
    return datetime_format


def overflowing_keyPressEvent(self: QDateTimeEdit, event: QKeyEvent) -> None:
    """Assign this method to a QDateTimeEdit to enable natural date overflow."""

    key = event.key()
    steps = 0
    if key == Qt.Key.Key_Up:
        steps = 1
    elif key == Qt.Key.Key_Down:
        steps = -1

    if steps != 0:
        section = self.currentSection()
        dt = self.dateTime()
        if section == QDateTimeEdit.Section.DaySection:
            self.setDateTime(dt.addDays(steps))
            return
        if section == QDateTimeEdit.Section.MonthSection:
            self.setDateTime(dt.addMonths(steps))
            return
        if section == QDateTimeEdit.Section.YearSection:
            self.setDateTime(dt.addYears(steps))
            return

    super(QDateTimeEdit, self).keyPressEvent(event)
