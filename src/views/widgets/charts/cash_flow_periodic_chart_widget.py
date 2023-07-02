import math
from collections.abc import Sequence
from typing import TYPE_CHECKING

import mplcursors
from matplotlib.container import BarContainer
from matplotlib.ticker import StrMethodFormatter
from mplcursors import Selection
from PyQt6.QtWidgets import QWidget
from src.models.statistics.cashflow_stats import CashFlowStats
from src.views.widgets.charts.chart_widget import ChartWidget

if TYPE_CHECKING:
    from matplotlib.text import Annotation

BAR_WIDTH = 0.2


class CashFlowPeriodicChartWidget(ChartWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.chart.axes.figure.set_layout_engine("tight")

    def load_data(self, stats_sequence: Sequence[CashFlowStats]) -> None:
        axes = self.chart.axes
        axes.clear()

        currency = stats_sequence[0].inflows.currency

        incomes = []
        inward_transfers = []
        refunds = []
        expenses = []
        outward_transfers = []
        cash_flow = []
        gain_loss = []
        max_value = 0
        min_value = 0
        for stats in stats_sequence:
            incomes.append(stats.incomes.value_rounded)
            inward_transfers.append(stats.inward_transfers.value_rounded)
            refunds.append(stats.refunds.value_rounded)
            expenses.append(stats.expenses.value_rounded)
            outward_transfers.append(stats.outward_transfers.value_rounded)
            cash_flow.append(stats.delta_neutral.value_rounded)
            gain_loss.append(stats.delta_performance.value_rounded)
            max_value = max(
                stats.inflows.value_rounded,
                stats.outflows.value_rounded,
                stats.delta_neutral.value_rounded,
                stats.delta_performance.value_rounded,
                max_value,
            )
            min_value = min(
                stats.inflows.value_rounded,
                stats.outflows.value_rounded,
                stats.delta_neutral.value_rounded,
                stats.delta_performance.value_rounded,
                min_value,
            )

        refund_bottom = [x + y for x, y in zip(incomes, inward_transfers, strict=True)]

        x1 = list(range(len(incomes)))
        x2 = [x + BAR_WIDTH for x in x1]
        x3 = [x + BAR_WIDTH for x in x2]
        x4 = [x + BAR_WIDTH for x in x3]
        axes.bar(x1, incomes, width=BAR_WIDTH, color="green", label="Income")
        axes.bar(
            x1,
            inward_transfers,
            width=BAR_WIDTH,
            bottom=incomes,
            color="limegreen",
            label="Inward Transfers",
        )
        axes.bar(
            x1,
            refunds,
            width=BAR_WIDTH,
            bottom=refund_bottom,
            color="lime",
            label="Refunds",
        )
        axes.bar(x2, expenses, width=BAR_WIDTH, color="red", label="Expenses")
        axes.bar(
            x2,
            outward_transfers,
            width=BAR_WIDTH,
            bottom=expenses,
            color="salmon",
            label="Outward Transfers",
        )
        axes.bar(x3, cash_flow, width=BAR_WIDTH, color="royalblue", label="Cash Flow")
        axes.bar(x4, gain_loss, width=BAR_WIDTH, color="orange", label="Gain / Loss")

        axes.set_axisbelow(True)
        axes.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        axes.grid(visible=True, axis="y")
        axes.set_ylabel(currency.code)
        axes.set_xticks(
            [x + 1.5 * BAR_WIDTH for x in x1],
            [stats.period for stats in stats_sequence],
        )

        yticks = axes.get_yticks()
        step = abs(yticks[1] - yticks[0])
        ymax = math.ceil(float(max_value) / step) * step
        ymin = math.floor(float(min_value) / step) * step
        axes.set_ylim(ymin, ymax)

        def show_annotation(sel: Selection) -> None:
            if type(sel.artist) == BarContainer:
                bar = sel.artist[sel.index]
                annotation: Annotation = sel.annotation
                annotation.set_text(
                    f"{sel.artist.get_label()}: "
                    f"{round(bar.get_height(),currency.places):,.{currency.places}f} "
                    f"{currency.code}"
                )
                annotation.xy = (
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                )
                bbox_patch = annotation.get_bbox_patch()
                if bbox_patch is not None:
                    bbox_patch.set_alpha(0.8)

        cursor = mplcursors.cursor(pickables=[axes])
        cursor.connect("add", show_annotation)

        axes.legend()
