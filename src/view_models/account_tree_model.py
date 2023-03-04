from collections.abc import Sequence
from typing import Any, Self

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
    def __init__(self, item: Account | AccountGroup, parent: Self | None) -> None:
        self.item = item
        self.parent = parent
        self.children: list[Self] = []
        self.visible: bool = True

    def __repr__(self) -> str:
        return f"AccountTreeNode({str(self.item)})"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, AccountTreeNode):
            return False
        return self.item == __o.item


def make_nodes(
    items: Sequence[Account | AccountGroup], parent: AccountTreeNode | None
) -> Sequence[AccountTreeNode]:
    nodes = []
    for item in items:
        node = AccountTreeNode(item, parent=parent)
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
        self._root_nodes = tuple(make_nodes(root_items, None))

    def rowCount(self, index: QModelIndex = ...) -> int:
        if index.isValid():
            if index.column() != 0:
                return 0
            node: AccountTreeNode = index.internalPointer()
            return len(node.children)
        return len(self._root_nodes)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: U100
        return 4 if not index.isValid() or index.column() == 0 else 0

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        if not parent or not parent.isValid():
            _parent = None
        else:
            _parent: AccountTreeNode = parent.internalPointer()

        if _parent is None:
            child = self._root_nodes[row]
        else:
            child = _parent.children[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        node: AccountTreeNode = index.internalPointer()
        parent = node.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            parent_row = self._root_nodes.index(parent)
        else:
            parent_row = grandparent.children.index(parent)
        return QAbstractItemModel.createIndex(self, parent_row, 0, parent)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> Any:
        if not index.isValid():
            return None
        column = index.column()
        node: AccountTreeNode = index.internalPointer()
        item = node.item
        if role == Qt.ItemDataRole.DisplayRole:
            if column == AccountTreeColumns.COLUMN_NAME:
                return item.name
            if column == AccountTreeColumns.COLUMN_BALANCE_NATIVE:
                if isinstance(item, CashAccount):
                    return str(item.get_balance(item.currency))
                return ""
            if column == AccountTreeColumns.COLUMN_BALANCE_BASE:
                try:
                    if self.base_currency is None:
                        return ""
                    return item.get_balance(self.base_currency).to_str_rounded()
                except ConversionFactorNotFoundError:
                    return "Error!"
        elif (
            role == Qt.ItemDataRole.DecorationRole
            and column == AccountTreeColumns.COLUMN_NAME
        ):
            if isinstance(item, AccountGroup):
                if self._tree.isExpanded(index):
                    return QIcon("icons_16:folder-open.png")
                return QIcon("icons_16:folder.png")
            if isinstance(item, SecurityAccount):
                return QIcon("icons_16:bank.png")
            if isinstance(item, CashAccount):
                if item.get_balance(item.currency).is_positive():
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
            if item.get_balance(self.base_currency).is_negative():
                return QBrush(QColor("red"))
            if item.get_balance(self.base_currency).value_normalized == 0:
                return QBrush(QColor("gray"))
        elif (
            role == Qt.ItemDataRole.CheckStateRole
            and column == AccountTreeColumns.COLUMN_SHOW
        ):
            return Qt.CheckState.Checked if node.visible else Qt.CheckState.Unchecked

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
            return Qt.ItemFlag.NoItemFlags

        if index.column() == AccountTreeColumns.COLUMN_SHOW:
            return (
                Qt.ItemFlag.ItemIsEnabled
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsUserCheckable
            )
        return super().flags(index)

    def setData(self, index: QModelIndex, value: Any, role: Qt.ItemDataRole) -> bool:
        if (
            index.column() == AccountTreeColumns.COLUMN_SHOW
            and role == Qt.ItemDataRole.CheckStateRole
        ):
            node: AccountTreeNode = index.internalPointer()
            node.visible = value
            self.dataChanged.emit(index, index)
            return True
        return super().setData(index, value, role)

    def pre_add(self, parent: AccountGroup | None) -> None:
        parent_index = self.get_index_from_item(parent)
        if parent is None:
            row_index = len(self._root_nodes)
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
            if new_index > len(self._root_nodes):
                new_index = len(self._root_nodes)
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
        index = self.get_selected_item_index()
        node: AccountTreeNode | None = index.internalPointer()
        if node is None:
            return None
        return node.item

    def get_index_from_item(self, item: Account | AccountGroup | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        node = self._get_node_from_item(item)
        parent = node.parent
        if parent is None:
            row = self._root_nodes.index(node)
        else:
            row = parent.children.index(node)
        return QAbstractItemModel.createIndex(self, row, 0, node)

    def _get_node_from_item(self, item: Account | AccountGroup) -> AccountTreeNode:
        node = AccountTreeModel._walk_node_tree(self._root_nodes, item)
        if node is None:
            raise ValueError(f"Item {item} not present within AccountTreeModel data.")
        return node

    @staticmethod
    def _walk_node_tree(
        nodes: Sequence[AccountTreeNode], item: Account | AccountGroup
    ) -> AccountTreeNode | None:
        for node in nodes:
            if node.item == item:
                return node
            child_node = AccountTreeModel._walk_node_tree(node.children, item)
            if child_node is not None:
                return child_node
        return None
