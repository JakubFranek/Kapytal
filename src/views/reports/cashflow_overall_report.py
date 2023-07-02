from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from src.models.statistics.cashflow_stats import CashFlowStats
from src.views import colors, icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.reports.Ui_cash_flow_overall_report import (
    Ui_CashFlowOverallReport,
)
from src.views.widgets.charts.cash_flow_overall_chart_widget import (
    CashFlowOverallChartWidget,
)


class CashFlowOverallReport(CustomWidget, Ui_CashFlowOverallReport):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle("Cash Flow Report - Overall")
        self.setWindowIcon(icons.bar_chart)

        self.chart_widget = CashFlowOverallChartWidget(self)
        self.horizontalLayout.addWidget(self.chart_widget)

    def load_stats(self, stats: CashFlowStats) -> None:
        self.incomeAmountLabel.setText(stats.incomes.to_str_rounded())
        if stats.incomes.is_positive():
            self.incomeAmountLabel.setStyleSheet(f"color: {colors.get_green().name()}")

        self.inwardTransfersAmountLabel.setText(stats.inward_transfers.to_str_rounded())
        if stats.inward_transfers.is_positive():
            self.inwardTransfersAmountLabel.setStyleSheet(
                f"color: {colors.get_green().name()}"
            )

        self.refundsAmountLabel.setText(stats.refunds.to_str_rounded())
        if stats.refunds.is_positive():
            self.refundsAmountLabel.setStyleSheet(f"color: {colors.get_green().name()}")

        self.inflowAmountLabel.setText(stats.inflows.to_str_rounded())
        if stats.inflows.is_positive():
            self.inflowAmountLabel.setStyleSheet(f"color: {colors.get_green().name()}")

        self.expensesAmountLabel.setText("-" + stats.expenses.to_str_rounded())
        if stats.expenses.is_positive():
            self.expensesAmountLabel.setStyleSheet(f"color: {colors.get_red().name()}")
        self.outwardTransfersAmountLabel.setText(
            "-" + stats.outward_transfers.to_str_rounded()
        )
        if stats.outward_transfers.is_positive():
            self.outwardTransfersAmountLabel.setStyleSheet(
                f"color: {colors.get_red().name()}"
            )
        self.outflowAmountLabel.setText("-" + stats.outflows.to_str_rounded())
        if stats.outflows.is_positive():
            self.outflowAmountLabel.setStyleSheet(f"color: {colors.get_red().name()}")

        self.gainLossAmountLabel.setText(stats.delta_performance.to_str_rounded())
        if stats.delta_performance.is_positive():
            self.gainLossAmountLabel.setStyleSheet(
                f"color: {colors.get_green().name()}"
            )
        elif stats.delta_performance.is_negative():
            self.gainLossAmountLabel.setStyleSheet(f"color: {colors.get_red().name()}")

        self.cashFlowAmountLabel.setText(stats.delta_neutral.to_str_rounded())
        if stats.delta_neutral.is_positive():
            self.cashFlowAmountLabel.setStyleSheet(
                f"color: {colors.get_green().name()}"
            )
        elif stats.delta_neutral.is_negative():
            self.cashFlowAmountLabel.setStyleSheet(f"color: {colors.get_red().name()}")

        self.netGrowthAmountLabel.setText(stats.delta_total.to_str_rounded())
        if stats.delta_total.is_positive():
            self.netGrowthAmountLabel.setStyleSheet(
                f"color: {colors.get_green().name()}"
            )
        elif stats.delta_total.is_negative():
            self.netGrowthAmountLabel.setStyleSheet(f"color: {colors.get_red().name()}")

        self.chart_widget.load_data(stats)
