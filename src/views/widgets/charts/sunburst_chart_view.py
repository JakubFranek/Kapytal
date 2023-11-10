from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial
from numbers import Real
from typing import Self

from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PyQt6.QtCore import QPointF, pyqtSignal
from PyQt6.QtGui import QColor, QCursor, QFont, QMouseEvent, QPainter
from PyQt6.QtWidgets import QWidget
from src.views import colors
from src.views.widgets.charts.general_chart_callout import GeneralChartCallout


@dataclass
class SunburstNode:
    # TODO: add full path property for callout
    label: str
    value: Real
    children: list[Self]

    def clear_label(self) -> None:
        self.label = ""
        for child in self.children:
            child.clear_label()

    def depth(self) -> int:
        return 1 + max((child.depth() for child in self.children), default=0)


class SunburstChartView(QChartView):
    signal_mouse_move = pyqtSignal()

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.min_size = 0
        self.max_size = 1

        self.series_dict: dict[int, QPieSeries] = {}

        self.callout = GeneralChartCallout(None, QPointF(0, 0))
        self.scene().addItem(self.callout)

        self.signal_mouse_move.connect(self.update_callout)

        self.font = QFont()
        self.font.setPointSize(10)

    def load_data(self, data: Sequence[SunburstNode]) -> None:
        self._chart = QChart()
        self._chart.legend().setVisible(False)
        self._chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        self.setChart(self._chart)
        self.series_dict = {}

        self.total_levels = max(node.depth() for node in data)

        for node in data:
            self.create_series(node, parent_slice=None, level=0, index=0)

        levels = len(self.series_dict)
        for level, series in self.series_dict.items():
            size = (self.max_size - self.min_size) / levels
            series.setHoleSize(self.min_size + size * level)
            # TODO: make central pie narrower to have more space for labels?
            series.setPieSize(self.min_size + size * (level + 1))
            self._chart.addSeries(series)

    def create_series(  # noqa: PLR0913
        self,
        node: SunburstNode,
        parent_slice: QPieSlice | None,
        level: int,
        index: int,
        *,
        empty: bool = False,
    ) -> None:
        slice_ = QPieSlice(node.label, node.value)
        if empty:
            slice_.setLabelVisible(False)
            slice_.setColor(QColor("white"))
        elif level == 0:
            slice_.setColor(QColor("gray"))
            self.total = node.value
        elif level == 1:
            slice_.setColor(colors.get_deep_tab10_palette()[index % 10])
        elif parent_slice is not None:
            slice_.setColor(parent_slice.color().lighter(120))

        if not empty:
            if node.value > self.total * 0.012 and len(node.label) < 20:
                slice_.setLabelVisible(True)
                slice_.setLabelFont(self.font)
                if level > 2:  # TODO: add smart way to decide font color
                    slice_.setLabelColor(QColor("black"))
                else:
                    slice_.setLabelColor(QColor("white"))
                slice_.setLabelPosition(QPieSlice.LabelPosition.LabelInsideNormal)
            slice_.hovered[bool].connect(partial(self.show_callout, slice_=slice_))
            # TODO: show transactions on double click, change cursor on hover

        if level not in self.series_dict:
            self.series_dict[level] = QPieSeries()
        self.series_dict[level].append(slice_)

        for index, child in enumerate(node.children):
            self.create_series(child, slice_, level + 1, index)

        sum_children = sum(child.value for child in node.children)
        if len(node.children) > 0 and sum_children < node.value:
            self.create_series(
                SunburstNode(label="", value=node.value - sum_children, children=[]),
                parent_slice=slice_,
                level=level + 1,
                index=len(node.children),
                empty=True,
            )

        if level < self.total_levels - 1 and len(node.children) == 0:
            self.create_series(
                SunburstNode(label="", value=node.value, children=[]),
                parent_slice=slice_,
                level=level + 1,
                index=len(node.children),
                empty=True,
            )

    def show_callout(self, enter: bool, slice_: QPieSlice) -> None:  # noqa: FBT001
        label = slice_.label()
        value = slice_.value()

        cursor_pos = QCursor.pos()
        view_pos = self.mapFromGlobal(cursor_pos)
        scene_pos = self.mapToScene(view_pos)

        # TODO: add unit, decimal places rounding
        self.callout.set_text(f"{label}\n{value:,}")
        self.callout.set_anchor(scene_pos)
        self.callout.setZValue(11)
        self.callout.update_geometry()
        if enter:
            self.callout.show()
        else:
            self.callout.hide()

    def update_callout(self) -> None:
        if self.callout.isVisible():
            cursor_pos = QCursor.pos()
            view_pos = self.mapFromGlobal(cursor_pos)
            scene_pos = self.mapToScene(view_pos)
            self.callout.set_anchor(scene_pos)
            self.callout.update_geometry()

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        self.signal_mouse_move.emit()
        return super().mouseMoveEvent(event)
