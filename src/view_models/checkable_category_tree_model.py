from collections.abc import Collection, Sequence

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, Qt
from PyQt6.QtWidgets import QTreeView
from src.models.model_objects.attributes import Category


class CheckableCategoryTreeModel(QAbstractItemModel):
    def __init__(
        self,
        tree_view: QTreeView,
        root_categories: Sequence[Category],
    ) -> None:
        super().__init__()
        self._tree_view = tree_view
        self.root_categories = root_categories

    @property
    def root_categories(self) -> tuple[Category, ...]:
        return self._root_categories

    @root_categories.setter
    def root_categories(self, root_categories: Collection[Category]) -> None:
        self._root_categories = tuple(root_categories)

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if index.isValid():
            if index.column() != 0:
                return 0
            node: Category = index.internalPointer()
            return len(node.children)
        return len(self.root_categories)

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
            parent: Category = _parent.internalPointer()

        child = self.root_categories[row] if parent is None else parent.children[row]
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

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None
        category: Category = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            return category.name
        return None

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
