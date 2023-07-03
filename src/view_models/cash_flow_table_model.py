from collections.abc import Sequence

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QFont
from PyQt6.QtWidgets import QTableView
from src.models.model_objects.currency_objects import CashAmount
from src.models.statistics.cashflow_stats import CashFlowStats
from src.views import colors
from src.views.constants import CashFlowTableColumn

bold_font = QFont()
bold_font.setBold(True)  # noqa: FBT003

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter

COLUMN_HEADERS = {
    CashFlowTableColumn.INCOME: "Income",
    CashFlowTableColumn.INWARD_TRANSFERS: "Inward Transfers",
    CashFlowTableColumn.REFUNDS: "Refunds",
    CashFlowTableColumn.TOTAL_INFLOW: "Total Inflow",
    CashFlowTableColumn.EXPENSES: "Expenses",
    CashFlowTableColumn.OUTWARD_TRANSFERS: "Outward Transfers",
    CashFlowTableColumn.TOTAL_OUTFLOW: "Total Outflow",
    CashFlowTableColumn.DELTA_NEUTRAL: "Cash Flow",
    CashFlowTableColumn.DELTA_PERFORMANCE: "Gain / Loss",
    CashFlowTableColumn.DELTA_TOTAL: "Net Growth",
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

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self._stats)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802, ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(COLUMN_HEADERS)
        return self._column_count

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return COLUMN_HEADERS[section]
            return self._stats[section].period
        if (
            role == Qt.ItemDataRole.TextAlignmentRole
            and orientation == Qt.Orientation.Vertical
        ):
            return ALIGNMENT_RIGHT
        if (
            role == Qt.ItemDataRole.FontRole
            and orientation == Qt.Orientation.Vertical
            and section == len(self._stats) - 1
        ):
            return bold_font
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
        if role == Qt.ItemDataRole.FontRole and index.row() == len(self._stats) - 1:
            return bold_font
        return None

    def _get_display_role_data(self, column: int, stats: CashFlowStats) -> str:
        return self._get_cash_amount_for_column(stats, column).to_str_rounded()

    def _get_user_role_data(self, column: int, stats: CashFlowStats) -> float:
        return float(self._get_cash_amount_for_column(stats, column).value_rounded)

    def _get_foreground_role_data(
        self, column: int, stats: CashFlowStats
    ) -> QBrush | None:
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

    def _get_cash_amount_for_column(
        self, stats: CashFlowStats, column: int
    ) -> CashAmount:
        if column == CashFlowTableColumn.INCOME:
            return stats.incomes
        if column == CashFlowTableColumn.INWARD_TRANSFERS:
            return stats.inward_transfers
        if column == CashFlowTableColumn.REFUNDS:
            return stats.refunds
        if column == CashFlowTableColumn.TOTAL_INFLOW:
            return stats.inflows
        if column == CashFlowTableColumn.EXPENSES:
            return -stats.expenses
        if column == CashFlowTableColumn.OUTWARD_TRANSFERS:
            return -stats.outward_transfers
        if column == CashFlowTableColumn.TOTAL_OUTFLOW:
            return -stats.outflows
        if column == CashFlowTableColumn.DELTA_NEUTRAL:
            return stats.delta_neutral
        if column == CashFlowTableColumn.DELTA_PERFORMANCE:
            return stats.delta_performance
        if column == CashFlowTableColumn.DELTA_TOTAL:
            return stats.delta_total
        raise ValueError(f"Unknown column {column}.")
