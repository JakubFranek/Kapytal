from collections.abc import Sequence
from numbers import Real

import matplotlib as mpl
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
        sizes = [data[0] for data in data]
        labels = [data[1] for data in data]
        self.chart.axes.pie(
            sizes,
            labels=labels,
            colors=mpl.colormaps["Set2"](range(len(sizes))),
            startangle=90,
            rotatelabels=True,
            labeldistance=0.75,
            counterclock=False,
            textprops={"va": "center", "rotation_mode": "anchor"},
        )
        self.chart.axes.relim()
        self.chart.axes.autoscale()
        self.chart.draw()
        self.chart_toolbar.update()
