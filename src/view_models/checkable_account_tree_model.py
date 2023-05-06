from collections.abc import Collection, Sequence
from copy import copy
from typing import Any, Self

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QTreeView
from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.security_objects import SecurityAccount
from src.presenters.utilities.event import Event
from src.views import icons


def convert_bool_to_checkstate(*, checked: bool) -> Qt.CheckState:
    return Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked


class AccountTreeNode:
    def __init__(self, item: Account | AccountGroup, parent: Self | None) -> None:
        self.item = item
        self.parent = parent
        self.children: list[Self] = []
        self.check_state: Qt.CheckState = Qt.CheckState.Checked
        self.event_signal_changed = Event()

    def __repr__(self) -> str:
        return f"AccountTreeNode({str(self.item)}, {self.check_state.name})"

    def set_check_state(
        self,
        *,
        checked: bool,
    ) -> None:
        """Sets check state of this node and its children, and updates the parents."""
        check_state = convert_bool_to_checkstate(checked=checked)
        self._set_check_state_recursive(check_state)
        if self.parent is not None:
            self.parent.update_check_state()

    def _set_check_state(self, check_state: Qt.CheckState) -> None:
        if check_state != self.check_state:
            self.check_state = check_state
            self.event_signal_changed(self.item.path)

    def _set_check_state_recursive(self, check_state: Qt.CheckState) -> None:
        self._set_check_state(check_state)
        for child in self.children:
            child._set_check_state_recursive(check_state)  # noqa: SLF001

    def update_check_state(self) -> None:
        """Updates check state of this node and its parents."""
        if all(child.check_state == Qt.CheckState.Checked for child in self.children):
            self._set_check_state(Qt.CheckState.Checked)
        elif all(
            child.check_state == Qt.CheckState.Unchecked for child in self.children
        ):
            self._set_check_state(Qt.CheckState.Unchecked)
        else:
            self._set_check_state(Qt.CheckState.PartiallyChecked)

        if self.parent is not None:
            self.parent.update_check_state()


def sync_nodes(
    items: Sequence[Account | AccountGroup], nodes: Sequence[AccountTreeNode]
) -> list[AccountTreeNode]:
    """Accepts flat sequences of items and nodes. Returns new flat nodes."""

    nodes_copy = list(copy(nodes))
    new_nodes: list[AccountTreeNode] = []

    for item in items:
        node = get_node(item, nodes_copy)
        parent_node = (
            get_node(item.parent, nodes_copy) if item.parent is not None else None
        )
        if node is None:
            node = AccountTreeNode(item, None)
        else:
            node.item = item
        node.parent = parent_node
        node.children = []
        if parent_node is not None:
            parent_node.children.append(node)
        if node not in nodes_copy:
            nodes_copy.append(node)
        new_nodes.append(node)

    return new_nodes


def get_node(
    item: Account | AccountGroup, nodes: Sequence[AccountTreeNode]
) -> AccountTreeNode | None:
    for node in nodes:
        if node.item == item:
            return node
    return None


def get_node_by_item_path(
    item_path: str, nodes: Sequence[AccountTreeNode]
) -> AccountTreeNode | None:
    for node in nodes:
        if node.item.path == item_path:
            return node
    return None


