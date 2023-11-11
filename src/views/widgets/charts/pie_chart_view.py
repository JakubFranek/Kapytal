from collections.abc import Sequence
from functools import partial
from numbers import Real

from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PyQt6.QtCore import QPointF, pyqtSignal
from PyQt6.QtGui import QCursor, QFont, QMouseEvent, QPainter
from PyQt6.QtWidgets import QWidget
from src.views import colors
from src.views.widgets.charts.general_chart_callout import GeneralChartCallout


class PieChartView(QChartView):
    signal_mouse_move = pyqtSignal()

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self._font = QFont()
        self._font.setPointSize(10)

    def load_data(
        self,
        data: Sequence[tuple[Real, str]],
        places: int,
        currency_code: str,
        color: colors.ColorRanges,
    ) -> None:
        self._places = places
        self._currency_code = currency_code

        _data = [(float(x[0]), x[1]) for x in data]

        total = sum(x[0] for x in _data)
        others = 0
        data_ = []
        for size, label in sorted(_data, key=lambda x: x[0], reverse=True):
            if size > total * 0.012:
                data_.append((size, label))
            else:
                others += size
        data_.append((others, "(other)"))

        colors_ = colors.get_color_range(color, len(data_))

        series = QPieSeries()
        series.setPieSize(0.6)
        for data_point in data_:
            _slice = series.append(data_point[1], data_point[0])
            _slice.setLabelVisible(data_point[0] > total * 0.012)
            _slice.setLabelPosition(QPieSlice.LabelPosition.LabelOutside)
            _slice.setLabelFont(self._font)
            _slice.setColor(colors_[data_.index(data_point)])

            _slice.hovered[bool].connect(partial(self.on_hover, slice_=_slice))
            # TODO: show transactions on double click, change cursor on hover

        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        chart.legend().setVisible(False)
        chart.addSeries(series)

        self.setChart(chart)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._tooltip = GeneralChartCallout(chart, QPointF(0, 0))
        self.signal_mouse_move.connect(self.update_callout)

    def on_hover(self, state: bool, slice_: QPieSlice) -> None:  # noqa: FBT001
        label = slice_.label()
        value = slice_.value()
        percentage = 100 * slice_.percentage()

        cursor_pos = QCursor.pos()
        view_pos = self.mapFromGlobal(cursor_pos)
        scene_pos = self.mapToScene(view_pos)

        self._tooltip.set_text(
            f"{label}\n"
            f"{value:,.{self._places}f} {self._currency_code}\n"
            f"{percentage:.2f}% of Total"
        )
        self._tooltip.set_anchor(scene_pos)
        self._tooltip.setZValue(11)
        self._tooltip.update_geometry()
        if state:
            self._tooltip.show()
        else:
            self._tooltip.hide()

    def update_callout(self) -> None:
        if self._tooltip.isVisible():
            cursor_pos = QCursor.pos()
            view_pos = self.mapFromGlobal(cursor_pos)
            scene_pos = self.mapToScene(view_pos)
            self._tooltip.set_anchor(scene_pos)
            self._tooltip.update_geometry()

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        self.signal_mouse_move.emit()
        return super().mouseMoveEvent(event)
