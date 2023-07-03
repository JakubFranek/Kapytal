import math
from collections.abc import Sequence
from numbers import Real

from matplotlib.axes import Axes
from PyQt6.QtWidgets import QWidget
from src.views.widgets.charts.chart_widget import ChartWidget


class SunburstChartWidget(ChartWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent, polar=True)

        self.chart.axes.figure.set_layout_engine("tight")
        self.lines = None

    def load_data(self, data: Sequence) -> None:
        self.chart.axes.clear()
        create_sunburst_chart(self.chart.axes, data)
        self.chart_toolbar.update()


def create_sunburst_chart(
    ax: Axes,
    nodes: Sequence,
    total: Real = math.pi * 2,
    offset: Real = 0,
    level: int = 0,
) -> None:
    if level == 0 and len(nodes) == 1:
        label, value, subnodes = nodes[0]
        ax.bar(x=[0], height=[0.5], width=[math.pi * 2])
        ax.text(0, 0, label, ha="center", va="center")
        create_sunburst_chart(ax, subnodes, total=value, level=level + 1)
    elif nodes:
        d = math.pi * 2 / total  # conversion factor between values and radians
        labels = []
        widths = []
        local_offset = offset
        for label, value, subnodes in nodes:
            labels.append(label)
            widths.append(value * d)
            create_sunburst_chart(
                ax, subnodes, total=total, offset=local_offset, level=level + 1
            )
            local_offset += value

        foo = [offset * d] + widths[:-1]
        values = cumulative_sum(foo)
        heights = [1] * len(nodes)
        bottoms = [level - 0.5] * len(nodes)
        rects = ax.bar(
            values,
            heights,
            widths,
            bottoms,
            linewidth=1,
            edgecolor="white",
            align="edge",
            label=labels,
        )
        for rect, label in zip(rects, labels, strict=True):
            x = rect.get_x() + rect.get_width() / 2
            y = rect.get_y() + rect.get_height() / 2
            rotation = (90 + (360 - (180 * x / math.pi) % 180)) % 360
            ax.text(x, y, label, rotation=rotation, ha="center", va="center")

    if level == 0:
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location("N")
        ax.set_axis_off()


def cumulative_sum(numbers: Sequence[Real]) -> tuple[Real]:
    return tuple([sum(numbers[:i]) for i in range(1, len(numbers) + 1)])
