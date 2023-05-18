import unicodedata
from collections.abc import Collection, Sequence

from PyQt6.QtCore import QAbstractItemModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QTreeView
from src.models.model_objects.attributes import Category
from src.models.utilities.calculation import CategoryStats
from src.views.constants import CategoryTreeColumn

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class CategoryTreeModel(QAbstractItemModel):
    COLUMN_HEADERS = {
        CategoryTreeColumn.NAME: "Name",
        CategoryTreeColumn.TRANSACTIONS: "Transactions",
        CategoryTreeColumn.BALANCE: "Balance",
    }

    def __init__(
        self,
        tree_view: QTreeView,
        root_categories: Sequence[Category],
        category_stats: dict[Category, CategoryStats],
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._tree_view = tree_view
        self.root_categories = root_categories
        self._category_stats_dict: dict[Category, CategoryStats] = category_stats
        self._proxy = proxy

    @property
    def root_categories(self) -> tuple[Category, ...]:
        return self._root_categories

    @root_categories.setter
    def root_categories(self, root_categories: Collection[Category]) -> None:
        self._root_categories = tuple(root_categories)

    def load_category_stats_dict(
        self, category_stats_dict: dict[Category, CategoryStats]
    ) -> None:
        self._category_stats_dict = category_stats_dict

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if index.isValid():
            if index.column() != 0:
                return 0
            node: Category = index.internalPointer()
            return len(node.children)
        return len(self._root_categories)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        return 3 if not index.isValid() or index.column() == 0 else 0

    def index(self, row: int, column: int, _parent: QModelIndex = ...) -> QModelIndex:
        if _parent.isValid() and _parent.column() != 0:
            return QModelIndex()

        if not _parent or not _parent.isValid():
            parent = None
        else:
            parent: Category = _parent.internalPointer()

        child = self._root_categories[row] if parent is None else parent.children[row]
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

    def data(  # noqa: PLR0911
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None
        column = index.column()
        category: Category = index.internalPointer()
        stats = self._category_stats_dict[category]
        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(column, category, stats)
        if role == Qt.ItemDataRole.UserRole:
            if column == CategoryTreeColumn.NAME:
                return unicodedata.normalize("NFD", category.name)
            if column == CategoryTreeColumn.TRANSACTIONS:
                return stats.transactions_total
            if column == CategoryTreeColumn.BALANCE:
                return float(stats.balance.value_normalized)
        if role == Qt.ItemDataRole.UserRole + 1 and column == CategoryTreeColumn.NAME:
            return category.path
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
        self, column: int, category: Category, stats: CategoryStats
    ) -> str | int | None:
        if column == CategoryTreeColumn.NAME:
            return category.name
        if column == CategoryTreeColumn.TRANSACTIONS:
            if len(category.children) == 0:
                return stats.transactions_total
            return f"{stats.transactions_total} ({stats.transactions_self})"
        if column == CategoryTreeColumn.BALANCE:
            return stats.balance.to_str_rounded()
        return None

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.TextAlignmentRole:
            if section == CategoryTreeColumn.TRANSACTIONS:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            if section == CategoryTreeColumn.BALANCE:
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
        proxy_indexes = self._tree_view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return QModelIndex()
        return source_indexes[0]

    def get_selected_item(self) -> Category | None:
        proxy_indexes = self._tree_view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return None
        return source_indexes[0].internalPointer()

    def get_index_from_item(self, item: Category | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        parent = item.parent
        if parent is None:
            row = self.root_categories.index(item)
        else:
            row = parent.children.index(item)
        return QAbstractItemModel.createIndex(self, row, 0, item)
