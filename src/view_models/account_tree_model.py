import logging
from collections.abc import Callable, Sequence
from copy import copy
from typing import Any, Self
from uuid import UUID

from PyQt6.QtCore import (
    QAbstractItemModel,
    QModelIndex,
    QObject,
    Qt,
    QTimer,
    pyqtSignal,
)
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
from src.views import colors, icons
from src.views.constants import AccountTreeColumn


def convert_bool_to_checkstate(*, checked: bool) -> Qt.CheckState:
    return Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked


class ClickTimer:
    DELAY_MS = 250

    def __init__(self, parent: QObject) -> None:
        self.timer = QTimer(parent=parent)
        self.timer.setInterval(ClickTimer.DELAY_MS)
        self.timer.setSingleShot(True)  # noqa: FBT003
        self.timer.timeout.connect(self._timeout)

    def set_timeout_callable(self, timeout_callable: Callable[[], Any]) -> None:
        self.timeout_callable = timeout_callable

    def start(self) -> None:
        self.timer.start()

    def stop(self) -> None:
        self.timer.stop()

    def _timeout(self) -> None:
        self.timeout_callable()


class AccountTreeNode:
    def __init__(self, item: Account | AccountGroup, parent: Self | None) -> None:
        self.item = item
        self.parent = parent
        self.children: list[Self] = []
        self.check_state: Qt.CheckState = Qt.CheckState.Checked

    @property
    def uuid(self) -> UUID:
        return self.item.uuid

    def __repr__(self) -> str:
        return f"AccountTreeNode({str(self.item)})"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, AccountTreeNode):
            return False
        return self.item == __o.item

    def set_visible(self, *, visible: bool) -> None:
        """Sets visibility of this node and its children, and updates the parents."""

        check_state = convert_bool_to_checkstate(checked=visible)
        self._set_check_state(check_state)
        if self.parent is not None:
            self.parent.update_visibility()

    def _set_check_state(self, visible: Qt.CheckState) -> None:
        self.check_state = visible
        self._set_children_visible(visible)

    def _set_children_visible(self, visible: Qt.CheckState) -> None:
        for child in self.children:
            child._set_check_state(visible)  # noqa: SLF001

    def update_visibility(self) -> None:
        if all(child.check_state == Qt.CheckState.Checked for child in self.children):
            self.check_state = Qt.CheckState.Checked
        elif all(
            child.check_state == Qt.CheckState.Unchecked for child in self.children
        ):
            self.check_state = Qt.CheckState.Unchecked
        else:
            self.check_state = Qt.CheckState.PartiallyChecked

        if self.parent is not None:
            self.parent.update_visibility()


# BUG: there is a bug here somewhere when deleting account item (maybe only CashAccount)
# can't reproduce it anymore...
def sync_nodes(
    items: Sequence[Account | AccountGroup], nodes: Sequence[AccountTreeNode]
) -> Sequence[AccountTreeNode]:
    """Accepts flat lists of items and nodes. Returns new flat nodes."""

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
        if node.uuid == item.uuid:
            return node
    return None


def get_visible_leaf_items(nodes: Sequence[AccountTreeNode]) -> list[Account]:
    resulting_list = []
    for node in nodes:
        if len(node.children) == 0 and node.check_state == Qt.CheckState.Checked:
            resulting_list.append(node.item)
        elif (
            node.check_state == Qt.CheckState.Checked
            or node.check_state == Qt.CheckState.PartiallyChecked
        ):
            resulting_list = resulting_list + get_visible_leaf_items(node.children)
    return resulting_list


