from collections.abc import Sequence

from PyQt6.QtWidgets import QWidget
from src.views.widgets.charts.chart_widget import ChartWidget


class PieChartWidget(ChartWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.chart.axes.figure.set_layout_engine("tight")
        self.lines = None

    def load_data(self, sizes: Sequence, labels: Sequence[str]) -> None:
        self.chart.axes.pie(sizes, labels=labels)
        self.chart.axes.relim()
        self.chart.axes.autoscale()
        self.chart.draw()
        self.chart_toolbar.update()
