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
        del column
        if parent.isValid():
            return QModelIndex()
        if not QAbstractListModel.hasIndex(self, row, 0, QModelIndex()):
            return QModelIndex()
        item = self._items[row]
        return QAbstractListModel.createIndex(self, row, 0, item)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> str | None:
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return self._items[index.row()]
        return None

    def get_selected_item(self) -> str | None:
        proxy_indexes = self._list_view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return None
        return source_indexes[0].internalPointer()