class AccountTreeModel(QAbstractItemModel):
    COLUMN_HEADERS = {
        AccountTreeColumn.NAME: "Name",
        AccountTreeColumn.BALANCE_NATIVE: "Native balance",
        AccountTreeColumn.BALANCE_BASE: "Base balance",
        AccountTreeColumn.SHOW: "",
    }
    signal_show_only_selection = pyqtSignal()
    signal_toggle_visibility = pyqtSignal()

    def __init__(
        self,
        view: QTreeView,
        flat_items: Sequence[Account | AccountGroup],
        base_currency: Currency,
    ) -> None:
        super().__init__()
        self._tree = view
        self._root_nodes = []
        self._flat_nodes = []
        self.flat_items = flat_items
        self.base_currency = base_currency

        self.timer = ClickTimer(self)

        self._tree.clicked.connect(lambda index: self._tree_clicked(index))
        self._tree.doubleClicked.connect(lambda index: self._tree_double_clicked(index))

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

    @property
    def root_items(self) -> tuple[Account | AccountGroup, ...]:
        return tuple(node.item for node in self._root_nodes)

    @property
    def visible_accounts(self) -> tuple[Account, ...]:
        return tuple(get_visible_leaf_items(self._root_nodes))

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if index.isValid():
            if index.column() != 0:
                return 0
            node: AccountTreeNode = index.internalPointer()
            if not isinstance(node, AccountTreeNode):
                raise TypeError(f"node should be AccountTreeNode, is {type(node)}")
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

    def data(  # noqa: PLR0911
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | QIcon | QBrush | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None
        column = index.column()
        node: AccountTreeNode = index.internalPointer()
        item = node.item
        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(column, item)
        if role == Qt.ItemDataRole.DecorationRole:
            return self._get_decoration_role_data(column, item, index, node)
        if role == Qt.ItemDataRole.TextAlignmentRole and (
            column == AccountTreeColumn.BALANCE_NATIVE
            or column == AccountTreeColumn.BALANCE_BASE
        ):
            return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(column, item)
        if role == Qt.ItemDataRole.ToolTipRole and column == AccountTreeColumn.SHOW:
            return (
                "Single-click: toggle visibility\n"
                "Double-click: set only this item visible"
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

    def _get_decoration_role_data(  # noqa: PLR0911
        self,
        column: int,
        item: Account | AccountGroup,
        index: QModelIndex,
        node: AccountTreeNode,
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
        if column == AccountTreeColumn.SHOW:
            # IDEA: change eye icon on mouse hover (blue)
            if node.check_state == Qt.CheckState.Checked:
                return icons.eye_open
            if node.check_state == Qt.CheckState.PartiallyChecked:
                return icons.eye_partial
            return icons.eye_closed
        return None

    def _get_foreground_role_data(  # noqa: PLR0911
        self, column: int, item: Account | AccountGroup
    ) -> QBrush | None:
        if self.base_currency is None:
            return None

        if (
            column == AccountTreeColumn.NAME
            and item.get_balance(self.base_currency).value_normalized == 0
        ):
            return QBrush(QColor("gray"))
        if column == AccountTreeColumn.BALANCE_BASE:
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
            return QBrush(QColor("gray"))
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

    def pre_add(self, parent: AccountGroup | None) -> None:
        parent_index = self.get_index_from_item(parent)
        row_index = len(self._root_nodes) if parent is None else len(parent.children)
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

    def get_selected_item_index(self) -> QModelIndex:
        indexes = self._tree.selectedIndexes()
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
        node = AccountTreeModel._find_node(self._root_nodes, item)
        if node is None:
            raise ValueError(f"Item {item} not present within AccountTreeModel data.")
        return node

    @staticmethod
    def _find_node(
        nodes: Sequence[AccountTreeNode], item: Account | AccountGroup
    ) -> AccountTreeNode | None:
        for node in nodes:
            if node.item == item:
                return node
            child_node = AccountTreeModel._find_node(node.children, item)
            if child_node is not None:
                return child_node
        return None

    def _tree_clicked(self, index: QModelIndex) -> None:
        if index.column() == AccountTreeColumn.SHOW:
            self.timer.set_timeout_callable(self.signal_toggle_visibility.emit)
            self.timer.start()

    def _tree_double_clicked(self, index: QModelIndex) -> None:
        if index.column() == AccountTreeColumn.SHOW:
            self.timer.stop()
            self.signal_show_only_selection.emit()

    def set_visibility_all(self, *, visible: bool) -> None:
        check_state = convert_bool_to_checkstate(checked=visible)
        logging.debug(f"Set all AccountTree item visibility: {check_state.name}")
        for node in self._root_nodes:
            AccountTreeModel._set_visibility_below(node, check_state)

    @staticmethod
    def _set_visibility_below(node: AccountTreeNode, visible: Qt.CheckState) -> None:
        node.check_state = visible
        for child in node.children:
            AccountTreeModel._set_visibility_below(child, visible)

    def set_visibility(self, *, visible: bool, only: bool) -> None:
        node = self.get_selected_node()
        if only:
            self.set_visibility_all(visible=not visible)
            node.set_visible(visible=visible)
            logging.debug(
                f"Set exclusive visibility: {node.check_state.name}, item={node.item}"
            )
        else:
            node.set_visible(visible=visible)
            logging.debug(f"Set visibility: {node.check_state.name}, item={node.item}")

    def toggle_visibility(self) -> None:
        node = self.get_selected_node()
        if node.check_state == Qt.CheckState.Checked:
            node.set_visible(visible=False)
        elif node.check_state == Qt.CheckState.Unchecked:
            node.set_visible(visible=True)
        else:
            node.set_visible(visible=True)
        self._tree.viewport().update()
        logging.debug(f"Toggled visibility: {node.check_state.name}, item={node.item}")
