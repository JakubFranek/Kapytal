import math

from matplotlib.ticker import StrMethodFormatter
from PyQt6.QtWidgets import QWidget
from src.models.statistics.cashflow_stats import CashFlowStats
from src.views.widgets.charts.chart_widget import ChartWidget

x_labels = ["Inflows", "Outflows", "Cash Flow", "Gain / Loss"]


class CashFlowTotalChartWidget(ChartWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)
        self.chart.axes.figure.set_layout_engine("tight")

    def load_data(self, stats: CashFlowStats) -> None:
        self.chart.axes.clear()
        bar_incomes = self.chart.axes.bar(
            "Inflows", stats.incomes.value_rounded, color="green"
        )
        bar_inward_transfers = self.chart.axes.bar(
            "Inflows",
            stats.inward_transfers.value_rounded,
            bottom=stats.incomes.value_rounded,
            color="limegreen",
        )
        bar_refunds = self.chart.axes.bar(
            "Inflows",
            stats.refunds.value_rounded,
            bottom=stats.incomes.value_rounded + stats.inward_transfers.value_rounded,
            color="lime",
        )

        bar_expenses = self.chart.axes.bar(
            "Outflows", stats.expenses.value_rounded, color="red"
        )
        bar_outward_transfers = self.chart.axes.bar(
            "Outflows",
            stats.outward_transfers.value_rounded,
            bottom=stats.expenses.value_rounded,
            color="salmon",
        )

        bar_cash_flow = self.chart.axes.bar(
            "Cash Flow", stats.delta_neutral.value_rounded, color="royalblue"
        )

        bar_delta_performance = self.chart.axes.bar(
            "Gain / Loss",
            stats.delta_performance.value_rounded,
            color="orange",
        )

        self.chart.axes.bar_label(
            bar_refunds, labels=[f"{stats.inflows.value_rounded:,}"]
        )
        self.chart.axes.bar_label(
            bar_outward_transfers, labels=[f"{stats.outflows.value_rounded:,}"]
        )
        self.chart.axes.bar_label(
            bar_cash_flow, labels=[f"{stats.delta_neutral.value_rounded:,}"]
        )
        self.chart.axes.bar_label(
            bar_delta_performance, labels=[f"{stats.delta_performance.value_rounded:,}"]
        )

        self.chart.axes.set_axisbelow(True)
        self.chart.axes.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        self.chart.axes.grid(visible=True, axis="y")

        self.chart.axes.legend(
            bar_incomes.patches
            + bar_inward_transfers.patches
            + bar_refunds.patches
            + bar_expenses.patches
            + bar_outward_transfers.patches
            + bar_cash_flow.patches
            + bar_delta_performance.patches,
            [
                "Income",
                "Inward Transfers",
                "Refunds",
                "Expenses",
                "Outward Transfers",
                "Cash Flow",
                "Gain / Loss",
            ],
        )

        max_value = max(
            stats.inflows,
            stats.outflows,
            stats.delta_neutral,
            stats.delta_performance,
        )
        min_value = min(
            stats.inflows,
            stats.outflows,
            stats.delta_neutral,
            stats.delta_performance,
        )
        yticks = self.chart.axes.get_yticks()
        step = abs(yticks[1] - yticks[0])
        ymax = math.ceil(float(max_value.value_rounded) / step) * step
        ymin = math.floor(float(min_value.value_rounded) / step) * step
        self.chart.axes.set_ylim(ymin, ymax)
        self.chart.axes.set_ylabel(stats.inflows.currency.code)
