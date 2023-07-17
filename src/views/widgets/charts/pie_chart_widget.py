from collections.abc import Sequence
from decimal import Decimal
from numbers import Real

import matplotlib as mpl
import numpy as np
from PyQt6.QtWidgets import QWidget
from src.views.widgets.charts.chart_widget import ChartWidget


class PieChartWidget(ChartWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.chart.axes.figure.set_layout_engine("tight")
        self.lines = None

    def load_data(self, data: Sequence[tuple[Real, str]]) -> None:
        self.chart.axes.clear()
        data = sorted(data, key=lambda x: x[0], reverse=True)

        total = sum(x[0] for x in data)
        others = 0
        sizes = []
        labels = []
        for size, label in data:
            if size > total * Decimal("0.0035"):
                labels.append(label)
                sizes.append(size)
            else:
                others += size
        sizes.append(others)
        labels.append("...")

        _len = len(sizes)
        color_cycle = mpl.colormaps["Set2"](range(_len))
        if _len > 8:
            color_cycle = color_cycle[:8]
            _single_cycle = color_cycle[:8]
            extra_cycles = _len // 8
            for _ in range(extra_cycles):
                color_cycle = np.append(color_cycle, _single_cycle, axis=0)

        self.chart.axes.pie(
            sizes,
            labels=labels,
            colors=color_cycle,
            startangle=90,
            rotatelabels=True,
            labeldistance=1.01,
            counterclock=False,
            textprops={"va": "center", "rotation_mode": "anchor"},
        )
        self.chart.axes.relim()
        self.chart.axes.autoscale()
        self.chart.draw()
        self.chart_toolbar.update()
