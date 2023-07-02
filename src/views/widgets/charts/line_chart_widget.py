from collections.abc import Sequence

import mplcursors
from matplotlib.dates import DateFormatter
from PyQt6.QtWidgets import QWidget
from src.views.widgets.charts.chart_widget import ChartWidget


class LineChartWidget(ChartWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.chart.axes.grid(visible=True)
        self.chart.axes.xaxis.set_major_formatter(DateFormatter("%d.%m.%Y"))
        self.chart.axes.tick_params(axis="x", rotation=30)
        self.chart.axes.figure.set_layout_engine("tight")
        self.lines = None

    def load_data(  # noqa: PLR0913
        self,
        x: Sequence,
        y: Sequence,
        title: str,
        ylabel: str = "",
        xlabel: str = "",
    ) -> None:
        if self.lines is None:
            line = self.chart.axes.plot(x, y, "-", color="tab:blue")
            points = self.chart.axes.plot(x, y, ".", color="tab:blue")
            self.lines = [line[0], points[0]]
            mplcursors.cursor(points)
        else:
            self.lines[0].set_data(x, y)
            self.lines[1].set_data(x, y)
        self.chart.axes.set_title(title)
        self.chart.axes.set_ylabel(ylabel)
        self.chart.axes.set_xlabel(xlabel)

        self.chart.axes.relim()
        self.chart.axes.autoscale()
        self.chart.draw()
        self.chart_toolbar.update()
