import locale
from datetime import datetime
from decimal import Decimal

from PyQt6.QtCore import QDateTime, Qt
from PyQt6.QtGui import QKeyEvent, QWheelEvent
from PyQt6.QtWidgets import QDateTimeEdit, QSpinBox, QTableView
from src.models.user_settings import user_settings

_qdatetimeedit_original_keyPressEvent = QDateTimeEdit.keyPressEvent
_qdatetimeedit_original_wheelEvent = QDateTimeEdit.wheelEvent

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
    key = event.key()
    steps = 1 if key == Qt.Key.Key_Up else -1 if key == Qt.Key.Key_Down else 0
    if steps and _overflow_step(self, steps):
        return
    return _qdatetimeedit_original_keyPressEvent(self, event)


def overflowing_wheelEvent(self: QDateTimeEdit, event: QWheelEvent) -> None:
    delta = event.angleDelta().y()
    steps = 1 if delta > 0 else -1 if delta < 0 else 0
    if steps and _overflow_step(self, steps):
        return
    return _qdatetimeedit_original_wheelEvent(self, event)


def _overflow_step(self: QDateTimeEdit, steps: int) -> bool:
    """Apply overflow step; return True if handled."""
    section = self.currentSection()
    dt = self.dateTime()
    if section == QDateTimeEdit.Section.DaySection:
        self.setDateTime(dt.addDays(steps))
        return True
    if section == QDateTimeEdit.Section.MonthSection:
        self.setDateTime(dt.addMonths(steps))
        return True
    if section == QDateTimeEdit.Section.YearSection:
        self.setDateTime(dt.addYears(steps))
        return True
    return False
