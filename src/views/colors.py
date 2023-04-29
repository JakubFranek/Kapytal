from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor

color_scheme: Qt.ColorScheme | None = None


def get_blue_brush() -> QBrush:
    color = (
        QColor("deepskyblue") if color_scheme == Qt.ColorScheme.Dark else QColor("blue")
    )
    return QBrush(color)


def get_green_brush() -> QBrush:
    color = QColor("lime") if color_scheme == Qt.ColorScheme.Dark else QColor("green")
    return QBrush(color)


def get_red_brush() -> QBrush:
    color = (
        QColor("orangered") if color_scheme == Qt.ColorScheme.Dark else QColor("red")
    )
    return QBrush(color)
