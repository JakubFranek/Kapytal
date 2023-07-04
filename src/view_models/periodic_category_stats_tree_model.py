import unicodedata
from collections.abc import Collection, Sequence
from decimal import Decimal
from typing import Self

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QFont
from PyQt6.QtWidgets import QTreeView
from src.models.model_objects.attributes import Category
from src.models.model_objects.currency_objects import CashAmount
from src.models.statistics.category_stats import CategoryStats
from src.views import colors

overline_font = QFont()
overline_font.setOverline(True)  # noqa: FBT003

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
ALIGNMENT_CENTER = Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
ALIGNMENT_LEFT = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter


class RowObject:
    def __init__(
        self, name: str, path: str, data: Sequence[Decimal], parent: Self | None
    ) -> None:
        self.name = name
        self.path = path
        self.data = tuple(data)
        self.parent = parent
        self.children: list[Self] = []

    def __repr__(self) -> str:
        return f"RowObject({self.name})"


class PeriodicCategoryStatsTreeModel(QAbstractItemModel):
    def __init__(
        self,
        view: QTreeView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self._proxy = proxy

    def load_periodic_category_stats(
        self,
        periodic_stats: dict[str, tuple[CategoryStats]],
        periodic_totals: dict[str, CashAmount],
        category_averages: dict[Category, CashAmount],
        category_totals: dict[Category, CashAmount],
    ) -> None:
        self._root_row_objects: list[RowObject] = []
        self._flat_row_objects: list[RowObject] = []
        periods = list(periodic_stats.keys())
        self._column_headers = ("Category", *periods, "Average", "Σ Total")

        categories = frozenset(
            item.category for stats in periodic_stats.values() for item in stats
        )
        categories = sorted(categories, key=lambda x: x.path)
        self._row_headers = tuple(
            [category.path for category in categories if category.parent is None]
            + ["Σ Total"]
        )
        for category in categories:
            row_data: list[Decimal] = []
            for period in periodic_stats:
                stats = _get_category_stats(periodic_stats[period], category.path)
                if stats is not None:
                    row_data.append(stats.balance.value_rounded)
                else:
                    row_data.append(Decimal(0))
            row_data.append(category_averages[category].value_rounded)
            row_data.append(category_totals[category].value_rounded)

            if category.parent is None:
                row_object = RowObject(category.name, category.path, row_data, None)
                self._root_row_objects.append(row_object)
            else:
                parent_row = _get_row_object_by_path(
                    self._flat_row_objects, category.parent.path
                )
                row_object = RowObject(
                    category.name, category.path, row_data, parent_row
                )
                parent_row.children.append(row_object)
            self._flat_row_objects.append(row_object)

        periodic_totals_row: list[Decimal] = []
        for period in periodic_totals:
            periodic_totals_row.append(periodic_totals[period].value_rounded)
        average_sum = sum(row.data[-2] for row in self._root_row_objects)
        total_sum = sum(row.data[-1] for row in self._root_row_objects)
        periodic_totals_row.append(average_sum)
        periodic_totals_row.append(total_sum)
        self._root_row_objects.append(
            RowObject("Σ Total", "Σ Total", periodic_totals_row, None)
        )

        self.TOTAL_COLUMN_INDEX = len(self._column_headers) - 1
        self.AVERAGE_COLUMN_INDEX = len(self._column_headers) - 2
        self.TOTAL_ROW_INDEX = len(self._row_headers) - 1

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if index.isValid():
            if index.column() != 0:
                return 0
            item: RowObject = index.internalPointer()
            return len(item.children)
        return len(self._root_row_objects)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802, ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(self._column_headers)
        return self._column_count

    def index(self, row: int, column: int, _parent: QModelIndex = ...) -> QModelIndex:
        if _parent.isValid() and _parent.column() != 0:
            return QModelIndex()

        if not _parent or not _parent.isValid():
            parent = None
        else:
            parent: RowObject = _parent.internalPointer()

        child = self._root_row_objects[row] if parent is None else parent.children[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child: RowObject = index.internalPointer()
        parent = child.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            row = self._root_row_objects.index(parent)
        else:
            row = grandparent.children.index(parent)
        return QAbstractItemModel.createIndex(self, row, 0, parent)

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._column_headers[section]
            return self._row_headers[section]
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return ALIGNMENT_CENTER
        if (
            role == Qt.ItemDataRole.FontRole
            and orientation == Qt.Orientation.Horizontal
            and section == self.AVERAGE_COLUMN_INDEX
        ):
            return overline_font
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | QFont | QBrush | float | int | None:
        if not index.isValid():
            return None

        row_object: RowObject = index.internalPointer()
        row = index.row()
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(row, column, row_object)
        if role == Qt.ItemDataRole.UserRole:
            if column == 0:
                return unicodedata.normalize("NFD", row_object.name)
            return float(row_object.data[column - 1])
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == 0:
                return ALIGNMENT_LEFT
            return ALIGNMENT_RIGHT
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(column, row_object.data[column - 1])
        if role == Qt.ItemDataRole.FontRole and column == self.AVERAGE_COLUMN_INDEX:
            return overline_font
        return None

    def _get_display_role_data(
        self, row: int, column: int, row_object: RowObject
    ) -> str | None:
        if column == 0:
            return row_object.name
        if column == self.TOTAL_COLUMN_INDEX or row == self.TOTAL_ROW_INDEX:
            prefix = "Σ "
        else:
            prefix = ""
        return prefix + f"{row_object.data[column-1]:,}"

    def _get_foreground_role_data(self, column: int, amount: Decimal) -> QBrush | None:
        if column == 0:
            return None
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


def _get_category_stats(
    stats: Collection[CategoryStats], category_path: str
) -> CategoryStats | None:
    for category_stats in stats:
        if category_stats.category.path == category_path:
            return category_stats
    return None


def _get_row_object_by_path(rows: Collection[RowObject], path: str) -> RowObject:
    for row in rows:
        if row.path == path:
            return row
    raise ValueError(f"RowObject for {path=} not found")
