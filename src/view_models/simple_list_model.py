import unicodedata
from collections.abc import Collection

from PyQt6.QtCore import QAbstractListModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QListView


class SimpleListModel(QAbstractListModel):
    def __init__(self, view: QListView, proxy: QSortFilterProxyModel) -> None:
        super().__init__()
        self._list_view = view
        self._items: tuple[str, ...] = ()
        self._proxy = proxy

    def load_items(self, items: Collection[str]) -> None:
        self._items = tuple(items)

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        if isinstance(parent, QModelIndex) and parent.isValid():
            return 0
        return len(self._items)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole) -> str | None:
        if not index.isValid():
            return None
        item = self._items[index.row()]
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
        return self._items[source_indexes[0].row()]
