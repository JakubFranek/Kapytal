import math
import numbers
from collections.abc import Sequence
from datetime import date

from PyQt6.QtCharts import (
    QChart,
    QChartView,
    QDateTimeAxis,
    QLineSeries,
    QValueAxis,
)
from PyQt6.QtCore import QDateTime, QPointF, Qt
from PyQt6.QtGui import (
    QMouseEvent,
    QPainter,
    QWheelEvent,
)
from PyQt6.QtWidgets import (
    QGraphicsScene,
    QWidget,
)
from src.models.user_settings import user_settings

from line_callout import LineCallout


class DateLineChartView(QChartView):
    def __init__(self, parent: QWidget = None) -> None:
        super().__init__(parent)
        self.setScene(QGraphicsScene(self))

        self._chart = QChart()
        self._chart.setMinimumSize(640, 480)
        self._chart.setTitle("Chart")
        self._chart.legend().hide()

        self._axis_x = QDateTimeAxis()
        self._axis_x.setFormat(
            user_settings.settings.general_date_format.replace("%", "")
        )
        self._chart.addAxis(self._axis_x, Qt.AlignmentFlag.AlignBottom)

        self._axis_y = QValueAxis()
        self._chart.addAxis(self._axis_y, Qt.AlignmentFlag.AlignLeft)
        self._chart.setAcceptHoverEvents(True)

        self._callout = LineCallout(self._chart)

        self.setChart(self._chart)
        self.scene().addItem(self._chart)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMouseTracking(True)
        self.setRubberBand(QChartView.RubberBand.RectangleRubberBand)

    def load_data(  # noqa: PLR0913
        self,
        x: Sequence[date],
        y: Sequence[numbers.Real],
        title: str = "",
        ylabel: str = "",
        xlabel: str = "",
    ) -> None:
        self._chart.removeAllSeries()
        self._chart.setTitle(title)
        self._axis_x.setTitleText(xlabel)
        self._axis_y.setTitleText(ylabel)

        self._series = QLineSeries()
        self._series.setMarkerSize(5)
        self._series.setPointsVisible(True)

        for i in range(len(x)):
            dt = QDateTime(x[i])
            self._series.append(dt.toMSecsSinceEpoch(), float(y[i]))
        self._chart.addSeries(self._series)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self._chart.mapToValue(QPointF(event.position().toPoint()))
        x = pos.x()
        y = pos.y()

        point = self._find_nearest_point(x, y)
        if point is not None:
            self._callout.set_text(f"X: {point.x():.2f} \nY: {point.y():.2f} ")
            self._callout.set_anchor(point)
            self._callout.setZValue(11)
            self._callout.update_geometry()
            self._callout.show()
        else:
            self._callout.hide()

        super().mouseMoveEvent(self, event)

    def wheelEvent(self, event: QWheelEvent | None) -> None:
        if event.angleDelta().y() > 0:
            self._chart.zoomIn()
        else:
            self._chart.zoomOut()
        return super().wheelEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self.chart().zoomReset()
            return None
        return super().mouseReleaseEvent(event)

    def _find_nearest_point(self, x: float, y: float) -> QPointF | None:
        x_axis: QValueAxis = self._chart.axes(Qt.Orientation.Horizontal)[0]
        x_range = x_axis.max() - x_axis.min()
        x_dist_max = x_range / 50

        y_axis: QValueAxis = self._chart.axes(Qt.Orientation.Vertical)[0]
        y_range = y_axis.max() - y_axis.min()
        y_dist_max = y_range / 50

        close_point = None
        min_distance_so_far = float("inf")
        for point in self._series.points():
            distance = math.sqrt((point.x() - x) ** 2 + (point.y() - y) ** 2)
            x_distance = abs(point.x() - x)
            y_distance = abs(point.y() - y)
            if (
                distance < min_distance_so_far
                and x_distance < x_dist_max
                and y_distance < y_dist_max
            ):
                min_distance_so_far = distance
                close_point = point

        return close_point if close_point is not None else None
