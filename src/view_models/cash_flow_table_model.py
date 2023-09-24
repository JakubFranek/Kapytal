from collections.abc import Sequence

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QFont
from PyQt6.QtWidgets import QTableView
from src.models.base_classes.transaction import Transaction
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.currency_objects import CashAmount
from src.models.statistics.cashflow_stats import CashFlowStats
from src.views import colors
from src.views.constants import CashFlowTableColumn

overline_font = QFont()
overline_font.setOverline(True)  # noqa: FBT003
bold_font = QFont()
bold_font.setBold(True)  # noqa: FBT003

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
COLUMN_HEADERS = {
    CashFlowTableColumn.INCOME: "Income",
    CashFlowTableColumn.INWARD_TRANSFERS: "Inward Transfers",
    CashFlowTableColumn.REFUNDS: "Refunds",
    CashFlowTableColumn.INITIAL_BALANCES: "Initial Balances",
    CashFlowTableColumn.TOTAL_INFLOW: "Total Inflow",
    CashFlowTableColumn.EXPENSES: "Expenses",
    CashFlowTableColumn.OUTWARD_TRANSFERS: "Outward Transfers",
    CashFlowTableColumn.TOTAL_OUTFLOW: "Total Outflow",
    CashFlowTableColumn.DELTA_NEUTRAL: "Cash Flow",
    CashFlowTableColumn.DELTA_PERFORMANCE_SECURITIES: "Securities Gain / Loss",
    CashFlowTableColumn.DELTA_PERFORMANCE_CURRENCIES: "Currencies Gain / Loss",
    CashFlowTableColumn.DELTA_PERFORMANCE: "Total Gain / Loss",
    CashFlowTableColumn.DELTA_TOTAL: "Net Growth",
    CashFlowTableColumn.SAVINGS_RATE: "Savings Rate",
}


