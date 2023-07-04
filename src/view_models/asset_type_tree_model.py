import unicodedata
from collections.abc import Collection
from decimal import Decimal

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QBrush, QIcon
from PyQt6.QtWidgets import QTreeView
from src.models.statistics.net_worth_stats import AssetStats, RootAssetType
from src.views import colors, icons
from src.views.constants import AssetTypeTreeColumn

ALIGNMENT_AMOUNTS = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
COLUMN_HEADERS = {
    AssetTypeTreeColumn.NAME: "Name",
    AssetTypeTreeColumn.BALANCE_NATIVE: "Native balance",
    AssetTypeTreeColumn.BALANCE_BASE: "Base balance",
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
        self._tree_items = ()

    def load_data(self, collection: Collection[AssetStats]) -> None:
        self._tree_items = collection

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if index.isValid():
            if index.column() != 0:
                return 0
            item: AssetStats = index.internalPointer()
            return len(item.children)
        return len(self._tree_items)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        return 3 if not index.isValid() or index.column() == 0 else 0

    def index(self, row: int, column: int, _parent: QModelIndex = ...) -> QModelIndex:
        if _parent.isValid() and _parent.column() != 0:
            return QModelIndex()

        if not _parent or not _parent.isValid():
            parent = None
        else:
            parent: AssetStats = _parent.internalPointer()

        child = self._tree_items[row] if parent is None else parent.children[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child: AssetStats = index.internalPointer()
        parent = child.parent
        if parent is None:
            return QModelIndex()
        row = self._tree_items.index(parent)
        return QAbstractItemModel.createIndex(self, row, 0, parent)

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return COLUMN_HEADERS[section]
            return str(section)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None
        column = index.column()
        item: AssetStats = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(column, item)
        if role == Qt.ItemDataRole.UserRole:  # sort role
            return self._get_sort_data(column, item)
        if role == Qt.ItemDataRole.TextAlignmentRole and (
            column == AssetTypeTreeColumn.BALANCE_NATIVE
            or column == AssetTypeTreeColumn.BALANCE_BASE
        ):
            return ALIGNMENT_AMOUNTS
        if role == Qt.ItemDataRole.DecorationRole:
            return self._get_decoration_role_data(column, item)
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(column, item)
        return None

    def _get_display_role_data(
        self, column: int, item: AssetStats
    ) -> str | Decimal | None:
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

    def _get_sort_data(self, column: int, item: AssetStats) -> str | Decimal | None:
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

    def _get_decoration_role_data(self, column: int, item: AssetStats) -> QIcon | None:
        if column != AssetTypeTreeColumn.NAME:
            return None
        if item.root_asset_type == RootAssetType.CURRENCY:
            return QIcon(icons.currency)
        if item.root_asset_type == RootAssetType.SECURITY:
            return QIcon(icons.security)
        return None

    def _get_foreground_role_data(self, column: int, item: AssetStats) -> QBrush | None:
        if column == AssetTypeTreeColumn.BALANCE_NATIVE:
            if item.amount_native is None:
                return None
            if item.amount_native.is_negative():
                return colors.get_red_brush()
            if item.amount_native.value_normalized == 0:
                return colors.get_gray_brush()
        if column == AssetTypeTreeColumn.BALANCE_BASE:
            if item.amount_base.is_negative():
                return colors.get_red_brush()
            if item.amount_base.value_normalized == 0:
                return colors.get_gray_brush()
        return None

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
