import math
from collections.abc import Sequence
from dataclasses import dataclass
from numbers import Real
from typing import Self

import matplotlib as mpl
from matplotlib.axes import Axes
from PyQt6.QtWidgets import QWidget
from src.views.widgets.charts.chart_widget import ChartWidget


@dataclass
class SunburstNode:
    label: str
    value: Real
    children: list[Self]

    def clear_label(self) -> None:
        self.label = ""
        for child in self.children:
            child.clear_label()


class SunburstChartWidget(ChartWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent, polar=True)

        self.chart.axes.figure.set_layout_engine("tight")
        self.lines = None

    def load_data(self, data: Sequence) -> None:
        self.chart.axes.clear()
        create_sunburst_chart(self.chart.axes, data)
        self.chart.draw()
        self.chart_toolbar.update()


def create_sunburst_chart(
    ax: Axes,
    nodes: Sequence[SunburstNode],
    color: str | Sequence = "white",
    total: Real = math.pi * 2,
    offset: Real = 0,
    level: int = 0,
) -> None:
    if level == 0 and len(nodes) == 1:
        node = nodes[0]
        ax.bar(x=[0], height=[0.5], width=[math.pi * 2], color=color)
        ax.text(0, 0, node.label, ha="center", va="center")
        create_sunburst_chart(
            ax,
            node.children,
            color=mpl.colormaps["tab10"](range(len(node.children))),
            total=node.value,
            level=level + 1,
        )
    elif nodes:
        d = math.pi * 2 / total  # conversion factor between values and radians
        labels: list[str] = []
        widths = []
        for node in nodes:
            labels.append(node.label)
            widths.append(node.value * d)

        values = cumulative_sum([offset * d] + widths[:-1])
        heights = [1] * len(nodes)
        bottoms = [level - 0.5] * len(nodes)

        try:
            cmap = mpl.colors.LinearSegmentedColormap.from_list("", [color, "white"])
            colors = [cmap(i) for i in get_color_map_ratios(len(nodes))]
            pass
        except ValueError:
            colors = color

        rects = ax.bar(
            values,
            heights,
            widths,
            bottoms,
            linewidth=1,
            edgecolor="white",
            align="edge",
            label=labels,
            color=colors,
        )
        for rect, label in zip(rects, labels, strict=True):
            x = rect.get_x() + rect.get_width() / 2
            y = rect.get_y() + rect.get_height() / 2
            rotation = (90 + (360 - (180 * x / math.pi) % 180)) % 360
            ha = "left" if x >= math.pi else "right"
            if len(label) > 15 and " " in label:
                index = get_middle_whitespace_index(label)
                if index > 0:
                    _label = label[:index] + "\n" + label[index + 1 :]
                else:
                    _label = label
            else:
                _label = label
            ax.text(
                x,
                y + 0.45,
                _label,
                rotation=rotation,
                rotation_mode="anchor",
                ha=ha,
                va="center",
            )

        local_offset = offset
        for index, node in enumerate(nodes):
            try:
                child_color = colors[index % len(nodes)]
                if len(child_color) != 4:  # noqa: PLR2004
                    child_color = color
            except TypeError:
                child_color = color

            create_sunburst_chart(
                ax,
                node.children,
                color=child_color,
                total=total,
                offset=local_offset,
                level=level + 1,
            )
            local_offset += node.value

    if level == 0:
        ax.set_theta_direction(-1)
        ax.set_theta_zero_location("N")
        ax.set_axis_off()


def cumulative_sum(numbers: Sequence[Real]) -> tuple[Real]:
    return tuple([sum(numbers[:i]) for i in range(1, len(numbers) + 1)])


def get_color_map_ratios(n: int) -> tuple[float]:
    if n == 0:
        raise ValueError("Parameter 'n' must be greater than 0.")
    if n > 0 and n < 4:  # noqa: PLR2004
        return tuple(round(0.2 + 0.2 * i, 2) for i in range(n))
    ratios = tuple(round(i * 0.8 / n, 2) for i in range(n + 1))
    return ratios[1:]


def get_middle_whitespace_index(string: str) -> int:
    middle_index = math.ceil(len(string) / 2)
    left_part = string[:middle_index]
    right_part = string[middle_index:]
    right_whitespace_index = right_part.find(" ")
    left_whitespace_index = left_part.rfind(" ")

    if right_whitespace_index == -1 and left_whitespace_index == -1:
        return -1
    if right_whitespace_index == -1:
        return left_whitespace_index
    if left_whitespace_index == -1:
        return right_whitespace_index + middle_index

    distance_left = abs(middle_index - left_whitespace_index)
    distance_right = right_whitespace_index
    if distance_right <= distance_left:
        return right_whitespace_index + middle_index
    return left_whitespace_index