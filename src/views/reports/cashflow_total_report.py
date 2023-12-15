from enum import Enum, auto

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget
from src.models.statistics.cashflow_stats import CashFlowStats
from src.presenters.utilities.event import Event
from src.views import colors, icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.reports.Ui_cash_flow_total_report import Ui_CashFlowTotalReport
from src.views.widgets.charts.cash_flow_total_chart_view import (
    CashFlowTotalChartView,
)


class TransactionGroup(Enum):
    INCOME = auto()
    INWARD_TRANSFER = auto()
    REFUND = auto()
    INFLOWS = auto()
    OUTWARD_TRANSFER = auto()
    EXPENSE = auto()
    OUTFLOWS = auto()
    CASHFLOW = auto()


class CashFlowTotalReport(CustomWidget, Ui_CashFlowTotalReport):
    event_show_transactions = Event()  # called with TransactionGroup argument
    signal_recalculate_report = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle("Cash Flow Report - Total")
        self.setWindowIcon(icons.bar_chart)

        self.chart_widget = CashFlowTotalChartView(self)
        self.horizontalLayout.addWidget(self.chart_widget)

        self._initialize_actions()
        self.set_recalculate_report_action_state(enabled=False)

        self.resize(1130, 600)

    def load_stats(self, stats: CashFlowStats) -> None:
        self.incomeAmountLabel.setText(stats.incomes.balance.to_str_rounded())
        if stats.incomes.balance.is_positive():
            self.incomeAmountLabel.setStyleSheet(f"color: {colors.get_green().name()}")

        self.inwardTransfersAmountLabel.setText(
            stats.inward_transfers.balance.to_str_rounded()
        )
        if stats.inward_transfers.balance.is_positive():
            self.inwardTransfersAmountLabel.setStyleSheet(
                f"color: {colors.get_green().name()}"
            )

        self.refundsAmountLabel.setText(stats.refunds.balance.to_str_rounded())
        if stats.refunds.balance.is_positive():
            self.refundsAmountLabel.setStyleSheet(f"color: {colors.get_green().name()}")

        self.initialBalancesAmountLabel.setText(stats.initial_balances.to_str_rounded())
        if stats.initial_balances.is_positive():
            self.initialBalancesAmountLabel.setStyleSheet(
                f"color: {colors.get_green().name()}"
            )

        self.inflowAmountLabel.setText(stats.inflows.balance.to_str_rounded())
        if stats.inflows.balance.is_positive():
            self.inflowAmountLabel.setStyleSheet(f"color: {colors.get_green().name()}")

        self.expensesAmountLabel.setText("-" + stats.expenses.balance.to_str_rounded())
        if stats.expenses.balance.is_positive():
            self.expensesAmountLabel.setStyleSheet(f"color: {colors.get_red().name()}")
        self.outwardTransfersAmountLabel.setText(
            "-" + stats.outward_transfers.balance.to_str_rounded()
        )
        if stats.outward_transfers.balance.is_positive():
            self.outwardTransfersAmountLabel.setStyleSheet(
                f"color: {colors.get_red().name()}"
            )
        self.outflowAmountLabel.setText("-" + stats.outflows.balance.to_str_rounded())
        if stats.outflows.balance.is_positive():
            self.outflowAmountLabel.setStyleSheet(f"color: {colors.get_red().name()}")

        self.gainLossSecuritiesAmountLabel.setText(
            stats.delta_performance_securities.to_str_rounded()
        )
        if stats.delta_performance_securities.is_positive():
            self.gainLossSecuritiesAmountLabel.setStyleSheet(
                f"color: {colors.get_green().name()}"
            )
        elif stats.delta_performance_securities.is_negative():
            self.gainLossSecuritiesAmountLabel.setStyleSheet(
                f"color: {colors.get_red().name()}"
            )

        self.gainLossCurrenciesAmountLabel.setText(
            stats.delta_performance_currencies.to_str_rounded()
        )
        if stats.delta_performance_currencies.is_positive():
            self.gainLossCurrenciesAmountLabel.setStyleSheet(
                f"color: {colors.get_green().name()}"
            )
        elif stats.delta_performance_currencies.is_negative():
            self.gainLossCurrenciesAmountLabel.setStyleSheet(
                f"color: {colors.get_red().name()}"
            )

        self.gainLossAmountLabel.setText(stats.delta_performance.to_str_rounded())
        if stats.delta_performance.is_positive():
            self.gainLossAmountLabel.setStyleSheet(
                f"color: {colors.get_green().name()}"
            )
        elif stats.delta_performance.is_negative():
            self.gainLossAmountLabel.setStyleSheet(f"color: {colors.get_red().name()}")

        self.cashFlowAmountLabel.setText(stats.delta_neutral.balance.to_str_rounded())
        if stats.delta_neutral.balance.is_positive():
            self.cashFlowAmountLabel.setStyleSheet(
                f"color: {colors.get_green().name()}"
            )
        elif stats.delta_neutral.balance.is_negative():
            self.cashFlowAmountLabel.setStyleSheet(f"color: {colors.get_red().name()}")

        self.savingsRateAmountLabel.setText(f"{100 * stats.savings_rate:.2f}%")
        if stats.savings_rate > 0:
            self.savingsRateAmountLabel.setStyleSheet(
                f"color: {colors.get_green().name()}"
            )
        elif stats.savings_rate < 0:
            self.savingsRateAmountLabel.setStyleSheet(
                f"color: {colors.get_red().name()}"
            )

        self.netGrowthAmountLabel.setText(stats.delta_total.to_str_rounded())
        if stats.delta_total.is_positive():
            self.netGrowthAmountLabel.setStyleSheet(
                f"color: {colors.get_green().name()}"
            )
        elif stats.delta_total.is_negative():
            self.netGrowthAmountLabel.setStyleSheet(f"color: {colors.get_red().name()}")

        self.actionShow_Income_Transactions.setEnabled(
            len(stats.incomes.transactions) > 0
        )
        self.actionShow_Inward_Transfers.setEnabled(
            len(stats.inward_transfers.transactions) > 0
        )
        self.actionShow_Refunds.setEnabled(len(stats.refunds.transactions) > 0)
        self.actionShow_Inflow_Transactions.setEnabled(
            len(stats.inflows.transactions) > 0
        )
        self.actionShow_Expense_Transactions.setEnabled(
            len(stats.expenses.transactions) > 0
        )
        self.actionShow_Outward_Transfers.setEnabled(
            len(stats.outward_transfers.transactions) > 0
        )
        self.actionShow_Outflow_Transactions.setEnabled(
            len(stats.outflows.transactions) > 0
        )
        self.actionShow_All_Transactions.setEnabled(
            len(stats.inflows) > 0 or len(stats.outflows) > 0
        )

        self.chart_widget.load_data(stats)

    def set_recalculate_report_action_state(self, *, enabled: bool) -> None:
        self.actionRecalculate_Report.setEnabled(enabled)
        self.recalculateToolButton.setVisible(enabled)

    def _initialize_actions(self) -> None:
        self.actionShow_Income_Transactions.setIcon(icons.table)
        self.actionShow_Inward_Transfers.setIcon(icons.table)
        self.actionShow_Refunds.setIcon(icons.table)
        self.actionShow_Inflow_Transactions.setIcon(icons.table)
        self.actionShow_Expense_Transactions.setIcon(icons.table)
        self.actionShow_Outward_Transfers.setIcon(icons.table)
        self.actionShow_Outflow_Transactions.setIcon(icons.table)
        self.actionShow_All_Transactions.setIcon(icons.table)
        self.actionRecalculate_Report.setIcon(icons.refresh)

        self.actionShow_Income_Transactions.triggered.connect(
            lambda: self.event_show_transactions(TransactionGroup.INCOME)
        )
        self.actionShow_Inward_Transfers.triggered.connect(
            lambda: self.event_show_transactions(TransactionGroup.INWARD_TRANSFER)
        )
        self.actionShow_Refunds.triggered.connect(
            lambda: self.event_show_transactions(TransactionGroup.REFUND)
        )
        self.actionShow_Inflow_Transactions.triggered.connect(
            lambda: self.event_show_transactions(TransactionGroup.INFLOWS)
        )
        self.actionShow_Expense_Transactions.triggered.connect(
            lambda: self.event_show_transactions(TransactionGroup.EXPENSE)
        )
        self.actionShow_Outward_Transfers.triggered.connect(
            lambda: self.event_show_transactions(TransactionGroup.OUTWARD_TRANSFER)
        )
        self.actionShow_Outflow_Transactions.triggered.connect(
            lambda: self.event_show_transactions(TransactionGroup.OUTFLOWS)
        )
        self.actionShow_All_Transactions.triggered.connect(
            lambda: self.event_show_transactions(TransactionGroup.CASHFLOW)
        )
        self.actionRecalculate_Report.triggered.connect(
            self.signal_recalculate_report.emit
        )

        self.incomeToolButton.setDefaultAction(self.actionShow_Income_Transactions)
        self.inwardTransfersToolButton.setDefaultAction(
            self.actionShow_Inward_Transfers
        )
        self.refundsToolButton.setDefaultAction(self.actionShow_Refunds)
        self.totalInflowToolButton.setDefaultAction(self.actionShow_Inflow_Transactions)
        self.expensesToolButton.setDefaultAction(self.actionShow_Expense_Transactions)
        self.outwardTransfersToolButton.setDefaultAction(
            self.actionShow_Outward_Transfers
        )
        self.totalOutflowToolButton.setDefaultAction(
            self.actionShow_Outflow_Transactions
        )
        self.cashflowToolButton.setDefaultAction(self.actionShow_All_Transactions)
        self.recalculateToolButton.setDefaultAction(self.actionRecalculate_Report)
