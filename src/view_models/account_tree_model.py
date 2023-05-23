import logging
import unicodedata
from collections.abc import Sequence
from copy import copy
from decimal import Decimal
from typing import Any, Self

from PyQt6.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QSortFilterProxyModel,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QBrush, QIcon
from PyQt6.QtWidgets import QTreeView
from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency_objects import (
    ConversionFactorNotFoundError,
    Currency,
)
from src.models.model_objects.security_objects import SecurityAccount
from src.presenters.utilities.event import Event
from src.views import colors, icons
from src.views.constants import AccountTreeColumn

TEXT_ALIGNMENT_BALANCE = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
FLAGS_SHOW = (
    Qt.ItemFlag.ItemIsSelectable
    | Qt.ItemFlag.ItemIsEnabled
    | Qt.ItemFlag.ItemIsUserCheckable
)
FLAGS_DEFAULT = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled


def convert_bool_to_checkstate(*, checked: bool) -> Qt.CheckState:
    return Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked


class AccountTreeNode:
    __slots__ = ("item", "parent", "children", "check_state", "event_signal_changed")

    def __init__(self, item: Account | AccountGroup, parent: Self | None) -> None:
        self.item = item
        self.parent = parent
        self.children: list[Self] = []
        self.check_state: Qt.CheckState = Qt.CheckState.Checked
        self.event_signal_changed = Event()

    def __repr__(self) -> str:
        return f"AccountTreeNode({self.item!s})"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, AccountTreeNode):
            return False
        return self.item.uuid == __o.item.uuid

    def set_check_state(self, *, checked: bool) -> None:
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


# BUG: there is a bug here somewhere when deleting account item (maybe only CashAccount)
# can't reproduce it anymore...
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


