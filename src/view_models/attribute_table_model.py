import unicodedata
from collections.abc import Collection

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush
from PyQt6.QtWidgets import QTableView
from src.models.base_classes.transaction import Transaction
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.attributes import Attribute
from src.models.statistics.attribute_stats import AttributeStats
from src.views import colors
from src.views.constants import AttributeTableColumn

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
COLUMN_HEADERS = {
    AttributeTableColumn.NAME: "Name",
    AttributeTableColumn.TRANSACTIONS: "Transactions",
    AttributeTableColumn.BALANCE: "Balance",
}
COLUMNS_NUMBERS = {
    AttributeTableColumn.TRANSACTIONS,
    AttributeTableColumn.BALANCE,
}


class AttributeTableModel(QAbstractTableModel):
    def __init__(
        self,
        view: QTableView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self._attribute_stats: tuple[AttributeStats, ...] = ()
        self._proxy = proxy

    @property
    def attribute_stats(self) -> tuple[AttributeStats, ...]:
        return self._attribute_stats

    def load_attribute_stats(self, stats: Collection[AttributeStats]) -> None:
        self._attribute_stats = tuple(stats)

    def rowCount(self, index: QModelIndex | None = None) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self._attribute_stats)

    def columnCount(self, index: QModelIndex | None = None) -> int:  # noqa: ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(COLUMN_HEADERS)
        return self._column_count

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return COLUMN_HEADERS[section]
            return str(section)
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole
    ) -> str | int | float | Qt.AlignmentFlag | QBrush | None:
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(
                index.column(), self._attribute_stats[index.row()]
            )
        if role == Qt.ItemDataRole.UserRole:
            return self._get_sort_role_data(
                index.column(), self._attribute_stats[index.row()]
            )
        column = index.column()
        if role == Qt.ItemDataRole.TextAlignmentRole and column in COLUMNS_NUMBERS:
            return ALIGNMENT_RIGHT
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(
                column, self._attribute_stats[index.row()]
            )
        return None

    def _get_display_role_data(
        self, column: int, stats: AttributeStats
    ) -> str | int | None:
        if column == AttributeTableColumn.NAME:
            return stats.attribute.name
        if column == AttributeTableColumn.TRANSACTIONS:
            return stats.no_of_transactions
        if column == AttributeTableColumn.BALANCE:
            return stats.balance.to_str_rounded() if stats.balance is not None else None
        return None

    def _get_sort_role_data(
        self, column: int, stats: AttributeStats
    ) -> str | int | float | None:
        if column == AttributeTableColumn.NAME:
            return unicodedata.normalize("NFD", stats.attribute.name)
        if column == AttributeTableColumn.TRANSACTIONS:
            return stats.no_of_transactions
        if column == AttributeTableColumn.BALANCE:
            return (
                float(stats.balance.value_normalized)
                if stats.balance is not None
                else None
            )
        return None

    def _get_foreground_role_data(
        self, column: int, stats: AttributeStats
    ) -> QBrush | None:
        if column != AttributeTableColumn.BALANCE:
            return None
        if stats.balance is None:
            return None
        if stats.balance.is_positive():
            return colors.get_green_brush()
        if stats.balance.is_negative():
            return colors.get_red_brush()
        return colors.get_gray_brush()

    def pre_add(self) -> None:
        self._proxy.setDynamicSortFilter(False)
        self._view.setSortingEnabled(False)
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

    def post_add(self) -> None:
        self.endInsertRows()
        self._view.setSortingEnabled(True)
        self._proxy.setDynamicSortFilter(True)

    def pre_reset_model(self) -> None:
        self._view.setSortingEnabled(False)
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
        self._view.setSortingEnabled(True)

    def pre_remove_item(self, item: Attribute) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def get_selected_attributes(self) -> tuple[Attribute, ...]:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        return tuple(
            self._attribute_stats[index.row()].attribute
            for index in source_indexes
            if index.column() == 0
        )

    def get_selected_attribute_transactions(self) -> set[Transaction]:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        source_indexes = [index for index in source_indexes if index.column() == 0]
        if len(source_indexes) != 1:
            raise InvalidOperationError(
                "Transactions can be shown for only for exactly one Attribute."
            )
        index = source_indexes[0]
        return self._attribute_stats[index.row()].transactions

    def get_index_from_item(self, item: Attribute | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        for index, stats in enumerate(self._attribute_stats):
            if stats.attribute == item:
                row = index
                break
        else:
            raise ValueError(
                f"Parameter {item=} not in AttributeTableModel.attribute_stats."
            )
        return QAbstractTableModel.createIndex(self, row, 0)

    def item_changed(self, item: Attribute) -> None:
        index = self.get_index_from_item(item)
        self.dataChanged.emit(index, index)
