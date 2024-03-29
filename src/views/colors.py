import math
from enum import Enum, auto

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


def get_linear_color_sequence(start: QColor, end: QColor, length: int) -> tuple[QColor]:
    # get the total difference between each color channel
    red_difference = end.red() - start.red()
    green_difference = end.green() - start.green()
    blue_difference = end.blue() - start.blue()

    # divide the difference by the number of rows
    red_delta = red_difference / (length - 1)
    green_delta = green_difference / (length - 1)
    blue_delta = blue_difference / (length - 1)

    # display the color for each row
    colors = []
    for i in range(length):
        # apply the delta to the red, green and blue channels
        interpolated_color = (
            int(start.red() + (red_delta * i)),
            int(start.green() + (green_delta * i)),
            int(start.blue() + (blue_delta * i)),
        )
        colors.append(QColor(*interpolated_color))

    return tuple(colors)


def get_bezier_color_sequence(
    start: QColor, end: QColor, control: QColor, length: int
) -> tuple[QColor]:
    if length > 1:
        step = 1 / (length - 1)
    else:
        return (control,)

    start_red = start.red()
    start_green = start.green()
    start_blue = start.blue()

    control_red = control.red()
    control_green = control.green()
    control_blue = control.blue()

    end_red = end.red()
    end_green = end.green()
    end_blue = end.blue()

    colors = []
    for i in range(length):
        x = i * step
        red = int(
            (1 - x**2) * start_red + 2 * (1 - x) * x * control_red + x**2 * end_red
        )
        green = int(
            (1 - x**2) * start_green
            + 2 * (1 - x) * x * control_green
            + x**2 * end_green
        )
        blue = int(
            (1 - x**2) * start_blue
            + 2 * (1 - x) * x * control_blue
            + x**2 * end_blue
        )
        colors.append(QColor(red, green, blue))

    return tuple(colors)


class ColorRanges(Enum):
    GREEN = auto()
    RED = auto()


def get_color_range(color: ColorRanges, steps: int) -> tuple[QColor]:
    match color:
        case ColorRanges.GREEN:
            return get_bezier_color_sequence(
                QColor(42, 84, 52),
                QColor(193, 232, 202),
                QColor(85, 168, 104),
                steps,
            )
        case ColorRanges.RED:
            return get_bezier_color_sequence(
                QColor(103, 34, 37),
                QColor(237, 202, 203),
                QColor(196, 78, 82),
                steps,
            )
        case _:
            raise ValueError("Invalid color range.")


def get_deep_tab10_palette(*, reverse: bool = False) -> tuple[QColor]:
    """Returns the deep version of the tab10 palette, as used in seaborn."""
    palette = (
        QColor(76, 114, 176),
        QColor(221, 132, 82),
        QColor(85, 168, 104),
        QColor(196, 78, 82),
        QColor(129, 114, 179),
        QColor(147, 120, 96),
        QColor(218, 139, 195),
        QColor(140, 140, 140),
        QColor(204, 185, 116),
        QColor(100, 181, 205),
    )
    return palette[::-1] if reverse else palette


_LIGHTNESS_DENOMINATOR = 255 * (3**0.5)
_LIGHTNESS_THRESHOLD = 0.38  # empirical value


def get_font_color_for_background(background: QColor) -> QColor:
    """Returns white or black font color based on 'weighted Euclidean norm'
    of the RGB vector."""

    lightness = (
        math.sqrt(
            0.299 * (background.red() ** 2)
            + 0.587 * (background.green() ** 2)
            + 0.111 * (background.blue() ** 2)
        )
        / _LIGHTNESS_DENOMINATOR
    )
    return QColor("white") if lightness < _LIGHTNESS_THRESHOLD else QColor("black")
