import logging
import unicodedata
from collections.abc import Sequence
from decimal import Decimal
from typing import Any, Self
from uuid import UUID

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
    CashAmount,
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
COLUMN_HEADERS = {
    AccountTreeColumn.NAME: "Name",
    AccountTreeColumn.BALANCE_NATIVE: "Native Balance",
    AccountTreeColumn.BALANCE_BASE: "Base Balance",
    AccountTreeColumn.SHOW: "",
}

COLUMNS_BALANCE = {
    AccountTreeColumn.BALANCE_NATIVE,
    AccountTreeColumn.BALANCE_BASE,
}


def convert_bool_to_checkstate(*, checked: bool) -> Qt.CheckState:
    return Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked


class AccountTreeNode:
    __slots__ = (
        "name",
        "path",
        "type_",
        "balance_base",
        "balance_native",
        "uuid",
        "parent",
        "children",
        "check_state",
        "event_signal_changed",
    )

    def __init__(  # noqa: PLR0913
        self,
        name: str,
        path: str,
        type_: type[Account | AccountGroup],
        balance_base: CashAmount | None,
        balance_native: CashAmount | None,
        uuid: UUID,
        parent: Self | None,
        children: list[Self],
    ) -> None:
        self.name = name
        self.path = path
        self.type_ = type_
        self.balance_base = balance_base
        self.balance_native = balance_native
        self.uuid = uuid
        self.parent = parent
        self.children: list[Self] = children
        self.check_state: Qt.CheckState = Qt.CheckState.Checked
        self.event_signal_changed = Event()

    def __repr__(self) -> str:
        return f"AccountTreeNode({self.path})"

    def __eq__(self, __o: object) -> bool:
        if not isinstance(__o, AccountTreeNode):
            return False
        return self.uuid == __o.uuid

    def set_check_state(self, *, checked: bool) -> None:
        """Sets check state of this node and its children, and updates the parents."""

        check_state = convert_bool_to_checkstate(checked=checked)
        self._set_check_state_recursive(check_state)
        if self.parent is not None:
            self.parent.update_check_state()

    def _set_check_state(self, check_state: Qt.CheckState) -> None:
        if check_state != self.check_state:
            self.check_state = check_state
            self.event_signal_changed(str(self.uuid))

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


def sync_nodes(
    items: Sequence[Account | AccountGroup],
    nodes: dict[UUID, AccountTreeNode],
    base_currency: Currency | None,
) -> tuple[AccountTreeNode]:
    """Accepts ordered sequence of items. Returns an ordered tuple of nodes."""

    new_nodes: list[AccountTreeNode] = []

    for item in items:
        node = get_node(item, nodes)
        parent_node = get_node(item.parent, nodes) if item.parent is not None else None
        if node is None:
            try:
                balance_base = item.get_balance(currency=base_currency)
            except (ConversionFactorNotFoundError, AttributeError):
                balance_base = None
            if isinstance(item, CashAccount) or (
                isinstance(item, SecurityAccount) and item.currency is not None
            ):
                balance_native = item.get_balance(item.currency)
            else:
                balance_native = None
            node = AccountTreeNode(
                item.name,
                item.path,
                item.__class__,
                balance_base,
                balance_native,
                item.uuid,
                parent_node,
                [],
            )
        else:
            node.name = item.name
            node.path = item.path
            try:
                node.balance_base = item.get_balance(currency=base_currency)
            except (ConversionFactorNotFoundError, AttributeError):
                node.balance_base = None
            if isinstance(item, CashAccount) or (
                isinstance(item, SecurityAccount) and item.currency is not None
            ):
                node.balance_native = item.get_balance(item.currency)
            node.parent = parent_node
            node.children = []
        node.parent = parent_node
        node.children = []
        if parent_node is not None:
            parent_node.children.append(node)
        if node.uuid not in nodes:
            nodes[node.uuid] = node
        new_nodes.append(node)

    return tuple(new_nodes)


def get_node(
    item: Account | AccountGroup | None, nodes: dict[UUID, AccountTreeNode]
) -> AccountTreeNode | None:
    if item is None:
        return None
    try:
        return nodes[item.uuid]
    except KeyError:
        return None


