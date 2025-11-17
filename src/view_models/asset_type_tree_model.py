import unicodedata
from collections.abc import Collection

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QIcon
from PyQt6.QtWidgets import QTreeView
from src.models.statistics.net_worth_stats import AssetStats, AssetType
from src.views import colors, icons
from src.views.constants import AssetTypeTreeColumn

ALIGNMENT_AMOUNTS = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
COLUMN_HEADERS = {
    AssetTypeTreeColumn.NAME: "Name",
    AssetTypeTreeColumn.BALANCE_NATIVE: "Native Balance",
    AssetTypeTreeColumn.BALANCE_BASE: "Base Balance",
}
COLUMNS_BALANCE = {
    AssetTypeTreeColumn.BALANCE_NATIVE,
    AssetTypeTreeColumn.BALANCE_BASE,
}


class AssetTypeTreeModel(QAbstractItemModel):
    def __init__(
        self,
        tree_view: QTreeView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._tree_view = tree_view
        self._proxy = proxy
        self._root_items = ()

    def load_data(self, collection: Collection[AssetStats]) -> None:
        self._root_items = tuple(collection)

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.isValid():
            if parent.column() != 0:
                return 0
            item: AssetStats = parent.internalPointer()
            return len(item.children)
        return len(self._root_items)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        return 3 if not parent.isValid() or parent.column() == 0 else 0

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        _parent: AssetStats | None
        if not parent or not parent.isValid():
            _parent = None
        else:
            _parent = parent.internalPointer()

        child = self._root_items[row] if _parent is None else _parent.children[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex:  # type: ignore[override]
        if not child.isValid():
            return QModelIndex()

        _child: AssetStats = child.internalPointer()
        parent = _child.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            row = self._root_items.index(parent)
        else:
            row = grandparent.children.index(parent)
        return QAbstractItemModel.createIndex(self, row, 0, parent)

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return COLUMN_HEADERS[section]
            return str(section)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        return None

    def data(
        self, index: QModelIndex, role: int = ...
    ) -> str | Qt.AlignmentFlag | None | float | QIcon | QBrush:
        if not index.isValid():
            return None

        column = index.column()
        item: AssetStats = index.internalPointer()

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(column, item)
        if role == Qt.ItemDataRole.UserRole:  # sort role
            return self._get_sort_data(column, item)
        if role == Qt.ItemDataRole.UserRole + 1:  # sort role
            return self._get_filter_data(column, item)
        if role == Qt.ItemDataRole.TextAlignmentRole and column in COLUMNS_BALANCE:
            return ALIGNMENT_AMOUNTS
        if role == Qt.ItemDataRole.DecorationRole:
            return self._get_decoration_role_data(column, item)
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(column, item)
        return None

    def _get_display_role_data(self, column: int, item: AssetStats) -> str | None:
        if column == AssetTypeTreeColumn.NAME:
            return item.name
        if column == AssetTypeTreeColumn.BALANCE_NATIVE:
            return (
                item.amount_native.to_str_rounded()
                if item.amount_native is not None
                else None
            )
        if column == AssetTypeTreeColumn.BALANCE_BASE:
            return item.amount_base.to_str_rounded()
        return None

    def _get_sort_data(self, column: int, item: AssetStats) -> float | str | None:
        if column == AssetTypeTreeColumn.NAME:
            return unicodedata.normalize("NFD", item.name)
        if column == AssetTypeTreeColumn.BALANCE_NATIVE:
            return (
                float(item.amount_native.value_normalized)
                if item.amount_native is not None
                else None
            )
        if column == AssetTypeTreeColumn.BALANCE_BASE:
            return float(item.amount_base.value_rounded)
        return None

    def _get_filter_data(self, column: int, item: AssetStats) -> str | None:
        if column == AssetTypeTreeColumn.NAME:
            return unicodedata.normalize("NFD", item.path)
        return None

    def _get_decoration_role_data(self, column: int, item: AssetStats) -> QIcon | None:
        if column != AssetTypeTreeColumn.NAME:
            return None
        if item.asset_type == AssetType.CURRENCY:
            return icons.currency
        if item.asset_type == AssetType.SECURITY:
            return (
                icons.securities
                if item.parent is None or item.parent.parent is None
                else icons.security
            )
        if item.asset_type == AssetType.ACCOUNT:
            return (
                icons.security_account
                if item.parent.asset_type == AssetType.SECURITY
                else icons.cash_account
            )
        return None

    def _get_foreground_role_data(self, column: int, item: AssetStats) -> QBrush | None:
        if column == AssetTypeTreeColumn.BALANCE_NATIVE:
            if item.amount_native is None:
                return None
            if item.amount_native.is_negative():
                return colors.get_red_brush()
        if (
            column == AssetTypeTreeColumn.BALANCE_BASE
            and item.amount_base.is_negative()
        ):
            return colors.get_red_brush()
        return None

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def get_index_from_item(self, item: AssetStats | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        parent = item.parent
        if parent is None:
            row = self._root_items.index(item)
        else:
            row = parent.children.index(item)
        return QAbstractItemModel.createIndex(self, row, 0, item)
