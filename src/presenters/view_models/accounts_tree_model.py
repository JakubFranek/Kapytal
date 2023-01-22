import typing

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QTreeView

from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.security_objects import SecurityAccount
from src.views.constants import AccountTreeColumns

# TODO: set up model checker test
# TODO: pass reference to settings?


class AccountsTreeModel(QAbstractItemModel):
    COLUMN_HEADERS = ("Name", "Balance", "Balance (base)", "Show")

    def __init__(self, view: QTreeView, data: list[Account | AccountGroup]) -> None:
        super().__init__()
        self._view = view
        self._data = data

    def rowCount(self, index: QModelIndex = ...) -> int:
        if index.isValid():
            node: Account | AccountGroup = index.internalPointer()
            if isinstance(node, AccountGroup):
                return len(node.children)
            return 0
        return len(self._data)

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
            child = self._data[row]
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
        if parent is not None:
            parent_row = parent.children.index(child)
        else:
            return QModelIndex()
        return QAbstractItemModel.createIndex(self, parent_row, 0, parent)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> typing.Any:
        if not index.isValid():
            return None
        column = index.column()
        node: Account | AccountGroup = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            if column == AccountTreeColumns.COLUMN_NAME:
                return node.name
            if column == AccountTreeColumns.COLUMN_BALANCE:
                return "0 CZK"
            if column == AccountTreeColumns.COLUMN_BALANCE_BASE:
                return "0 CZK"
            if column == AccountTreeColumns.COLUMN_SHOW:
                return "xxx"
        if role == Qt.ItemDataRole.DecorationRole and column == self.COLUMN_NAME:
            if isinstance(node, AccountGroup):
                if self._view.isExpanded(index):
                    return QIcon("icons_16:folder-horizontal-open.png")
                return QIcon("icons_16:folder-horizontal.png")
            if isinstance(node, SecurityAccount):
                return QIcon("icons_16:bank.png")
            if isinstance(node, CashAccount):
                return QIcon("icons_16:money-coin.png")
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.COLUMN_HEADERS[section]
            return str(section)
        return None
