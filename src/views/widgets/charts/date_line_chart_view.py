import math
import numbers
from collections.abc import Sequence
from datetime import date, datetime

from PyQt6.QtCharts import (
    QChart,
    QChartView,
    QDateTimeAxis,
    QLineSeries,
    QValueAxis,
)
from PyQt6.QtCore import QDateTime, QMargins, QPointF, Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QMouseEvent,
    QPainter,
    QWheelEvent,
)
from PyQt6.QtWidgets import (
    QGraphicsScene,
    QWidget,
)
from src.models.user_settings import user_settings
from src.utilities.formatting import format_real
from src.views.utilities.helper_functions import convert_datetime_format_to_qt
from src.views.widgets.charts.date_line_chart_callout import DateLineChartCallout


class DateLineChartView(QChartView):
    def __init__(
        self, parent: QWidget | None = None, background_color: QColor | None = None
    ) -> None:
        super().__init__(parent)

        if background_color is not None:
            self.setBackgroundBrush(background_color)

        self._font = QFont()
        self._font.setPointSize(10)

        self._font_bold = QFont()
        self._font_bold.setPointSize(12)
        self._font_bold.setBold(True)

        self._font_bold_small = QFont()
        self._font_bold_small.setPointSize(10)
        self._font_bold_small.setBold(True)

        self._chart = QChart()
        self._chart.setMinimumSize(200, 200)
        self._chart.setTitle("Chart")
        self._chart.legend().hide()
        self._chart.setAcceptHoverEvents(True)
        self._chart.setMargins(QMargins(5, 5, 5, 5))
        self._chart.setTitleFont(self._font_bold)

        self._callout = DateLineChartCallout(self._chart)

        self.setScene(QGraphicsScene(self))
        self.setChart(self._chart)
        self.scene().addItem(self._chart)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMouseTracking(True)
        self.setRubberBand(QChartView.RubberBand.RectangleRubberBand)

    def load_data(
        self,
        x: Sequence[date],
        y: Sequence[numbers.Real],
        title: str = "",
        y_label: str = "",
        x_label: str = "",
        y_unit: str = "",
        y_decimals: int = 2,
    ) -> None:
        self._chart.removeAllSeries()
        if hasattr(self, "_axis_x"):
            self._chart.removeAxis(self._axis_x)
        if hasattr(self, "_axis_y"):
            self._chart.removeAxis(self._axis_y)
        self._chart.setTitle(title)

        self._y_unit = " " + y_unit if y_unit else ""
        self._y_decimals = y_decimals

        self._series = QLineSeries()
        self._series.setMarkerSize(3)
        self._series.setPointsVisible(True)

        constant_y = False
        for i in range(len(x)):
            dt = datetime.combine(x[i], datetime.min.time())
            qdt = QDateTime(dt)
            self._series.append(qdt.toMSecsSinceEpoch(), float(y[i]))

        if len(x) == 1:
            d = datetime.now(tz=user_settings.settings.time_zone).date()
            dt = datetime.combine(d, datetime.min.time())
            qdt = QDateTime(dt)
            self._series.append(qdt.toMSecsSinceEpoch(), float(y[0]))
            constant_y = True

        self._chart.addSeries(self._series)

        self._axis_x = QDateTimeAxis()
        self._axis_x.setTitleText(x_label)
        self._axis_x.setTitleFont(self._font_bold_small)
        self._axis_x.setLabelsFont(self._font)
        self._axis_x.setTickCount(6)
        self._axis_x.setFormat(
            convert_datetime_format_to_qt(user_settings.settings.general_date_format)
        )
        self._chart.addAxis(self._axis_x, Qt.AlignmentFlag.AlignBottom)
        self._series.attachAxis(self._axis_x)

        self._axis_y = QValueAxis()
        self._axis_y.setTitleText(y_label)
        self._axis_y.setTitleFont(self._font_bold_small)
        self._axis_y.setTickType(QValueAxis.TickType.TicksFixed)
        self._axis_y.setLabelsFont(self._font)
        self._chart.addAxis(self._axis_y, Qt.AlignmentFlag.AlignLeft)
        self._series.attachAxis(self._axis_y)

        if constant_y:
            self._axis_y.setRange(
                round(float(y[0]) - 0.1 * float(y[0])),
                round(float(y[0]) + 0.1 * float(y[0])),
            )
        self._axis_y.applyNiceNumbers()

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        pos = self._chart.mapToValue(QPointF(event.position().toPoint()))
        x = pos.x()
        y = pos.y()

        point = self._find_nearest_point(x, y)
        if point is not None:
            x_dt = QDateTime.fromMSecsSinceEpoch(int(point.x()))
            self._callout.set_anchor(point)
            dt_format_qt = convert_datetime_format_to_qt(
                user_settings.settings.general_date_format
            )
            self._callout.set_text(
                f"X: {x_dt.toString(dt_format_qt)}\n"
                f"Y: {format_real(point.y(), self._y_decimals)}" + self._y_unit
            )
            self._callout.setZValue(11)
            self._callout.update_geometry()
            self._callout.show()
        else:
            self._callout.hide()

        super().mouseMoveEvent(event)

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        if event.angleDelta().y() > 0:
            self._chart.zoomIn()
        else:
            self._chart.zoomOut()
        self._callout.hide()
        return super().wheelEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self.chart().zoomReset()
            self._callout.hide()
            return
        self._callout.hide()
        super().mouseReleaseEvent(event)

    def _find_nearest_point(self, x: float, y: float) -> QPointF | None:
        horizontal_axes = self._chart.axes(Qt.Orientation.Horizontal)
        if len(horizontal_axes) == 0:
            return None
        x_axis: QDateTimeAxis = horizontal_axes[0]
        x_range = x_axis.max().toMSecsSinceEpoch() - x_axis.min().toMSecsSinceEpoch()
        x_dist_max = x_range / 50

        y_axis: QValueAxis = self._chart.axes(Qt.Orientation.Vertical)[0]
        y_range = y_axis.max() - y_axis.min()
        y_dist_max = y_range / 50

        closest_point = None
        closest_distance = float("inf")
        for point in self._series.points():
            distance = math.sqrt((point.x() - x) ** 2 + (point.y() - y) ** 2)
            x_distance = abs(point.x() - x)
            y_distance = abs(point.y() - y)
            if (
                distance < closest_distance
                and x_distance < x_dist_max
                and y_distance < y_dist_max
            ):
                closest_distance = distance
                closest_point = point

        return closest_point if closest_point is not None else None