class CashFlowTableModel(QAbstractTableModel):
    def __init__(
        self,
        view: QTableView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self._stats: tuple[CashFlowStats, ...] = ()
        self._proxy = proxy

    @property
    def stats(self) -> tuple[CashFlowStats, ...]:
        return self._stats

    def load_cash_flow_stats(self, stats: Sequence[CashFlowStats]) -> None:
        self._stats = tuple(stats)
        self.AVERAGE_ROW = len(self._stats) - 2
        self.TOTAL_ROW = len(self._stats) - 1

    def rowCount(self, index: QModelIndex = ...) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self._stats)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(COLUMN_HEADERS)
        return self._column_count

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return COLUMN_HEADERS[section]
            return self._stats[section].period
        if (
            role == Qt.ItemDataRole.FontRole
            and orientation == Qt.Orientation.Vertical
            and section == self.AVERAGE_ROW
        ):
            return overline_font
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | QFont | QBrush | float | int | None:
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(index.column(), self._stats[index.row()])
        if role == Qt.ItemDataRole.UserRole:
            return self._get_user_role_data(index.column(), self._stats[index.row()])
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return ALIGNMENT_RIGHT
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(
                index.column(), self._stats[index.row()]
            )
        if role == Qt.ItemDataRole.FontRole:
            if index.row() == self.AVERAGE_ROW:
                return overline_font
            if index.row() == self.TOTAL_ROW:
                return bold_font
        return None

    def _get_display_role_data(self, column: int, stats: CashFlowStats) -> str:
        if column == CashFlowTableColumn.SAVINGS_RATE:
            return f"{stats.savings_rate:.2%}"
        return f"{self._get_cash_amount_for_column(stats, column).value_rounded:,}"

    def _get_user_role_data(self, column: int, stats: CashFlowStats) -> float:
        if column == CashFlowTableColumn.SAVINGS_RATE:
            return float(stats.savings_rate)
        return float(self._get_cash_amount_for_column(stats, column).value_rounded)

    def _get_foreground_role_data(
        self, column: int, stats: CashFlowStats
    ) -> QBrush | None:
        if column == CashFlowTableColumn.SAVINGS_RATE:
            if stats.savings_rate.is_nan() or stats.savings_rate == 0:
                return colors.get_gray_brush()
            if stats.savings_rate > 0:
                return colors.get_green_brush()
            if stats.savings_rate < 0:
                return colors.get_red_brush()
        amount = self._get_cash_amount_for_column(stats, column)
        if amount.is_positive():
            return colors.get_green_brush()
        if amount.is_negative():
            return colors.get_red_brush()
        return colors.get_gray_brush()

    def pre_reset_model(self) -> None:
        self._view.setSortingEnabled(False)  # noqa: FBT003
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
        self._view.setSortingEnabled(True)  # noqa: FBT003

    def get_selected_transactions(
        self,
    ) -> tuple[tuple[Transaction, ...], str, str]:
        """Returns a tuple of selected Transactions, type and period."""
        indexes = self._view.selectedIndexes()
        if len(indexes) != 1:
            raise InvalidOperationError(
                "Transactions can be shown for only for exactly one selection."
            )
        index = indexes[0]
        if self._proxy:
            index = self._proxy.mapToSource(index)

        stats = self._stats[index.row()]
        return (
            tuple(self._get_transactions_for_column(stats, index.column())),
            self.headerData(
                index.column(), Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole
            ),
            self.headerData(
                index.row(), Qt.Orientation.Vertical, Qt.ItemDataRole.DisplayRole
            ),
        )

    def _get_cash_amount_for_column(
        self, stats: CashFlowStats, column: int
    ) -> CashAmount:
        if column == CashFlowTableColumn.INCOME:
            return stats.incomes.balance
        if column == CashFlowTableColumn.INWARD_TRANSFERS:
            return stats.inward_transfers.balance
        if column == CashFlowTableColumn.REFUNDS:
            return stats.refunds.balance
        if column == CashFlowTableColumn.INITIAL_BALANCES:
            return stats.initial_balances
        if column == CashFlowTableColumn.TOTAL_INFLOW:
            return stats.inflows.balance
        if column == CashFlowTableColumn.EXPENSES:
            return -stats.expenses.balance
        if column == CashFlowTableColumn.OUTWARD_TRANSFERS:
            return -stats.outward_transfers.balance
        if column == CashFlowTableColumn.TOTAL_OUTFLOW:
            return -stats.outflows.balance
        if column == CashFlowTableColumn.DELTA_NEUTRAL:
            return stats.delta_neutral.balance
        if column == CashFlowTableColumn.DELTA_PERFORMANCE_SECURITIES:
            return stats.delta_performance_securities
        if column == CashFlowTableColumn.DELTA_PERFORMANCE_CURRENCIES:
            return stats.delta_performance_currencies
        if column == CashFlowTableColumn.DELTA_PERFORMANCE:
            return stats.delta_performance
        if column == CashFlowTableColumn.DELTA_TOTAL:
            return stats.delta_total
        raise ValueError(f"Unknown column {column}.")

    def _get_transactions_for_column(
        self, stats: CashFlowStats, column: int
    ) -> set[Transaction]:
        if column == CashFlowTableColumn.INCOME:
            return stats.incomes.transactions
        if column == CashFlowTableColumn.INWARD_TRANSFERS:
            return stats.inward_transfers.transactions
        if column == CashFlowTableColumn.REFUNDS:
            return stats.refunds.transactions
        if column == CashFlowTableColumn.TOTAL_INFLOW:
            return stats.inflows.transactions
        if column == CashFlowTableColumn.EXPENSES:
            return stats.expenses.transactions
        if column == CashFlowTableColumn.OUTWARD_TRANSFERS:
            return stats.outward_transfers.transactions
        if column == CashFlowTableColumn.TOTAL_OUTFLOW:
            return stats.outflows.transactions
        if column == CashFlowTableColumn.DELTA_NEUTRAL:
            return stats.delta_neutral.transactions
        return set()
