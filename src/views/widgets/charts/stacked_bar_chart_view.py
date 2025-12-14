from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial

from PyQt6.QtCharts import (
    QBarCategoryAxis,
    QBarSet,
    QChart,
    QChartView,
    QStackedBarSeries,
    QValueAxis,
)
from PyQt6.QtCore import QMargins, QPointF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QCursor, QFont, QMouseEvent, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsScene, QWidget
from src.models.model_objects.currency_objects import CashAmount
from src.utilities.formatting import format_real
from src.views import colors
from src.views.widgets.charts.general_chart_callout import GeneralChartCallout


@dataclass
class DataSeries:
    name: str
    values: list[CashAmount]


class StackedBarChartView(QChartView):
    signal_mouse_move = pyqtSignal()
    signal_bar_clicked = pyqtSignal(str, str)

    def __init__(
        self, parent: QWidget | None, *, background_color: QColor | None = None
    ) -> None:
        super().__init__(parent)

        if background_color is not None:
            self.setBackgroundBrush(background_color)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMouseTracking(True)

        self._currency_code = ""
        self._decimals = 0

        self._font = QFont()
        self._font.setPointSize(10)

        self._font_bold = QFont()
        self._font_bold.setPointSize(10)
        self._font_bold.setBold(True)

    def load_data(
        self, data: Sequence[DataSeries], period_names: Sequence[str]
    ) -> None:
        try:
            self._currency_code = data[0].values[0].currency.code
            self._decimals = data[0].values[0].currency.decimals
        except IndexError:
            self._currency_code = ""
            self._decimals = 0

        bar_sets: list[QBarSet] = []
        for index, series in enumerate(data):
            bar_set = QBarSet(series.name)
            bar_set.setColor(colors.get_deep_tab10_palette()[index % 10])
            bar_set.setPen(QPen(Qt.PenStyle.NoPen))
            bar_set.append([float(value.value_normalized) for value in series.values])
            bar_sets.append(bar_set)

        series = QStackedBarSeries()
        for bar_set in bar_sets:
            series.append(bar_set)
            bar_set.hovered[bool, int].connect(partial(self.on_hover, bar_set=bar_set))
            bar_set.clicked[int].connect(partial(self._bar_clicked, bar_set=bar_set))

        self._chart = QChart()
        self._chart.setMargins(QMargins(5, 5, 5, 5))
        self._chart.legend().setVisible(True)
        self._chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self._chart.legend().setFont(self._font)
        self._chart.addSeries(series)
        self._chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.axis_x = QBarCategoryAxis()
        self.axis_x.setLabelsFont(self._font)
        self.axis_x.setGridLineVisible(False)
        self.axis_x.append(period_names)
        self._chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setTitleText(self._currency_code)
        self.axis_y.setTitleFont(self._font_bold)
        self.axis_y.setLabelsFont(self._font)
        self._chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(self.axis_y)

        self.signal_mouse_move.connect(self.update_callout)

        self.setScene(QGraphicsScene(self))
        self.setChart(self._chart)
        self.scene().addItem(self._chart)

        self._tooltip = GeneralChartCallout(self._chart, QPointF(0, 0))

        self.axis_y.applyNiceNumbers()

    def on_hover(
        self,
        state: bool,  # noqa: FBT001
        index: int,
        bar_set: QBarSet,
    ) -> None:
        label = bar_set.label()
        value = bar_set.at(index)

        self._tooltip.set_text(
            f"{label}\n{format_real(value, self._decimals)} {self._currency_code}"
        )

        self._update_callout()
        if state:
            self._tooltip.show()
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self._tooltip.hide()
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def update_callout(self) -> None:
        if self._tooltip.isVisible():
            self._update_callout()

    def _update_callout(self) -> None:
        cursor_pos = QCursor.pos()
        view_pos = self.mapFromGlobal(cursor_pos)
        scene_pos = self.mapToScene(view_pos)

        y_threshold = self.rect().topLeft().y()
        top = scene_pos.y() > y_threshold + 80

        x_threshold = self.rect().topLeft().x()
        left = scene_pos.x() > x_threshold + 120

        self._tooltip.set_text(self._tooltip.text, left=left, top=top)
        self._tooltip.set_anchor(scene_pos)
        self._tooltip.setZValue(11)
        self._tooltip.update_geometry()

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        self.signal_mouse_move.emit()
        return super().mouseMoveEvent(event)

    def _bar_clicked(self, index: int, bar_set: QBarSet) -> None:
        period = self.axis_x.categories()[index]
        label = bar_set.label()
        self.signal_bar_clicked.emit(period, label)
