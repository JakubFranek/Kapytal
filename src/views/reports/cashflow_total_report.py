from decimal import Decimal
from enum import Enum, auto

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QWidget
from src.models.model_objects.currency_objects import CashAmount
from src.models.statistics.cashflow_stats import CashFlowStats
from src.presenters.utilities.event import Event
from src.utilities.formatting import format_percentage
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
    signal_recalculate_report = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle("Cash Flow Report - Total")
        self.setWindowIcon(icons.bar_chart)

        self.event_show_transactions = Event()  # called with TransactionGroup argument

        self.chart_widget = CashFlowTotalChartView(self)
        self.horizontalLayout.addWidget(self.chart_widget)

        self._initialize_actions()
        self.set_recalculate_report_action_state(enabled=False)

        self.resize(1150, 600)

    def load_stats(self, stats: CashFlowStats) -> None:
        set_label(self.incomeAmountLabel, stats.incomes.balance)
        set_label(self.inwardTransfersAmountLabel, stats.inward_transfers.balance)
        set_label(self.refundsAmountLabel, stats.refunds.balance)
        set_label(self.initialBalancesAmountLabel, stats.initial_balances)
        set_label(self.inflowAmountLabel, stats.inflows.balance)

        set_label(self.expensesAmountLabel, -stats.expenses.balance)
        set_label(self.outwardTransfersAmountLabel, -stats.outward_transfers.balance)
        set_label(self.outflowAmountLabel, -stats.outflows.balance)

        set_label(self.cashFlowAmountLabel, stats.delta_neutral.balance)
        set_label(
            self.gainLossSecuritiesAmountLabel, stats.delta_performance_securities
        )
        set_label(
            self.gainLossCurrenciesAmountLabel, stats.delta_performance_currencies
        )
        set_label(self.gainLossAmountLabel, stats.delta_performance)

        self.savingsRateAmountLabel.setText(format_percentage(100 * stats.savings_rate))
        set_label_color(self.savingsRateAmountLabel, stats.savings_rate)

        set_label(self.netGrowthAmountLabel, stats.delta_total)

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


def set_label(label: QLabel, value: CashAmount) -> None:
    label.setText(value.to_str_rounded())
    set_label_color(label, value)


def set_label_color(label: QLabel, value: CashAmount | Decimal) -> None:
    _value = value.value_rounded if isinstance(value, CashAmount) else value

    if _value.is_nan() or _value == 0:
        label.setStyleSheet(f"color: {colors.get_gray().name()}")
    elif _value > 0:
        label.setStyleSheet(f"color: {colors.get_green().name()}")
    else:
        label.setStyleSheet(f"color: {colors.get_red().name()}")
