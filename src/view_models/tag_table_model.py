import unicodedata
from collections.abc import Collection

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QTableView
from src.models.model_objects.attributes import Attribute
from src.models.utilities.calculation import AttributeStats
from src.views.constants import TagTableColumn

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class TagTableModel(QAbstractTableModel):
    COLUMN_HEADERS = {
        TagTableColumn.NAME: "Name",
        TagTableColumn.TRANSACTIONS: "Transactions",
        TagTableColumn.BALANCE: "Balance",
    }

    def __init__(
        self,
        view: QTableView,
        tag_stats: Collection[  # TODO: get rid of these parameters across all view models
            AttributeStats
        ],
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self.tag_stats = tag_stats
        self._proxy = proxy

    @property
    def tag_stats(self) -> tuple[AttributeStats, ...]:
        return self._tag_stats

    @tag_stats.setter
    def tag_stats(self, tag_stats: Collection[AttributeStats]) -> None:
        self._tag_stats = tuple(tag_stats)

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self._tag_stats)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802, ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(self.COLUMN_HEADERS)
        return self._column_count

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | int | float | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(
                index.column(), self._tag_stats[index.row()]
            )
        if role == Qt.ItemDataRole.UserRole:
            return self._get_user_role_data(
                index.column(), self._tag_stats[index.row()]
            )
        column = index.column()
        if role == Qt.ItemDataRole.TextAlignmentRole and (
            column == TagTableColumn.TRANSACTIONS or column == TagTableColumn.BALANCE
        ):
            return ALIGNMENT_RIGHT
        return None

    def _get_display_role_data(
        self, column: int, tag_stats: AttributeStats
    ) -> str | int | None:
        if column == TagTableColumn.NAME:
            return tag_stats.attribute.name
        if column == TagTableColumn.TRANSACTIONS:
            return tag_stats.no_of_transactions
        if column == TagTableColumn.BALANCE:
            return tag_stats.balance.to_str_rounded()
        return None

    def _get_user_role_data(
        self, column: int, tag_stats: AttributeStats
    ) -> str | int | float | None:
        if column == TagTableColumn.NAME:
            return unicodedata.normalize("NFD", tag_stats.attribute.name)
        if column == TagTableColumn.TRANSACTIONS:
            return tag_stats.no_of_transactions
        if column == TagTableColumn.BALANCE:
            return float(tag_stats.balance.value_normalized)
        return None

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.COLUMN_HEADERS[section]
            return str(section)
        return None

    def pre_add(self) -> None:
        self._proxy.setDynamicSortFilter(False)  # noqa: FBT003
        self._view.setSortingEnabled(False)  # noqa: FBT003
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

    def post_add(self) -> None:
        self.endInsertRows()
        self._view.setSortingEnabled(True)  # noqa: FBT003
        self._proxy.setDynamicSortFilter(True)  # noqa: FBT003

    def pre_reset_model(self) -> None:
        self._view.setSortingEnabled(False)  # noqa: FBT003
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
        self._view.setSortingEnabled(True)  # noqa: FBT003

    def pre_remove_item(self, item: Attribute) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def get_selected_items(self) -> tuple[Attribute]:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        return tuple(
            self._tag_stats[index.row()].attribute
            for index in source_indexes
            if index.column() == 0
        )

    def get_index_from_item(self, item: Attribute | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        for index, tag_stats in enumerate(self._tag_stats):
            if tag_stats.attribute == item:
                row = index
                break
        else:
            raise ValueError(f"Parameter {item=} not in TagTableModel.tag_stats.")
        return QAbstractTableModel.createIndex(self, row, 0)
