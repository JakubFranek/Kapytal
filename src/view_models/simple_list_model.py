import unicodedata
from collections.abc import Collection

from PyQt6.QtCore import QAbstractListModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QListView


class SimpleListModel(QAbstractListModel):
    def __init__(
        self, view: QListView, items: Collection[str], proxy: QSortFilterProxyModel
    ) -> None:
        super().__init__()
        self._list_view = view
        self._items: list[str] = items
        self._proxy = proxy

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self._items)

    def index(self, row: int, column: int, parent: QModelIndex = ...) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if row < 0 or column < 0:
            return QModelIndex()
        if row >= len(self._items) or column >= 1:
            return QModelIndex()

        item = self._items[row]
        return QAbstractListModel.createIndex(self, row, 0, item)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> str | None:
        if not index.isValid():
            return None
        item = index.internalPointer()
        if role == Qt.ItemDataRole.DisplayRole:
            return item
        if role == Qt.ItemDataRole.UserRole:
            return unicodedata.normalize("NFD", str(item))
        return None

    def get_selected_item(self) -> str | None:
        proxy_indexes = self._list_view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return None
        return source_indexes[0].internalPointer()
