from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor

color_scheme: Qt.ColorScheme | None = None

_blue_light_mode = QBrush(QColor("blue"))
_blue_dark_mode = QBrush(QColor("deepskyblue"))
_green_light_mode = QBrush(QColor("green"))
_green_dark_mode = QBrush(QColor("lime"))
_red_light_mode = QBrush(QColor("red"))
_red_dark_mode = QBrush(QColor("deeppink"))


def get_blue_brush() -> QBrush:
    return _blue_dark_mode if color_scheme == Qt.ColorScheme.Dark else _blue_light_mode


def get_green_brush() -> QBrush:
    return (
        _green_dark_mode if color_scheme == Qt.ColorScheme.Dark else _green_light_mode
    )


def get_red_brush() -> QBrush:
    return _red_dark_mode if color_scheme == Qt.ColorScheme.Dark else _red_light_mode
