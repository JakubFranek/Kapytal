import typing

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTreeView

from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency_objects import Currency
from src.models.model_objects.security_objects import SecurityAccount
from src.views.constants import AccountTreeColumns

# TODO: set up model checker test
# TODO: pass reference to settings?
# TODO: save expand state before reset and load after it


class AccountTreeModel(QAbstractItemModel):
    COLUMN_HEADERS = {
        AccountTreeColumns.COLUMN_NAME: "Name",
        AccountTreeColumns.COLUMN_BALANCE_NATIVE: "Native balance",
        AccountTreeColumns.COLUMN_BALANCE_BASE: "Base balance",
        AccountTreeColumns.COLUMN_SHOW: "Show",
    }

    def __init__(
        self,
        view: QTreeView,
        root_items: list[Account | AccountGroup],
        base_currency: Currency,
    ) -> None:
        super().__init__()
        self._tree = view
        self.root_items = root_items
        self.base_currency = base_currency

    def rowCount(self, index: QModelIndex = ...) -> int:
        if index.isValid():
            node: Account | AccountGroup = index.internalPointer()
            if isinstance(node, AccountGroup):
                return len(node.children)
            return 0
        return len(self.root_items)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: U100
        return 4

    def index(self, row: int, column: int, _parent: QModelIndex = ...) -> QModelIndex:
        if not _parent or not _parent.isValid():
            parent = None
        else:
            parent: Account | AccountGroup = _parent.internalPointer()

        if not QAbstractItemModel.hasIndex(self, row, column, _parent):
            return QModelIndex()

        if parent is None:
            child = self.root_items[row]
        else:
            child = parent.children[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child: AccountGroup = index.internalPointer()
        parent = child.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            parent_row = self.root_items.index(parent)
        else:
            parent_row = grandparent.children.index(parent)
        return QAbstractItemModel.createIndex(self, parent_row, 0, parent)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> typing.Any:
        if not index.isValid():
            return None
        column = index.column()
        node: Account | AccountGroup = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            if column == AccountTreeColumns.COLUMN_NAME:
                return node.name
            if column == AccountTreeColumns.COLUMN_BALANCE_NATIVE:
                if isinstance(node, CashAccount):
                    return str(node.get_balance(node.currency))
                return ""
            if column == AccountTreeColumns.COLUMN_BALANCE_BASE:
                try:
                    return str(node.get_balance(self.base_currency))
                except Exception:
                    return "Error!"
            if column == AccountTreeColumns.COLUMN_SHOW:
                return "xxx"
        if (
            role == Qt.ItemDataRole.DecorationRole
            and column == AccountTreeColumns.COLUMN_NAME
        ):
            if isinstance(node, AccountGroup):
                if self._tree.isExpanded(index):
                    return QIcon("icons_16:folder-open.png")
                return QIcon("icons_16:folder.png")
            if isinstance(node, SecurityAccount):
                return QIcon("icons_16:bank.png")
            if isinstance(node, CashAccount):
                return QIcon("icons_16:money-coin.png")
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == AccountTreeColumns.COLUMN_BALANCE_NATIVE:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            if column == AccountTreeColumns.COLUMN_BALANCE_BASE:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            if column == AccountTreeColumns.COLUMN_SHOW:
                return Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.COLUMN_HEADERS[section]
            return str(section)
        return None

    def pre_add(self, parent: AccountGroup | None) -> None:
        parent_index = self.get_index_from_item(parent)
        if parent is None:
            row_index = len(self.root_items)
        else:
            row_index = len(parent.children)
        self.beginInsertRows(parent_index, row_index, row_index)

    def post_add(self) -> None:
        self.endInsertRows()

    def pre_new_list(self) -> None:
        self.beginResetModel()

    def post_new_list(self) -> None:
        self.endResetModel()

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def pre_delete_item(self, index: QModelIndex) -> None:
        self.beginRemoveRows(index.parent(), index.row(), index.row())

    def post_delete_item(self) -> None:
        self.endRemoveRows()

    def get_selected_item_index(self) -> QModelIndex:
        indexes = self._tree.selectedIndexes()
        if len(indexes) == 0:
            return QModelIndex()
        return indexes[0]

    def get_selected_item(self) -> Account | AccountGroup | None:
        indexes = self._tree.selectedIndexes()
        if len(indexes) == 0:
            return None
        return indexes[0].internalPointer()

    def get_index_from_item(self, item: Account | AccountGroup | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        parent = item.parent
        if parent is None:
            row = self.root_items.index(item)
        else:
            row = parent.children.index(item)
        return QAbstractItemModel.createIndex(self, row, 0, item)