class AccountTreeModel(QAbstractItemModel):
    signal_check_state_changed = pyqtSignal()

    def __init__(
        self,
        view: QTreeView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._tree = view
        self._proxy = proxy
        self._root_nodes: tuple[AccountTreeNode] = ()
        self._item_dict: dict[UUID, Account | AccountGroup] = {}
        self._node_dict: dict[UUID, AccountTreeNode] = {}

    def load_data(
        self, items: Sequence[Account | AccountGroup], base_currency: Currency | None
    ) -> None:
        nodes = sync_nodes(items, self._node_dict, base_currency)
        self._item_dict = {item.uuid: item for item in items}
        self._node_dict = {node.uuid: node for node in nodes}
        self._root_nodes = tuple(node for node in nodes if node.parent is None)

        for node in nodes:
            node.event_signal_changed.clear()
            node.event_signal_changed.append(
                lambda uuid_string: self._node_check_state_changed(uuid_string)
            )

        # alert presenter check state could have changed (i.e. after adding items)
        self.signal_check_state_changed.emit()

    def get_checked_accounts(self) -> frozenset[Account]:
        uuids = {
            node.uuid
            for node in self._node_dict.values()
            if node.check_state == Qt.CheckState.Checked
        }
        items = [self._item_dict[uuid] for uuid in uuids]
        return frozenset(item for item in items if isinstance(item, Account))

    def get_checked_account_items(self) -> frozenset[Account | AccountGroup]:
        uuids = {
            node.uuid
            for node in self._node_dict.values()
            if node.check_state
            in {Qt.CheckState.Checked, Qt.CheckState.PartiallyChecked}
        }
        items = [self._item_dict[uuid] for uuid in uuids]
        return frozenset(items)

    def rowCount(self, index: QModelIndex = ...) -> int:
        if index.isValid():
            if index.column() != 0:
                return 0
            node: AccountTreeNode = index.internalPointer()
            return len(node.children)
        return len(self._root_nodes)

    def columnCount(self, index: QModelIndex = ...) -> int:
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

    def setData(
        self, index: QModelIndex, value: Any, role: int = ...  # noqa: ANN401
    ) -> bool | None:
        if role == Qt.ItemDataRole.CheckStateRole:
            node: AccountTreeNode = index.internalPointer()
            checked = value == Qt.CheckState.Checked.value
            node.set_check_state(checked=checked)
            logging.debug(
                f"Changing Account Tree item '{node.path}' state: "
                f"{node.check_state.name}"
            )
            self.signal_check_state_changed.emit()
            return True
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return COLUMN_HEADERS[section]
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
            return self._get_display_role_data(index.column(), index.internalPointer())
        if role == Qt.ItemDataRole.DecorationRole:
            return self._get_decoration_role_data(
                index.column(), index.internalPointer(), index
            )
        if (
            role == Qt.ItemDataRole.CheckStateRole
            and index.column() == AccountTreeColumn.SHOW
        ):
            return index.internalPointer().check_state
        if role == Qt.ItemDataRole.TextAlignmentRole:
            column = index.column()
            if column in COLUMNS_BALANCE:
                return TEXT_ALIGNMENT_BALANCE
        if role == Qt.ItemDataRole.ForegroundRole:
            return self._get_foreground_role_data(
                index.column(), index.internalPointer()
            )
        if role == Qt.ItemDataRole.UserRole:
            return self._get_sort_data(index.column(), index.internalPointer())
        if role == Qt.ItemDataRole.UserRole + 1:
            return self._get_filter_data(index.column(), index.internalPointer())
        if role == Qt.ItemDataRole.ToolTipRole:
            return self._get_tooltip_role_data(index.column(), index.internalPointer())
        return None

    def _get_display_role_data(self, column: int, item: AccountTreeNode) -> str | None:
        if column == AccountTreeColumn.NAME:
            return item.name
        if (
            column == AccountTreeColumn.BALANCE_NATIVE
            and item.balance_native is not None
        ):
            if (
                item.balance_base is not None
                and item.balance_native.currency == item.balance_base.currency
            ):
                return ""
            return item.balance_native.to_str_rounded()
        if column == AccountTreeColumn.BALANCE_BASE:
            if item.balance_base is not None:
                return item.balance_base.to_str_rounded()
            return "Error!"
        return None

    def _get_decoration_role_data(
        self,
        column: int,
        item: AccountTreeNode,
        index: QModelIndex,
    ) -> QIcon | None:
        if column == AccountTreeColumn.NAME:
            if item.type_ == AccountGroup:
                if self._tree.isExpanded(index):
                    return icons.folder_open
                return icons.folder_closed
            if item.type_ == SecurityAccount:
                return icons.security_account
            if item.type_ == CashAccount:
                if (
                    item.balance_base is not None
                    and not item.balance_base.is_nan()
                    and item.balance_base.value_rounded > 0
                ):
                    return icons.cash_account
                return icons.cash_account_empty
        return None

    def _get_foreground_role_data(  # noqa: PLR0911
        self, column: int, item: AccountTreeNode
    ) -> QBrush | None:
        if column == AccountTreeColumn.SHOW:
            return None

        if column == AccountTreeColumn.NAME:
            if item.balance_base is None:
                return None
            if abs(item.balance_base.value_rounded) == 0:
                return colors.get_gray_brush()
        if column == AccountTreeColumn.BALANCE_BASE:
            if item.balance_base is None:
                return colors.get_red_brush()
            amount = item.balance_base
        elif (
            column == AccountTreeColumn.BALANCE_NATIVE
            and item.balance_native is not None
        ):
            amount = item.balance_native
        else:
            return None

        if amount.is_nan() or amount.value_rounded < 0:
            return colors.get_red_brush()
        if abs(amount.value_rounded) == 0:
            return colors.get_gray_brush()
        return None

    def _get_sort_data(
        self, column: int, item: AccountTreeNode
    ) -> Decimal | str | None:
        if column == AccountTreeColumn.NAME:
            return unicodedata.normalize(
                "NFD", self._get_display_role_data(column, item)
            )
        if (
            column == AccountTreeColumn.BALANCE_NATIVE
            and item.balance_native is not None
        ):
            return float(item.balance_native.value_normalized)
        if column == AccountTreeColumn.BALANCE_BASE and item.balance_base is not None:
            try:
                return float(item.balance_base.value_normalized)
            except ConversionFactorNotFoundError:
                return None
        return None

    def _get_tooltip_role_data(self, column: int, item: AccountTreeNode) -> str | None:
        if column == AccountTreeColumn.BALANCE_NATIVE:
            if (
                item.type_ == CashAccount
                and item.balance_base.currency != item.balance_native.currency
            ):
                return item.balance_native.to_str_normalized()
            return None
        if column == AccountTreeColumn.BALANCE_BASE:
            return item.balance_base.to_str_normalized()
        if column == AccountTreeColumn.SHOW:
            return (
                "Only Transactions related to checked Accounts will be shown in "
                "the Transaction Table"
            )
        return None

    def _get_filter_data(self, column: int, item: AccountTreeNode) -> str | None:
        if column == AccountTreeColumn.NAME:
            return item.path
        return self._get_display_role_data(column, item)

    def pre_add(self, parent: AccountGroup | None, index: int) -> None:
        self._proxy.setDynamicSortFilter(False)
        parent_index = self.get_index_from_item(parent)
        self.beginInsertRows(parent_index, index, index)

    def post_add(self) -> None:
        self.endInsertRows()
        self._proxy.setDynamicSortFilter(True)

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
        self._proxy.setDynamicSortFilter(False)
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
        self._proxy.setDynamicSortFilter(True)

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
        return self._item_dict[node.uuid]

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
        node = get_node(item, self._node_dict)
        if node is None:
            raise ValueError(f"Item {item} not present within AccountTreeModel data.")
        return node

    def set_check_state_all(self, *, checked: bool) -> None:
        check_state = convert_bool_to_checkstate(checked=checked)
        logging.debug(f"Set all AccountTree item check state: {check_state.name}")
        for node in self._node_dict.values():
            node.check_state = check_state

    def set_selected_check_state(self, *, checked: bool, only: bool) -> None:
        node = self.get_selected_node()
        if node is None:
            return
        if only:
            check_state = convert_bool_to_checkstate(checked=not checked)
            for _node in self._node_dict.values():
                _node.check_state = check_state
            node.set_check_state(checked=checked)
            logging.debug(
                f"Set exclusive check state: {node.check_state.name}, path={node.path}"
            )
        else:
            node.set_check_state(checked=checked)
            logging.debug(f"Set check state: {node.check_state.name}, path={node.path}")

    def check_all_cash_accounts_below(self, account_group: AccountGroup) -> None:
        parent_node = get_node(account_group, self._node_dict)
        if parent_node is None:
            raise ValueError(f"Node with path='{account_group.path}' not found.")
        for node in self._node_dict.values():
            if parent_node.path in node.path and node.type_ == CashAccount:
                node.set_check_state(checked=True)

    def check_all_security_accounts_below(self, account_group: AccountGroup) -> None:
        parent_node = get_node(account_group, self._node_dict)
        if parent_node is None:
            raise ValueError(f"Node with path='{account_group.path}' not found.")
        for node in self._node_dict.values():
            if parent_node.path in node.path and node.type_ == SecurityAccount:
                node.set_check_state(checked=True)

    def _node_check_state_changed(self, uuid_string: str) -> None:
        uuid = UUID(uuid_string)
        try:
            node = self._node_dict[uuid]
        except KeyError as exc:
            raise ValueError(f"Node with uuid='{uuid_string}' not found.") from exc

        if node.parent is None:
            row = self._root_nodes.index(node)
        else:
            row = node.parent.children.index(node)
        index = QAbstractItemModel.createIndex(self, row, AccountTreeColumn.SHOW, node)
        self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
