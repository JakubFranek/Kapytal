from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor

color_scheme: Qt.ColorScheme | None = None

_blue_light_mode = QColor("blue")
_blue_dark_mode = QColor("deepskyblue")
_green_light_mode = QColor("green")
_green_dark_mode = QColor("lime")
_red_light_mode = QColor("red")
_red_dark_mode = QColor(255, 0, 191, 255)  # "shocking pink"
_gray = QColor("gray")

_tab_widget_background_dark_mode = QColor(75, 75, 75, 255)
_tab_widget_background_light_mode = QColor(252, 252, 252, 255)

_brush_blue_light_mode = QBrush(_blue_light_mode)
_brush_blue_dark_mode = QBrush(_blue_dark_mode)
_brush_green_light_mode = QBrush(_green_light_mode)
_brush_green_dark_mode = QBrush(_green_dark_mode)
_brush_red_light_mode = QBrush(_red_light_mode)
_brush_red_dark_mode = QBrush(_red_dark_mode)
_brush_gray = QBrush(_gray)


def get_blue() -> QColor:
    return _blue_dark_mode if color_scheme == Qt.ColorScheme.Dark else _blue_light_mode


def get_green() -> QColor:
    return (
        _green_dark_mode if color_scheme == Qt.ColorScheme.Dark else _green_light_mode
    )


def get_red() -> QColor:
    return _red_dark_mode if color_scheme == Qt.ColorScheme.Dark else _red_light_mode


def get_gray() -> QColor:
    return _gray


def get_tab_widget_background() -> QColor:
    if color_scheme == Qt.ColorScheme.Dark:
        return _tab_widget_background_dark_mode
    return _tab_widget_background_light_mode


def get_blue_brush() -> QBrush:
    return (
        _brush_blue_dark_mode
        if color_scheme == Qt.ColorScheme.Dark
        else _brush_blue_light_mode
    )


def get_green_brush() -> QBrush:
    return (
        _brush_green_dark_mode
        if color_scheme == Qt.ColorScheme.Dark
        else _brush_green_light_mode
    )


def get_red_brush() -> QBrush:
    return (
        _brush_red_dark_mode
        if color_scheme == Qt.ColorScheme.Dark
        else _brush_red_light_mode
    )


def get_gray_brush() -> QBrush:
    return _brush_gray
