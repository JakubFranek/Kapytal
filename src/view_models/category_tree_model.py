import unicodedata
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Self

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QTreeView
from src.models.model_objects.attributes import Category
from src.models.model_objects.currency_objects import CashAmount
from src.models.utilities.calculation import CategoryStats
from src.views.constants import CategoryTreeColumn

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


@dataclass
class CategoryTreeNode:
    name: str
    path: str
    transactions_self: int
    transactions_total: int
    balance: CashAmount
    parent: Self | None
    children: list[Self]
    uuid: uuid.UUID

    def __repr__(self) -> str:
        return f"CategoryTreeNode({self.path})"


def sync_nodes(
    nodes: Sequence[CategoryTreeNode],
    flat_categories: Sequence[Category],
    category_stats: dict[Category, CategoryStats],
) -> tuple[CategoryTreeNode]:
    nodes_dict = {node.uuid: node for node in nodes}
    new_nodes: list[CategoryTreeNode] = []

    for category in flat_categories:
        stats = category_stats[category]
        node = get_node(category, nodes_dict)
        parent_node = get_node(category.parent, nodes_dict)
        if node is None:
            node = CategoryTreeNode(
                category.name,
                category.path,
                stats.transactions_self,
                stats.transactions_total,
                stats.balance,
                parent_node,
                [],
                category.uuid,
            )
        else:
            node.name = category.name
            node.path = category.path
            node.transactions_self = stats.transactions_self
            node.transactions_total = stats.transactions_total
            node.balance = stats.balance
            node.parent = parent_node
            node.children = []
        if parent_node is not None:
            parent_node.children.append(node)
        if node.uuid not in nodes_dict:
            nodes_dict[node.uuid] = node
        new_nodes.append(node)
    return tuple(new_nodes)


def get_node(
    category: Category | None, nodes: dict[uuid.UUID, CategoryTreeNode]
) -> CategoryTreeNode | None:
    if category is None:
        return None
    try:
        return nodes[category.uuid]
    except KeyError:
        return None


class CategoryTreeModel(QAbstractItemModel):
    COLUMN_HEADERS = {
        CategoryTreeColumn.NAME: "Name",
        CategoryTreeColumn.TRANSACTIONS: "Transactions",
        CategoryTreeColumn.BALANCE: "Balance",
    }

    def __init__(
        self,
        tree_view: QTreeView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._tree_view = tree_view
        self._proxy = proxy
        self._flat_nodes: tuple[CategoryTreeNode, ...] = ()
        self._root_nodes: tuple[CategoryTreeNode, ...] = ()

    def load_data(
        self,
        flat_categories: Sequence[Category],
        category_stats: dict[Category, CategoryStats],
    ) -> None:
        self._flat_categories = tuple(flat_categories)
        self._flat_nodes = sync_nodes(self._flat_nodes, flat_categories, category_stats)
        self._root_nodes = tuple(
            node for node in self._flat_nodes if node.parent is None
        )

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if index.isValid():
            if index.column() != 0:
                return 0
            node: CategoryTreeNode = index.internalPointer()
            return len(node.children)
        return len(self._root_nodes)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        return 3 if not index.isValid() or index.column() == 0 else 0

    def index(self, row: int, column: int, _parent: QModelIndex = ...) -> QModelIndex:
        if _parent.isValid() and _parent.column() != 0:
            return QModelIndex()

        if not _parent or not _parent.isValid():
            parent = None
        else:
            parent: CategoryTreeNode = _parent.internalPointer()

        child = self._root_nodes[row] if parent is None else parent.children[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child: CategoryTreeNode = index.internalPointer()
        parent = child.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            parent_row = self._root_nodes.index(parent)
        else:
            parent_row = grandparent.children.index(parent)
        return QAbstractItemModel.createIndex(self, parent_row, 0, parent)

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.COLUMN_HEADERS[section]
            return str(section)
        return None

    def data(  # noqa: PLR0911
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None
        column = index.column()
        node: CategoryTreeNode = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(column, node)
        if role == Qt.ItemDataRole.UserRole:
            if column == CategoryTreeColumn.NAME:
                return unicodedata.normalize("NFD", node.name)
            if column == CategoryTreeColumn.TRANSACTIONS:
                return node.transactions_total
            if column == CategoryTreeColumn.BALANCE:
                return float(node.balance.value_normalized)
        if role == Qt.ItemDataRole.UserRole + 1 and column == CategoryTreeColumn.NAME:
            return node.path
        if role == Qt.ItemDataRole.TextAlignmentRole and (
            column == CategoryTreeColumn.TRANSACTIONS
            or column == CategoryTreeColumn.BALANCE
        ):
            return ALIGNMENT_RIGHT
        if (
            role == Qt.ItemDataRole.ToolTipRole
            and column == CategoryTreeColumn.TRANSACTIONS
        ):
            return (
                "Number outside of parentheses is the number of Transactions\n"
                "containing the Category and/or its children Categories.\n"
                "Number in parentheses is the number of Transactions containing\n"
                "the Category directly, not counting its children."
            )
        return None

    def _get_display_role_data(
        self, column: int, node: CategoryTreeNode
    ) -> str | int | None:
        if column == CategoryTreeColumn.NAME:
            return node.name
        if column == CategoryTreeColumn.TRANSACTIONS:
            if len(node.children) == 0:
                return node.transactions_total
            return f"{node.transactions_total} ({node.transactions_self})"
        if column == CategoryTreeColumn.BALANCE:
            return node.balance.to_str_rounded()
        return None

    def pre_add(self, parent: Category | None, index: int) -> None:
        parent_index = self.get_index_from_item(parent)
        self.beginInsertRows(parent_index, index, index)

    def post_add(self) -> None:
        self.endInsertRows()

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def pre_remove_item(self, item: Category) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(index.parent(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def pre_move_item(
        self,
        previous_parent: Category | None,
        previous_index: int,
        new_parent: Category | None,
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

    def get_selected_item(self) -> Category | None:
        proxy_indexes = self._tree_view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return None
        node = source_indexes[0].internalPointer()
        return self._get_item_from_node(node)

    def get_index_from_item(self, item: Category | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        node = self._get_node_from_item(item)
        parent_node = node.parent
        if parent_node is None:
            row = self._root_nodes.index(node)
        else:
            row = parent_node.children.index(node)
        return QAbstractItemModel.createIndex(self, row, 0, node)

    def _get_item_from_node(self, node: CategoryTreeNode) -> Category:
        for category in self._flat_categories:
            if node.uuid == category.uuid:
                return category
        raise ValueError(f"Category {node.path} not found.")

    def _get_node_from_item(self, item: Category) -> CategoryTreeNode:
        for node in self._flat_nodes:
            if node.uuid == item.uuid:
                return node
        raise ValueError(f"Node for Category {item.path} not found.")
