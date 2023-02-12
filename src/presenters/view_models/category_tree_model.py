import typing
from collections.abc import Sequence

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtWidgets import QTreeView

from src.models.model_objects.attributes import Category
from src.models.model_objects.currency_objects import Currency
from src.views.constants import CategoryTreeColumns


class CategoryTreeModel(QAbstractItemModel):
    COLUMN_HEADERS = {
        CategoryTreeColumns.COLUMN_NAME: "Name",
        CategoryTreeColumns.COLUMN_TRANSACTIONS: "Transactions",
        CategoryTreeColumns.COLUMN_BALANCE: "Total balance",
    }

    def __init__(
        self,
        view: QTreeView,
        root_items: Sequence[Category],
        base_currency: Currency,
    ) -> None:
        super().__init__()
        self._tree = view
        self.root_categories = tuple(root_items)
        self.base_currency = base_currency

    def rowCount(self, index: QModelIndex = ...) -> int:
        if index.isValid():
            if index.column() != 0:
                return 0
            node: Category = index.internalPointer()
            return len(node.children)
        return len(self.root_categories)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: U100
        return 3 if not index.isValid() or index.column() == 0 else 0

    def index(self, row: int, column: int, _parent: QModelIndex = ...) -> QModelIndex:
        if _parent.isValid() and _parent.column() != 0:
            return QModelIndex()

        if not _parent or not _parent.isValid():
            parent = None
        else:
            parent: Category = _parent.internalPointer()

        if parent is None:
            child = self.root_categories[row]
        else:
            child = parent.children[row]
        if child:
            return QAbstractItemModel.createIndex(self, row, column, child)
        return QModelIndex()

    def parent(self, index: QModelIndex = ...) -> QModelIndex:
        if not index.isValid():
            return QModelIndex()

        child: Category = index.internalPointer()
        parent = child.parent
        if parent is None:
            return QModelIndex()
        grandparent = parent.parent
        if grandparent is None:
            parent_row = self.root_categories.index(parent)
        else:
            parent_row = grandparent.children.index(parent)
        return QAbstractItemModel.createIndex(self, parent_row, 0, parent)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> typing.Any:
        if not index.isValid():
            return None
        column = index.column()
        node: Category = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            if column == CategoryTreeColumns.COLUMN_NAME:
                return node.name
            if column == CategoryTreeColumns.COLUMN_TRANSACTIONS:
                return "0"
            if column == CategoryTreeColumns.COLUMN_BALANCE:
                return "0"

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if column == CategoryTreeColumns.COLUMN_TRANSACTIONS:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            if column == CategoryTreeColumns.COLUMN_BALANCE:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if section == CategoryTreeColumns.COLUMN_TRANSACTIONS:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            if section == CategoryTreeColumns.COLUMN_BALANCE:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.COLUMN_HEADERS[section]
            return str(section)
        return None

    def pre_add(self, parent: Category | None) -> None:
        parent_index = self.get_index_from_item(parent)
        if parent is None:
            row_index = len(self.root_categories)
        else:
            row_index = len(parent.children)
        self.beginInsertRows(parent_index, row_index, row_index)

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
            if new_index > len(self.root_categories):
                new_index = len(self.root_categories)
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

    def get_selected_item(self) -> Category | None:
        indexes = self._tree.selectedIndexes()
        if len(indexes) == 0:
            return None
        return indexes[0].internalPointer()

    def get_index_from_item(self, item: Category | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        parent = item.parent
        if parent is None:
            row = self.root_categories.index(item)
        else:
            row = parent.children.index(item)
        return QAbstractItemModel.createIndex(self, row, 0, item)
