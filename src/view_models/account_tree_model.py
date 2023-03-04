from collections.abc import Sequence
from typing import Any

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtGui import QBrush, QColor, QIcon
from PyQt6.QtWidgets import QTreeView

from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency_objects import (
    ConversionFactorNotFoundError,
    Currency,
)
from src.models.model_objects.security_objects import SecurityAccount
from src.views.constants import AccountTreeColumns


class AccountTreeNode:
    def __init__(
        self, item: Account | AccountGroup, parent: AccountGroup | None
    ) -> None:
        self.item = item
        self.parent = parent
        self.children = []
        self.visible = True

    def __repr__(self) -> str:
        return f"AccountTreeNode({str(self.item)})"


def make_nodes(
    items: Sequence[Account | AccountGroup], parent: AccountGroup | None
) -> Sequence[AccountTreeNode]:
    nodes = []
    for item in items:
        node = AccountTreeNode(item, parent=None)
        if isinstance(item, AccountGroup):
            node.children = make_nodes(item.children, node)
        nodes.append(node)

    return nodes


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
        root_items: Sequence[Account | AccountGroup],
        base_currency: Currency,
    ) -> None:
        super().__init__()
        self._tree = view
        self.root_items = root_items
        self.base_currency = base_currency

    @property
    def root_items(self) -> tuple[Account | AccountGroup, ...]:
        return self._root_items

    @root_items.setter
    def root_items(self, root_items: Sequence[Account | AccountGroup]) -> None:
        self._root_items = tuple(root_items)
        self.root_nodes = make_nodes(root_items, None)

    def rowCount(self, index: QModelIndex = ...) -> int:
        if index.isValid():
            if index.column() != 0:
                return 0
            node: Account | AccountGroup = index.internalPointer()
            if isinstance(node, AccountGroup):
                return len(node.children)
            return 0
        return len(self.root_items)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: U100
        return 4 if not index.isValid() or index.column() == 0 else 0

    def index(self, row: int, column: int, _parent: QModelIndex = ...) -> QModelIndex:
        if _parent.isValid() and _parent.column() != 0:
            return QModelIndex()

        if not _parent or not _parent.isValid():
            parent = None
        else:
            parent: AccountGroup = _parent.internalPointer()

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

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> Any:
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
                    if self.base_currency is None:
                        return ""
                    return node.get_balance(self.base_currency).to_str_rounded()
                except ConversionFactorNotFoundError:
                    return "Error!"
        elif (
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
                if node.get_balance(node.currency).is_positive():
                    return QIcon("icons_16:piggy-bank.png")
                return QIcon("icons_16:piggy-bank-empty.png")
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if column == AccountTreeColumns.COLUMN_BALANCE_NATIVE:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            if column == AccountTreeColumns.COLUMN_BALANCE_BASE:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        elif role == Qt.ItemDataRole.ForegroundRole and (
            column == AccountTreeColumns.COLUMN_BALANCE_NATIVE
            or column == AccountTreeColumns.COLUMN_BALANCE_BASE
        ):
            if node.get_balance(self.base_currency).is_negative():
                return QBrush(QColor("red"))
            if node.get_balance(self.base_currency).value_normalized == 0:
                return QBrush(QColor("gray"))
        elif (
            role == Qt.ItemDataRole.CheckStateRole
            and column == AccountTreeColumns.COLUMN_SHOW
        ):
            return Qt.CheckState.Checked

        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if section == AccountTreeColumns.COLUMN_BALANCE_NATIVE:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            if section == AccountTreeColumns.COLUMN_BALANCE_BASE:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            if section == AccountTreeColumns.COLUMN_SHOW:
                return Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignHCenter
        elif role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.COLUMN_HEADERS[section]
            return str(section)
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return None

        if index.column() == AccountTreeColumns.COLUMN_SHOW:
            return (
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsUserCheckable
            )
        return super().flags(index)

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole) -> bool:
        return super().setData()

    def pre_add(self, parent: AccountGroup | None) -> None:
        parent_index = self.get_index_from_item(parent)
        if parent is None:
            row_index = len(self.root_items)
        else:
            row_index = len(parent.children)
        self.beginInsertRows(parent_index, row_index, row_index)

    def post_add(self) -> None:
        self.endInsertRows()

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def pre_remove_item(self, item: Account | AccountGroup) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(index.parent(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def pre_move_item(
        self,
        previous_parent: AccountGroup | None,
        previous_index: int,
        new_parent: AccountGroup | None,
        new_index: int,
    ) -> None:
        previous_parent_index = self.get_index_from_item(previous_parent)
        new_parent_index = self.get_index_from_item(new_parent)
        # Index must be limited to valid indexes
        if new_parent is None:
            if new_index > len(self.root_items):
                new_index = len(self.root_items)
        else:
            if new_index > len(new_parent.children):
                new_index = len(new_parent.children)
        if previous_parent == new_parent and new_index > previous_index:
            new_index += 1
        self.beginMoveRows(
            previous_parent_index,
            previous_index,
            previous_index,
            new_parent_index,
            new_index,
        )

    def post_move_item(self) -> None:
        self.endMoveRows()

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
