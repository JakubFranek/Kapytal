from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QFont
from PyQt6.QtWidgets import QTableView
from src.models.model_objects.attributes import Attribute
from src.models.model_objects.currency_objects import CashAmount
from src.models.statistics.attribute_stats import AttributeStats
from src.views import colors

overline_font = QFont()
overline_font.setOverline(True)  # noqa: FBT003

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


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
        periodic_totals: dict[str, CashAmount],
        attribute_averages: dict[Attribute, CashAmount],
        attribute_totals: dict[Attribute, CashAmount],
    ) -> None:
        self._rows: list[list[Decimal]] = []
        periods = list(periodic_stats.keys())
        self._column_headers = (*periods, "Average", "Σ Total")

        attributes = frozenset(
            item.attribute for stats in periodic_stats.values() for item in stats
        )
        attributes = sorted(attributes, key=lambda x: x.path)
        self._row_headers = tuple(
            [attribute.name for attribute in attributes] + ["Σ Total"]
        )
        for attribute in attributes:
            row: list[Decimal] = []
            for period in periodic_stats:
                stats = _get_attribute_stats(periodic_stats[period], attribute.name)
                if stats is not None:
                    row.append(stats.balance.value_rounded)
                else:
                    row.append(Decimal(0))
            row.append(attribute_averages[attribute].value_rounded)
            row.append(attribute_totals[attribute].value_rounded)
            self._rows.append(row)

        periodic_totals_row: list[Decimal] = []
        for period in periodic_totals:
            periodic_totals_row.append(periodic_totals[period].value_rounded)
        average_sum = sum(row[-2] for row in self._rows)
        total_sum = sum(row[-1] for row in self._rows)
        periodic_totals_row.append(average_sum)
        periodic_totals_row.append(total_sum)
        self._rows.append(periodic_totals_row)

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self._rows)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802, ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(self._column_headers)
        return self._column_count

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._column_headers[section]
            return self._row_headers[section]
        if role == Qt.ItemDataRole.FontRole:
            if (
                orientation == Qt.Orientation.Vertical
                and section == len(self._rows) - 1
            ):
                return None
            if orientation == Qt.Orientation.Horizontal:
                if section == len(self._column_headers) - 2:
                    return overline_font
                if section == len(self._column_headers) - 1:
                    return None
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | QFont | QBrush | float | int | None:
        if not index.isValid():
            return None

        row = index.row()
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            if column == len(self._column_headers) - 1 or row == len(self._rows) - 1:
                prefix = "Σ "
            else:
                prefix = ""
            return prefix + f"{self._rows[row][column]:,}"
        if role == Qt.ItemDataRole.UserRole:
            return float(self._rows[row][column])
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return ALIGNMENT_RIGHT
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(self._rows[row][column])
        if role == Qt.ItemDataRole.FontRole and column == len(self._column_headers) - 2:
            return overline_font
        return None

    def _get_foreground_role_data(self, amount: Decimal) -> QBrush | None:
        if amount > 0:
            return colors.get_green_brush()
        if amount < 0:
            return colors.get_red_brush()
        return colors.get_gray_brush()

    def pre_reset_model(self) -> None:
        self._view.setSortingEnabled(False)  # noqa: FBT003
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
        self._view.setSortingEnabled(True)  # noqa: FBT003


def _get_attribute_stats(
    stats: Collection[AttributeStats], attribute_name: str
) -> AttributeStats | None:
    for _stats in stats:
        if _stats.attribute.name == attribute_name:
            return _stats
    return None
