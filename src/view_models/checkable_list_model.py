import unicodedata
from collections.abc import Collection
from typing import Any

from PyQt6.QtCore import QAbstractListModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QListView


class CheckableListModel(QAbstractListModel):
    def __init__(
        self,
        view: QListView,
        items: Collection[Any],
        checked_items: Collection[Any],
        proxy: QSortFilterProxyModel,
        *,
        sort: bool = True
    ) -> None:
        super().__init__()
        self._list_view = view
        self._items = sorted(items, key=str) if sort else items
        self._checked_items = sorted(checked_items, key=str) if sort else checked_items
        self._proxy = proxy
        self._sort = sort

    @property
    def items(self) -> tuple[Any]:
        return tuple(self._items)

    @items.setter
    def items(self, values: Collection[Any]) -> None:
        self._items = sorted(values, key=str) if self._sort else values

    @property
    def checked_items(self) -> tuple[Any]:
        return tuple(self._checked_items)

    @checked_items.setter
    def checked_items(self, values: Collection[Any]) -> None:
        self._checked_items = sorted(values, key=str) if self._sort else list(values)

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self._items)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> str | None:
        if not index.isValid():
            return None
        item = self._items[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return str(item)
        if role == Qt.ItemDataRole.CheckStateRole:
            return (
                Qt.CheckState.Checked
                if item in self._checked_items
                else Qt.CheckState.Unchecked
            )
        if role == Qt.ItemDataRole.UserRole:
            return unicodedata.normalize("NFD", str(item))
        return None

    def setData(  # noqa: N802
        self, index: QModelIndex, value: Any, role: int = ...  # noqa: ANN401
    ) -> bool | None:
        if role == Qt.ItemDataRole.CheckStateRole:
            item: str = self._items[index.row()]
            checked = value == Qt.CheckState.Checked.value
            if checked and item not in self._checked_items:
                self._checked_items.append(item)
            elif not checked and item in self._checked_items:
                self._checked_items.remove(item)
            return True
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return (
            Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsUserCheckable
        )

    def get_selected_item(self) -> Any | None:
        indexes = self._list_view.selectedIndexes()
        if self._proxy:
            indexes = [self._proxy.mapToSource(index) for index in indexes]
        if len(indexes) == 0:
            return None
        return self._items[indexes[0].row()]

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
