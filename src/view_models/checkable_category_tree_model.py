from collections.abc import Collection, Sequence
from copy import copy
from enum import Enum, auto
from typing import Self

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtGui import QFont
from src.models.model_objects.attributes import Category
from src.presenters.utilities.event import Event

bold_font = QFont()
bold_font.setBold(True)

FLAGS_CHECKABLE = (
    Qt.ItemFlag.ItemIsSelectable
    | Qt.ItemFlag.ItemIsEnabled
    | Qt.ItemFlag.ItemIsUserCheckable
)


class CategorySelectionMode(Enum):
    HIERARCHICAL = auto()
    INDIVIDUAL = auto()


def convert_bool_to_checkstate(*, checked: bool) -> Qt.CheckState:
    return Qt.CheckState.Checked if checked else Qt.CheckState.Unchecked


class CategoryTreeNode:
    def __init__(self, item: Category, parent: Self | None) -> None:
        self.item = item
        self.parent = parent
        self.children: list[Self] = []
        self.check_state: Qt.CheckState = Qt.CheckState.Checked
        self._are_children_check_states_mixed: bool = False
        self.event_state_changed = Event()

    def __repr__(self) -> str:
        return f"CategoryTreeNode({self.item!s}, {self.check_state.name})"

    @property
    def are_children_check_states_mixed(self) -> bool:
        return self._are_children_check_states_mixed

    def set_check_state(self, *, checked: bool, mode: CategorySelectionMode) -> None:
        """Sets check state of this node and its children, and updates the parents."""

        check_state = convert_bool_to_checkstate(checked=checked)
        if mode == CategorySelectionMode.HIERARCHICAL:
            self._set_check_state_recursive(check_state)
            if self.parent is not None:
                self.parent.update_check_state()
        else:
            self._set_check_state(check_state)
        self.update_are_children_mixed_check_state()

    def _set_check_state(self, check_state: Qt.CheckState) -> None:
        if check_state != self.check_state:
            self.check_state = check_state
            self.event_state_changed(self.item.path)

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

        if self.parent is not None:
            self.parent.update_check_state()

    def update_are_children_mixed_check_state(self) -> None:
        """Updates are_children_check_states_mixed of this node and its parents."""
        if not self._are_children_check_states_mixed and (
            any(child.are_children_check_states_mixed for child in self.children)
            or any(child.check_state != self.check_state for child in self.children)
        ):
            self._are_children_check_states_mixed = True
            self.event_state_changed(self.item.path)
        elif (
            self._are_children_check_states_mixed
            and all(
                not child.are_children_check_states_mixed for child in self.children
            )
            and all(child.check_state == self.check_state for child in self.children)
        ):
            self._are_children_check_states_mixed = False
            self.event_state_changed(self.item.path)

        if self.parent is not None:
            self.parent.update_are_children_mixed_check_state()


def sync_nodes(
    items: Sequence[Category], nodes: Sequence[CategoryTreeNode]
) -> list[CategoryTreeNode]:
    """Accepts flat sequences of items and nodes. Returns new flat nodes."""

    nodes_copy = list(copy(nodes))
    new_nodes: list[CategoryTreeNode] = []

    for item in items:
        node = get_node(item, nodes_copy)
        parent_node = (
            get_node(item.parent, nodes_copy) if item.parent is not None else None
        )
        if node is None:
            node = CategoryTreeNode(item, None)
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
    item: Category, nodes: Sequence[CategoryTreeNode]
) -> CategoryTreeNode | None:
    for node in nodes:
        if node.item == item:
            return node
    return None


def get_node_by_item_path(
    item_path: str, nodes: Sequence[CategoryTreeNode]
) -> CategoryTreeNode | None:
    for node in nodes:
        if node.item.path == item_path:
            return node
    return None


class CheckableCategoryTreeModel(QAbstractItemModel):
    def __init__(
        self,
    ) -> None:
        super().__init__()
        self._flat_nodes: tuple[CategoryTreeNode, ...] = ()
        self._root_nodes: tuple[CategoryTreeNode, ...] = ()
        self._selection_mode = CategorySelectionMode.HIERARCHICAL
        self.event_checked_categories_changed = Event()

    @property
    def flat_categories(self) -> tuple[Category, ...]:
        return tuple(node.item for node in self._flat_nodes)

    @property
    def checked_categories(self) -> tuple[Category, ...]:
        return tuple(
            node.item
            for node in self._flat_nodes
            if node.check_state == Qt.CheckState.Checked
        )

    @property
    def selection_mode(self) -> CategorySelectionMode:
        return self._selection_mode

    def set_selection_mode(self, selection_mode: CategorySelectionMode) -> None:
        if not isinstance(selection_mode, CategorySelectionMode):
            raise TypeError(
                "CheckableCategoryTreeModel.selection_mode must be a SelectionMode."
            )
        self._selection_mode = selection_mode

    def load_flat_categories(self, flat_categories: Collection[Category]) -> None:
        self._flat_nodes = tuple(sync_nodes(flat_categories, self._flat_nodes))
        self._root_nodes = tuple(
            node for node in self._flat_nodes if node.parent is None
        )
        for node in self._flat_nodes:
            node.event_state_changed.clear()
            node.event_state_changed.append(
                lambda item_path: self._node_check_state_changed(item_path)
            )

    def load_checked_categories(self, checked_categories: Collection[Category]) -> None:
        for node in self._flat_nodes:
            node.check_state = (
                Qt.CheckState.Checked
                if node.item in checked_categories
                else Qt.CheckState.Unchecked
            )
        for node in self._flat_nodes:
            node.update_are_children_mixed_check_state()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if parent.isValid():
            if parent.column() != 0:
                return 0
            node: CategoryTreeNode = parent.internalPointer()
            return len(node.children)
        return len(self._root_nodes)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 1 if not parent.isValid() or parent.column() == 0 else 0

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if parent.isValid() and parent.column() != 0:
            return QModelIndex()

        if not parent or not parent.isValid():
            _parent = None
        else:
            _parent: CategoryTreeNode = parent.internalPointer()

        child = self._root_nodes[row] if _parent is None else _parent.children[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex) -> QModelIndex:  # type: ignore[override]
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

    def data(
        self, index: QModelIndex, role: int = ...
    ) -> str | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None
        node: CategoryTreeNode = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            return node.item.name
        if role == Qt.ItemDataRole.CheckStateRole:
            return node.check_state
        if role == Qt.ItemDataRole.FontRole and node.are_children_check_states_mixed:
            return bold_font
        if role == Qt.ItemDataRole.UserRole:
            return node.item.path
        return None

    def setData(  # type: ignore[override]
        self,
        index: QModelIndex,
        value: object,
        role: int = ...,
    ) -> bool | None:
        if role == Qt.ItemDataRole.CheckStateRole:
            item: CategoryTreeNode = index.internalPointer()
            checked = value == Qt.CheckState.Checked.value
            item.set_check_state(checked=checked, mode=self._selection_mode)
            return True
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return FLAGS_CHECKABLE

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def select_all(self) -> None:
        for node in self._root_nodes:
            node.set_check_state(checked=True, mode=CategorySelectionMode.HIERARCHICAL)
        for node in self._flat_nodes:
            node.update_are_children_mixed_check_state()

    def unselect_all(self) -> None:
        for node in self._root_nodes:
            node.set_check_state(checked=False, mode=CategorySelectionMode.HIERARCHICAL)
        for node in self._flat_nodes:
            node.update_are_children_mixed_check_state()

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
        self.event_checked_categories_changed()
