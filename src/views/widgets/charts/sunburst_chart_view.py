from collections.abc import Sequence
from dataclasses import dataclass
from functools import partial
from numbers import Real
from typing import Self

from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QPieSlice
from PyQt6.QtCore import QPointF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QCursor, QFont, QMouseEvent, QPainter
from PyQt6.QtWidgets import QWidget
from src.views import colors
from src.views.widgets.charts.general_chart_callout import GeneralChartCallout


@dataclass
class SunburstNode:
    label: str
    path: str
    value: Real
    unit: str
    decimals: int
    children: list[Self]
    parent: Self | None

    def clear_label(self) -> None:
        self.label = ""
        for child in self.children:
            child.clear_label()

    def depth(self) -> int:
        return 1 + max((child.depth() for child in self.children), default=0)

    def get_root_node(self) -> Self:
        return self if self.parent is None else self.parent.get_root_node()

    def get_callout_text(self) -> str:
        text = f"{self.path}\n{self.value:,.{self.decimals}f}"
        text = text + f" {self.unit}" if self.unit else text
        for ancestor in self.get_ancestors():
            text += f"\n{100*self.value/ancestor.value:.2f}% of {ancestor.path}"

        return text

    def get_ancestors(self) -> tuple[Self, ...]:
        if self.parent is None:
            return ()
        return self.parent, *self.parent.get_ancestors()


class SunburstSlice(QPieSlice):
    def __init__(
        self,
        node: SunburstNode,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(label=node.label, value=node.value, parent=parent)
        self.node = node


class SunburstChartView(QChartView):
    signal_mouse_move = pyqtSignal()
    signal_slice_clicked = pyqtSignal(str)

    def __init__(self, parent: QWidget | None, *, clickable_slices: bool) -> None:
        super().__init__(parent)
        self._clickable_slices = clickable_slices

        self.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.min_size = 0
        self.max_size = 1

        self.series_dict: dict[int, QPieSeries] = {}

        self.callout = GeneralChartCallout(None, QPointF(0, 0))
        self.scene().addItem(self.callout)

        self.signal_mouse_move.connect(self.update_callout)

        self._font = QFont()
        self._font.setPointSize(10)

    def load_data(self, data: Sequence[SunburstNode]) -> None:
        self._chart = QChart()
        self._chart.legend().setVisible(False)
        self._chart.setAnimationOptions(QChart.AnimationOption.AllAnimations)
        self.setChart(self._chart)
        self.series_dict = {}

        self.total_levels = max(node.depth() for node in data)
        self.lighter_coefficient = int(100 + 100 / self.total_levels)

        for node in data:
            self.create_series(node, parent_slice=None, level=0, index=0)

        size = (self.max_size - self.min_size) / (self.total_levels - 0.5)
        for level, series in self.series_dict.items():
            series.setHoleSize(self.min_size + size * max(level - 0.5, 0))
            series.setPieSize(self.min_size + size * (level + 0.5))
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
        # TODO: add smart algorithm for shortening long labels
        # for example: Adam/Investments/Interactive Brokers/Securities
        #              Adam/Inv./Int.Bro./Securities
        # shorten words >4 to 3+dot, except for last word (?)
        slice_ = SunburstSlice(node)
        if empty:
            slice_.setLabelVisible(False)
            slice_.setColor(QColor("white"))
        elif level == 0:
            slice_.setColor(QColor("gray"))
            self.total = node.value
        elif level == 1:
            slice_.setColor(colors.get_deep_tab10_palette()[index % 10])
        elif parent_slice is not None:
            slice_.setColor(parent_slice.color().lighter(self.lighter_coefficient))

        if not empty:
            if node.value > self.total * 0.012 and len(node.label) < 20:
                slice_.setLabelVisible(True)
                slice_.setLabelFont(self._font)
                slice_.setLabelColor(
                    colors.get_font_color_for_background(slice_.color())
                )
                if level == 0:
                    slice_.setLabelPosition(
                        QPieSlice.LabelPosition.LabelInsideHorizontal
                    )
                else:
                    slice_.setLabelPosition(QPieSlice.LabelPosition.LabelInsideNormal)
            slice_.hovered[bool].connect(partial(self.slice_hovered, slice_=slice_))
            slice_.clicked.connect(partial(self.slice_clicked, slice_=slice_))

        if level not in self.series_dict:
            self.series_dict[level] = QPieSeries()
        self.series_dict[level].append(slice_)

        for index, child in enumerate(node.children):
            self.create_series(child, slice_, level + 1, index)

        sum_children = sum(child.value for child in node.children)
        if len(node.children) > 0 and sum_children < node.value:
            # create empty slice to fill remaining space among child nodes
            self.create_series(
                SunburstNode(
                    label="",
                    path="",
                    value=node.value - sum_children,
                    unit="",
                    decimals=0,
                    children=[],
                    parent=node,
                ),
                parent_slice=slice_,
                level=level + 1,
                index=len(node.children),
                empty=True,
            )

        if level < self.total_levels - 1 and len(node.children) == 0:
            # create empty slice to fill space in unused levels
            self.create_series(
                SunburstNode(
                    label="",
                    path="",
                    value=node.value,
                    unit="",
                    decimals=0,
                    children=[],
                    parent=node,
                ),
                parent_slice=slice_,
                level=level + 1,
                index=len(node.children),
                empty=True,
            )

    def slice_hovered(self, enter: bool, slice_: SunburstSlice) -> None:  # noqa: FBT001
        node = slice_.node

        self._update_callout(node.get_callout_text())
        if enter:
            self.callout.show()
            if self._clickable_slices:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
        else:
            self.callout.hide()
            if self._clickable_slices:
                self.setCursor(Qt.CursorShape.ArrowCursor)

    def update_callout(self) -> None:
        if self.callout.isVisible():
            self._update_callout(self.callout.text)

    def _update_callout(self, text: str) -> None:
        cursor_pos = QCursor.pos()
        view_pos = self.mapFromGlobal(cursor_pos)
        scene_pos = self.mapToScene(view_pos)

        center_x = self.rect().center().x()
        left = scene_pos.x() > center_x

        self.callout.set_text(text, left=left)
        self.callout.set_anchor(scene_pos)
        self.callout.setZValue(11)
        self.callout.update_geometry()

    def slice_clicked(self, slice_: SunburstSlice) -> None:
        if not self._clickable_slices:
            return
        self.signal_slice_clicked.emit(slice_.node.path)

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        self.signal_mouse_move.emit()
        return super().mouseMoveEvent(event)