class AccountTreeModel(QAbstractItemModel):
    COLUMN_HEADERS = {
        AccountTreeColumn.NAME: "Name",
        AccountTreeColumn.BALANCE_NATIVE: "Native balance",
        AccountTreeColumn.BALANCE_BASE: "Base balance",
        AccountTreeColumn.SHOW: "",
    }
    signal_check_state_changed = pyqtSignal()

    def __init__(
        self,
        view: QTreeView,
        proxy: QSortFilterProxyModel,
        flat_items: Sequence[Account | AccountGroup],
        base_currency: Currency,
    ) -> None:
        super().__init__()
        self._tree = view
        self._proxy = proxy
        self._root_nodes = ()
        self._flat_nodes = ()
        self.flat_items = flat_items
        self.base_currency = base_currency

    @property
    def flat_items(self) -> tuple[Account | AccountGroup, ...]:
        return tuple(self._flat_items)

    @flat_items.setter
    def flat_items(self, items: Sequence[Account | AccountGroup]) -> None:
        self._flat_items = list(items)
        self._flat_nodes = tuple(sync_nodes(items, self._flat_nodes))
        self._root_nodes = tuple(
            node for node in self._flat_nodes if node.parent is None
        )
        for node in self._flat_nodes:
            node.event_signal_changed.clear()
            node.event_signal_changed.append(
                lambda item_path: self._node_check_state_changed(item_path)
            )

    @property
    def root_items(self) -> tuple[Account | AccountGroup, ...]:
        return tuple(node.item for node in self._root_nodes)

    @property
    def checked_accounts(self) -> tuple[Account, ...]:
        return tuple(
            node.item
            for node in self._flat_nodes
            if node.check_state == Qt.CheckState.Checked
            and isinstance(node.item, Account)
        )

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if index.isValid():
            if index.column() != 0:
                return 0
            node: AccountTreeNode = index.internalPointer()
            return len(node.children)
        return len(self._root_nodes)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        return 4 if not index.isValid() or index.column() == 0 else 0

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        if not parent or not parent.isValid():
            _parent = None
        else:
            _parent: AccountTreeNode = parent.internalPointer()

        child = self._root_nodes[row] if _parent is None else _parent.children[row]
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

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        column = index.column()
        if column == AccountTreeColumn.SHOW:
            return FLAGS_SHOW
        return FLAGS_DEFAULT

    def setData(  # noqa: N802
        self, index: QModelIndex, value: Any, role: int = ...  # noqa: ANN401
    ) -> bool | None:
        if role == Qt.ItemDataRole.CheckStateRole:
            node: AccountTreeNode = index.internalPointer()
            checked = value == Qt.CheckState.Checked.value
            node.set_check_state(checked=checked)
            self.signal_check_state_changed.emit()
            return True
        return None

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.COLUMN_HEADERS[section]
            return str(section)
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        return None

    def data(  # noqa: PLR0911, C901
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | QIcon | QBrush | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(
                index.column(), index.internalPointer().item
            )
        if role == Qt.ItemDataRole.DecorationRole:
            return self._get_decoration_role_data(
                index.column(), index.internalPointer().item, index
            )
        if (
            role == Qt.ItemDataRole.CheckStateRole
            and index.column() == AccountTreeColumn.SHOW
        ):
            return index.internalPointer().check_state
        if role == Qt.ItemDataRole.TextAlignmentRole:
            column = index.column()
            if (
                column == AccountTreeColumn.BALANCE_NATIVE
                or column == AccountTreeColumn.BALANCE_BASE
            ):
                return TEXT_ALIGNMENT_BALANCE
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(
                index.column(), index.internalPointer().item
            )
        if role == Qt.ItemDataRole.UserRole:
            return self._get_sort_data(index.column(), index.internalPointer().item)
        if role == Qt.ItemDataRole.UserRole + 1:
            return self._get_filter_data(index.column(), index.internalPointer().item)
        if (
            role == Qt.ItemDataRole.ToolTipRole
            and index.column() == AccountTreeColumn.SHOW
        ):
            return (
                "Only Transactions related to checked Accounts will be shown in "
                "the Transaction Table"
            )

        return None

    def _get_display_role_data(
        self, column: int, item: Account | AccountGroup
    ) -> str | None:
        if column == AccountTreeColumn.NAME:
            return item.name
        if column == AccountTreeColumn.BALANCE_NATIVE and isinstance(item, CashAccount):
            return item.get_balance(item.currency).to_str_rounded()
        if column == AccountTreeColumn.BALANCE_BASE and self.base_currency is not None:
            try:
                balance = item.get_balance(self.base_currency)
            except ConversionFactorNotFoundError:
                return "Error!"
            else:
                return balance.to_str_rounded()
        return None

    def _get_decoration_role_data(
        self,
        column: int,
        item: Account | AccountGroup,
        index: QModelIndex,
    ) -> QIcon | None:
        if column == AccountTreeColumn.NAME:
            if isinstance(item, AccountGroup):
                if self._tree.isExpanded(index):
                    return icons.folder_open
                return icons.folder_closed
            if isinstance(item, SecurityAccount):
                return icons.security_account
            if isinstance(item, CashAccount):
                if item.get_balance(item.currency).is_positive():
                    return icons.cash_account
                return icons.cash_account_empty
        return None

    def _get_foreground_role_data(  # noqa: PLR0911, PLR0912, C901
        self, column: int, item: Account | AccountGroup
    ) -> QBrush | None:
        if column == AccountTreeColumn.SHOW:
            return None

        if column == AccountTreeColumn.NAME:
            if self.base_currency is None:
                return None
            try:
                if item.get_balance(self.base_currency).value_normalized == 0:
                    return colors.get_gray_brush()
            except ConversionFactorNotFoundError:
                return None
            else:
                return None
        if column == AccountTreeColumn.BALANCE_BASE:
            if self.base_currency is None:
                return None
            try:
                amount = item.get_balance(self.base_currency)
            except ConversionFactorNotFoundError:
                return colors.get_red_brush()
        elif column == AccountTreeColumn.BALANCE_NATIVE and isinstance(
            item, CashAccount
        ):
            amount = item.get_balance(item.currency)
        else:
            return None

        if amount.is_negative():
            return colors.get_red_brush()
        if amount.value_normalized == 0:
            return colors.get_gray_brush()
        return None

    def _get_sort_data(
        self, column: int, item: Account | AccountGroup
    ) -> Decimal | str | None:
        if column == AccountTreeColumn.NAME:
            return unicodedata.normalize(
                "NFD", self._get_display_role_data(column, item)
            )
        if column == AccountTreeColumn.BALANCE_NATIVE and isinstance(item, CashAccount):
            return float(item.get_balance(item.currency).value_normalized)
        if column == AccountTreeColumn.BALANCE_BASE and self.base_currency is not None:
            try:
                return float(item.get_balance(self.base_currency).value_normalized)
            except ConversionFactorNotFoundError:
                return None
        return None

    def _get_filter_data(self, column: int, item: Account | AccountGroup) -> str | None:
        if column == AccountTreeColumn.NAME:
            return item.path
        return self._get_display_role_data(column, item)

    def pre_add(self, parent: AccountGroup | None) -> None:
        self._proxy.setDynamicSortFilter(False)  # noqa: FBT003
        parent_index = self.get_index_from_item(parent)
        row_index = len(self._root_nodes) if parent is None else len(parent.children)
        self.beginInsertRows(parent_index, row_index, row_index)

    def post_add(self) -> None:
        self.endInsertRows()
        self._proxy.setDynamicSortFilter(True)  # noqa: FBT003

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
        self._proxy.setDynamicSortFilter(False)  # noqa: FBT003
        previous_parent_index = self.get_index_from_item(previous_parent)
        new_parent_index = self.get_index_from_item(new_parent)
        # Index must be limited to valid indexes
        if new_parent is None:
            if new_index > len(self._root_nodes):
                new_index = len(self._root_nodes)
        elif new_index > len(new_parent.children):
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
        self._proxy.setDynamicSortFilter(True)  # noqa: FBT003

    def get_selected_item_index(self) -> QModelIndex:
        indexes = self._tree.selectedIndexes()
        indexes = [self._proxy.mapToSource(index) for index in indexes]
        if len(indexes) == 0:
            return QModelIndex()
        return indexes[0]

    def get_selected_node(self) -> AccountTreeNode:
        index = self.get_selected_item_index()
        return index.internalPointer()

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
        node = get_node(item, self._flat_nodes)
        if node is None:
            raise ValueError(f"Item {item} not present within AccountTreeModel data.")
        return node

    def set_check_state_all(self, *, checked: bool) -> None:
        check_state = convert_bool_to_checkstate(checked=checked)
        logging.debug(f"Set all AccountTree item check state: {check_state.name}")
        for node in self._flat_nodes:
            node.check_state = check_state

    def set_selected_check_state(self, *, checked: bool, only: bool) -> None:
        node = self.get_selected_node()
        if node is None:
            return
        if only:
            self.set_check_state_all(checked=not checked)
            node.set_check_state(checked=checked)
            logging.debug(
                f"Set exclusive check state: {node.check_state.name}, item={node.item}"
            )
        else:
            node.set_check_state(checked=checked)
            logging.debug(f"Set check state: {node.check_state.name}, item={node.item}")

    def select_all_cash_accounts_below(self, account_group: AccountGroup) -> None:
        parent_node = get_node(account_group, self._flat_nodes)
        if parent_node is None:
            raise ValueError(f"Node with path='{account_group.path}' not found.")
        for node in self._flat_nodes:
            if parent_node.item.path in node.item.path and isinstance(
                node.item, CashAccount
            ):
                node.set_check_state(checked=True)

    def select_all_security_accounts_below(self, account_group: AccountGroup) -> None:
        parent_node = get_node(account_group, self._flat_nodes)
        if parent_node is None:
            raise ValueError(f"Node with path='{account_group.path}' not found.")
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
        index = QAbstractItemModel.createIndex(self, row, AccountTreeColumn.SHOW, node)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
