import math
from collections.abc import Sequence
from enum import Enum, auto
from typing import TYPE_CHECKING

import mplcursors
from matplotlib.container import BarContainer
from matplotlib.ticker import PercentFormatter, StrMethodFormatter
from mplcursors import Selection
from PyQt6.QtWidgets import QWidget
from src.models.statistics.cashflow_stats import CashFlowStats
from src.views.widgets.charts.chart_widget import ChartWidget

if TYPE_CHECKING:
    from matplotlib.text import Annotation


class ChartData(Enum):
    ALL = auto()
    INFLOWS = auto()
    OUTFLOWS = auto()
    CASH_FLOW = auto()
    GAIN_LOSS = auto()
    NET_GROWTH = auto()
    SAVINGS_RATE = auto()


BAR_WIDTH_4 = 0.15
BAR_WIDTH_1 = 0.75


class CashFlowPeriodicChartWidget(ChartWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.chart.axes.figure.set_layout_engine("tight")

    def load_data(
        self, stats_sequence: Sequence[CashFlowStats], chart_data: ChartData
    ) -> None:
        width = BAR_WIDTH_4 if chart_data == ChartData.ALL else BAR_WIDTH_1

        axes = self.chart.axes
        axes.clear()

        currency = stats_sequence[0].inflows.currency

        incomes = []
        inward_transfers = []
        refunds = []
        initial_balances = []
        expenses = []
        outward_transfers = []
        cash_flow = []
        gain_loss = []
        net_growth = []
        savings_rate = []
        max_value = 0
        min_value = 0
        for stats in stats_sequence:
            incomes.append(stats.incomes.value_rounded)
            inward_transfers.append(stats.inward_transfers.value_rounded)
            refunds.append(stats.refunds.value_rounded)
            initial_balances.append(stats.initial_balances.value_rounded)
            expenses.append(stats.expenses.value_rounded)
            outward_transfers.append(stats.outward_transfers.value_rounded)
            cash_flow.append(stats.delta_neutral.value_rounded)
            gain_loss.append(stats.delta_performance.value_rounded)
            net_growth.append(stats.delta_total.value_rounded)
            if stats.savings_rate.is_nan():
                savings_rate.append(0)
            else:
                savings_rate.append(stats.savings_rate)

            if chart_data == ChartData.ALL:
                value_set = [
                    stats.inflows.value_rounded,
                    stats.outflows.value_rounded,
                    stats.delta_neutral.value_rounded,
                    stats.delta_performance.value_rounded,
                ]
            elif chart_data == ChartData.INFLOWS:
                value_set = [stats.inflows.value_rounded]
            elif chart_data == ChartData.OUTFLOWS:
                value_set = [stats.outflows.value_rounded]
            elif chart_data == ChartData.CASH_FLOW:
                value_set = [stats.delta_neutral.value_rounded]
            elif chart_data == ChartData.GAIN_LOSS:
                value_set = [stats.delta_performance.value_rounded]
            elif chart_data == ChartData.NET_GROWTH:
                value_set = [stats.delta_total.value_rounded]
            elif chart_data == ChartData.SAVINGS_RATE:
                value_set = [0] if stats.savings_rate.is_nan() else [stats.savings_rate]

            max_value = max(
                *value_set,
                max_value,
            )
            min_value = min(
                *value_set,
                min_value,
            )

        refund_bottom = [x + y for x, y in zip(incomes, inward_transfers, strict=True)]
        initial_balances_bottom = [
            x + y + z
            for x, y, z in zip(incomes, inward_transfers, refunds, strict=True)
        ]

        x1 = list(range(len(incomes)))
        _width = width if chart_data == ChartData.ALL else 0
        x2 = [x + _width for x in x1]
        x3 = [x + _width for x in x2]
        x4 = [x + _width for x in x3]

        if chart_data in {ChartData.ALL, ChartData.INFLOWS}:
            axes.bar(x1, incomes, width=width, color="darkgreen", label="Income")
            axes.bar(
                x1,
                inward_transfers,
                width=width,
                bottom=incomes,
                color="green",
                label="Inward Transfers",
            )
            axes.bar(
                x1,
                refunds,
                width=width,
                bottom=refund_bottom,
                color="limegreen",
                label="Refunds",
            )
            axes.bar(
                x1,
                initial_balances,
                width=width,
                bottom=initial_balances_bottom,
                color="lime",
                label="Initial Balances",
            )
        if chart_data in {ChartData.ALL, ChartData.OUTFLOWS}:
            axes.bar(x2, expenses, width=width, color="red", label="Expenses")
            axes.bar(
                x2,
                outward_transfers,
                width=width,
                bottom=expenses,
                color="salmon",
                label="Outward Transfers",
            )
        if chart_data in {ChartData.ALL, ChartData.CASH_FLOW}:
            axes.bar(x3, cash_flow, width=width, color="royalblue", label="Cash Flow")
        if chart_data in {ChartData.ALL, ChartData.GAIN_LOSS}:
            axes.bar(
                x4, gain_loss, width=width, color="orange", label="Total Gain / Loss"
            )
        if chart_data == ChartData.NET_GROWTH:
            axes.bar(x1, net_growth, width=width, color="deeppink", label="Net Growth")
        if chart_data == ChartData.SAVINGS_RATE:
            axes.bar(
                x1, savings_rate, width=width, color="purple", label="Savings Rate"
            )

        axes.set_axisbelow(True)
        if chart_data != ChartData.SAVINGS_RATE:
            axes.set_ylabel(currency.code)
            axes.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        else:
            axes.set_ylabel("Savings Rate")
            axes.yaxis.set_major_formatter(PercentFormatter(xmax=1))
        axes.grid(visible=True, axis="y")

        x_tick_labels = [stats.period for stats in stats_sequence]
        if chart_data == ChartData.ALL:
            axes.set_xticks([x + 1.5 * width for x in x1], x_tick_labels)
        else:
            axes.set_xticks(x1, x_tick_labels)
        if len(x_tick_labels) > 10:
            axes.set_xticklabels(x_tick_labels, rotation=45, ha="right")

        yticks = axes.get_yticks()
        step = abs(yticks[1] - yticks[0])
        ymax = math.ceil(float(max_value) / step) * step
        ymin = math.floor(float(min_value) / step) * step
        axes.set_ylim(ymin, ymax)

        def show_annotation(sel: Selection) -> None:
            if type(sel.artist) == BarContainer:
                bar = sel.artist[sel.index]
                annotation: Annotation = sel.annotation
                if chart_data != ChartData.SAVINGS_RATE:
                    annotation.set_text(
                        f"{sel.artist.get_label()}: "
                        f"{round(bar.get_height(),currency.places):,.{currency.places}f} "
                        f"{currency.code}"
                    )
                else:
                    annotation.set_text(
                        f"{sel.artist.get_label()}: {bar.get_height():.2%}"
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
        self.chart.draw()