class CheckableAccountTreeModel(QAbstractItemModel):
    def __init__(
        self,
        tree_view: QTreeView,
        proxy: QSortFilterProxyModel,
        flat_account_items: Sequence[Account | AccountGroup],
    ) -> None:
        super().__init__()
        self._tree_view = tree_view
        self._proxy = proxy
        self._flat_nodes: tuple[AccountTreeNode] = ()
        self._root_nodes: tuple[AccountTreeNode] = ()
        self.flat_account_items = flat_account_items

    @property
    def flat_account_items(self) -> tuple[Account | AccountGroup, ...]:
        return tuple(node.item for node in self._flat_nodes)

    @flat_account_items.setter
    def flat_account_items(
        self, flat_account_items: Collection[Account | AccountGroup]
    ) -> None:
        self._flat_nodes = tuple(sync_nodes(flat_account_items, self._flat_nodes))
        self._root_nodes = tuple(
            node for node in self._flat_nodes if node.parent is None
        )
        for node in self._flat_nodes:
            node.event_signal_changed.clear()
            node.event_signal_changed.append(
                lambda item_path: self._node_check_state_changed(item_path)
            )

    @property
    def checked_accounts(self) -> tuple[Account, ...]:
        return tuple(
            node.item
            for node in self._flat_nodes
            if node.check_state == Qt.CheckState.Checked
            and isinstance(node.item, Account)
        )

    @checked_accounts.setter
    def checked_accounts(self, checked_accounts: Collection[Account]) -> None:
        for node in self._flat_nodes:
            node.set_check_state(checked=node.item in checked_accounts)

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if index.isValid():
            if index.column() != 0:
                return 0
            node: AccountTreeNode = index.internalPointer()
            return len(node.children)
        return len(self._root_nodes)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        return 1 if not index.isValid() or index.column() == 0 else 0

    def index(self, row: int, column: int, _parent: QModelIndex = ...) -> QModelIndex:
        if _parent.isValid() and _parent.column() != 0:
            return QModelIndex()

        if not QAbstractItemModel.hasIndex(self, row, column, _parent):
            return QModelIndex()

        if not _parent or not _parent.isValid():
            parent = None
        else:
            parent: AccountTreeNode = _parent.internalPointer()

        child = self._root_nodes[row] if parent is None else parent.children[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child: AccountTreeNode = index.internalPointer()
        parent = child.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            parent_row = self._root_nodes.index(parent)
        else:
            parent_row = grandparent.children.index(parent)
        return QAbstractItemModel.createIndex(self, parent_row, 0, parent)

    def data(  # noqa: PLR0911, C901
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None
        node: AccountTreeNode = index.internalPointer()
        item = node.item
        if role == Qt.ItemDataRole.DisplayRole:
            return item.name
        if role == Qt.ItemDataRole.CheckStateRole:
            return node.check_state
        if role == Qt.ItemDataRole.DecorationRole:
            if isinstance(item, AccountGroup):
                if self._tree_view.isExpanded(self._proxy.mapFromSource(index)):
                    return icons.folder_open
                return icons.folder_closed
            if isinstance(item, CashAccount):
                if item.get_balance(item.currency).is_positive():
                    return icons.cash_account
                return icons.cash_account_empty
            if isinstance(item, SecurityAccount):
                return icons.security_account
        if role == Qt.ItemDataRole.UserRole:  # used for filtering
            return item.path
        return None

    def setData(  # noqa: N802
        self, index: QModelIndex, value: Any, role: int = ...  # noqa: ANN401
    ) -> bool | None:
        if role == Qt.ItemDataRole.CheckStateRole:
            item: AccountTreeNode = index.internalPointer()
            checked = value == Qt.CheckState.Checked.value
            item.set_check_state(checked=checked)
            return True
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsUserCheckable
        )

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def get_selected_item(self) -> Account | AccountGroup | None:
        proxy_indexes = self._tree_view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return None
        node: AccountTreeNode = source_indexes[0].internalPointer()
        return node.item

    def select_all(self) -> None:
        for node in self._root_nodes:
            node.set_check_state(
                checked=True,
            )

    def unselect_all(self) -> None:
        for node in self._root_nodes:
            node.set_check_state(
                checked=False,
            )

    def select_all_cash_accounts_below(self, account_group: AccountGroup) -> None:
        parent_node = get_node(account_group, self._flat_nodes)
        if parent_node is None:
            raise ValueError(f"Node with path='{account_group.path}' not found")
        for node in self._flat_nodes:
            if parent_node.item.path in node.item.path and isinstance(
                node.item, CashAccount
            ):
                node.set_check_state(checked=True)

    def select_all_security_accounts_below(self, account_group: AccountGroup) -> None:
        parent_node = get_node(account_group, self._flat_nodes)
        if parent_node is None:
            raise ValueError(f"Node with path='{account_group.path}' not found")
        for node in self._flat_nodes:
            if parent_node.item.path in node.item.path and isinstance(
                node.item, SecurityAccount
            ):
                node.set_check_state(checked=True)

    def _node_check_state_changed(self, item_path: str) -> None:
        node = get_node_by_item_path(item_path, self._flat_nodes)
        if node is None:
            raise ValueError(f"Node with path='{item_path}' not found")
        if node.parent is None:
            row = self._root_nodes.index(node)
        else:
            row = node.parent.children.index(node)
        index = QAbstractItemModel.createIndex(self, row, 0, node)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
