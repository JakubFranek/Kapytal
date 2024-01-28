from collections.abc import Sequence
from functools import partial
from numbers import Real

from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PyQt6.QtCore import QPointF, Qt, pyqtSignal
from PyQt6.QtGui import QCursor, QFont, QMouseEvent, QPainter
from PyQt6.QtWidgets import QWidget
from src.utilities.formatting import format_percentage, format_real
from src.views import colors
from src.views.widgets.charts.general_chart_callout import GeneralChartCallout

SMALL_SLICE_LABEL = "(others)"
SMALL_SLICE_RATIO = 0.012


class PieChartView(QChartView):
    signal_mouse_move = pyqtSignal()
    signal_slice_clicked = pyqtSignal(str)

    def __init__(self, parent: QWidget | None, *, clickable_slices: bool) -> None:
        super().__init__(parent)
        self._clickable_slices = clickable_slices

        self._font = QFont()
        self._font.setPointSize(10)

    def load_data(
        self,
        data: Sequence[tuple[Real, str]],
        places: int,
        currency_code: str,
        color: colors.ColorRanges,
    ) -> None:
        self._decimals = places
        self._currency_code = currency_code

        _data = [(float(d[0]), d[1]) for d in data]

        total = sum(d[0] for d in _data)
        others = 0
        data_ = []
        for size, label in sorted(_data, key=lambda x: x[0], reverse=True):
            if size > total * SMALL_SLICE_RATIO:
                data_.append((size, label))
            else:
                others += size
        data_.append((others, SMALL_SLICE_LABEL))

        colors_ = colors.get_color_range(color, len(data_))

        series = QPieSeries()
        series.setPieSize(0.6)
        for data_point in data_:
            _slice = series.append(data_point[1], data_point[0])
            _slice.setLabelVisible(data_point[0] > total * SMALL_SLICE_RATIO)
            _slice.setLabelPosition(QPieSlice.LabelPosition.LabelOutside)
            _slice.setLabelFont(self._font)
            _slice.setColor(colors_[data_.index(data_point)])

            _slice.hovered[bool].connect(partial(self.slice_hovered, slice_=_slice))
            _slice.clicked.connect(partial(self.slice_clicked, slice_=_slice))

        chart = QChart()
        chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        chart.legend().setVisible(False)
        chart.addSeries(series)

        self.setChart(chart)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._callout = GeneralChartCallout(chart, QPointF(0, 0))
        self.signal_mouse_move.connect(self.update_callout)

    def slice_hovered(self, state: bool, slice_: QPieSlice) -> None:  # noqa: FBT001
        label = slice_.label()
        value = slice_.value()
        percentage = 100 * slice_.percentage()

        callout_text = (
            f"{label}\n"
            f"{format_real(value, self._decimals)} {self._currency_code}\n"
            f"{format_percentage(percentage)} of Total"
        )
        self._update_callout(callout_text)
        if state:
            self._callout.show()
            if self._clickable_slices and label != SMALL_SLICE_LABEL:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self._callout.hide()
            if self._clickable_slices:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def update_callout(self) -> None:
        if self._callout.isVisible():
            self._update_callout(self._callout.text)

    def _update_callout(self, text: str) -> None:
        cursor_pos = QCursor.pos()
        view_pos = self.mapFromGlobal(cursor_pos)
        scene_pos = self.mapToScene(view_pos)

        self._callout.set_text(text)
        self._callout.set_anchor(scene_pos)
        self._callout.setZValue(11)
        self._callout.update_geometry()

    def slice_clicked(self, slice_: QPieSlice) -> None:
        if not self._clickable_slices:
            return
        self.signal_slice_clicked.emit(slice_.label())

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        self.signal_mouse_move.emit()
        return super().mouseMoveEvent(event)
