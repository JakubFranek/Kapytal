from collections.abc import Collection
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Self

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QFont
from PyQt6.QtWidgets import QTableView
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.attributes import Attribute
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.statistics.attribute_stats import AttributeStats
from src.models.statistics.common_classes import TransactionBalance
from src.views import colors

overline_font = QFont()
overline_font.setOverline(True)
bold_font = QFont()
bold_font.setBold(True)
overline_bold_font = QFont()
overline_bold_font.setOverline(True)
overline_bold_font.setBold(True)

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


@dataclass
class Cell:
    value: Decimal
    transactions: set[CashTransaction | RefundTransaction] = field(default_factory=set)

    def __add__(self, other: Self) -> Self:
        if other == 0:
            return self
        return Cell(
            self.value + other.value,
            self.transactions.union(other.transactions),
        )


class PeriodicAttributeStatsTableModel(QAbstractTableModel):
    def __init__(
        self,
        view: QTableView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self._proxy = proxy

    def load_periodic_attribute_stats(
        self,
        periodic_stats: dict[str, tuple[AttributeStats]],
        periodic_totals: dict[str, TransactionBalance],
        attribute_averages: dict[Attribute, TransactionBalance],
        attribute_totals: dict[Attribute, TransactionBalance],
    ) -> None:
        self._rows: list[list[Cell]] = []
        periods = list(periodic_stats.keys())
        self._column_headers = (*periods, "Average", "Σ Total")

        attributes = frozenset(
            item.attribute for stats in periodic_stats.values() for item in stats
        )
        attributes = sorted(attributes, key=lambda x: x.name)
        self._row_headers = tuple(
            [attribute.name for attribute in attributes] + ["Σ Total"]
        )
        for attribute in attributes:
            row: list[Cell] = []
            for stats in periodic_stats.values():
                stat = _get_attribute_stats(stats, attribute.name)
                if stat is not None:
                    row.append(Cell(stat.balance.value_rounded, stat.transactions))
                else:
                    row.append(Cell(Decimal(0)))
            row.append(
                Cell(
                    attribute_averages[attribute].balance.value_rounded,
                    attribute_averages[attribute].transactions,
                )
            )
            row.append(
                Cell(
                    attribute_totals[attribute].balance.value_rounded,
                    attribute_totals[attribute].transactions,
                )
            )
            self._rows.append(row)

        periodic_totals_row = [
            Cell(
                periodic_totals[period].balance.value_rounded,
                periodic_totals[period].transactions,
            )
            for period in periodic_totals
        ]
        average_sum = sum((row[-2] for row in self._rows), Cell(Decimal(0)))
        total_sum = sum((row[-1] for row in self._rows), Cell(Decimal(0)))
        periodic_totals_row.append(average_sum)
        periodic_totals_row.append(total_sum)
        self._rows.append(periodic_totals_row)

        self.TOTAL_COLUMN_INDEX = len(self._column_headers) - 1
        self.AVERAGE_COLUMN_INDEX = len(self._column_headers) - 2
        self.TOTAL_ROW_INDEX = len(self._row_headers) - 1

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if isinstance(parent, QModelIndex) and parent.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, parent: QModelIndex = ...) -> int:  # noqa: ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(self._column_headers)
        return self._column_count

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._column_headers[section]
            return self._row_headers[section]
        if role == Qt.ItemDataRole.FontRole:
            if (
                orientation == Qt.Orientation.Vertical
                and section == self.TOTAL_ROW_INDEX
            ):
                return bold_font
            if orientation == Qt.Orientation.Horizontal:
                if section == self.AVERAGE_COLUMN_INDEX:
                    return overline_font
                if section == self.TOTAL_COLUMN_INDEX:
                    return bold_font
        return None

    def data(
        self, index: QModelIndex, role: int = ...
    ) -> str | Qt.AlignmentFlag | QFont | QBrush | float | int | None:
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(row, column)
        if role == Qt.ItemDataRole.UserRole:
            return float(self._rows[row][column].value)
        if role == Qt.ItemDataRole.UserRole + 1:
            return self._row_headers[row]
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return ALIGNMENT_RIGHT
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(self._rows[row][column].value)
        if role == Qt.ItemDataRole.FontRole:
            return self._get_font_role_data(row, column)
        return None

    def _get_display_role_data(self, row: int, column: int) -> str | None:
        if column == self.TOTAL_COLUMN_INDEX or row == self.TOTAL_ROW_INDEX:
            prefix = "Σ "
        else:
            prefix = ""
        return prefix + f"{self._rows[row][column].value:n}"

    def _get_foreground_role_data(self, amount: Decimal) -> QBrush | None:
        if amount > 0:
            return colors.get_green_brush()
        if amount < 0:
            return colors.get_red_brush()
        return colors.get_gray_brush()

    def _get_font_role_data(self, row: int, column: int) -> QFont | None:
        if row == self.TOTAL_ROW_INDEX:
            if column == self.AVERAGE_COLUMN_INDEX:
                return overline_bold_font
            return bold_font
        if column == self.TOTAL_COLUMN_INDEX:
            return bold_font
        if column == self.AVERAGE_COLUMN_INDEX:
            return overline_font
        return None

    def pre_reset_model(self) -> None:
        self._view.setSortingEnabled(False)
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
        self._view.setSortingEnabled(True)

    def get_selected_transactions(
        self,
    ) -> tuple[tuple[CashTransaction | RefundTransaction, ...], str, str]:
        """Returns a tuple of selected Transactions, period and name."""
        indexes = self._view.selectedIndexes()
        if len(indexes) != 1:
            raise InvalidOperationError(
                "Transactions can be shown for only for exactly one Attribute."
            )
        index = indexes[0]
        if self._proxy:
            index = self._proxy.mapToSource(index)

        cell: Cell = self._rows[index.row()][index.column()]
        return (
            tuple(cell.transactions),
            self._column_headers[index.column()],
            self._row_headers[index.row()],
        )


def _get_attribute_stats(
    stats: Collection[AttributeStats], attribute_name: str
) -> AttributeStats | None:
    for _stats in stats:
        if _stats.attribute.name == attribute_name:
            return _stats
    return None
