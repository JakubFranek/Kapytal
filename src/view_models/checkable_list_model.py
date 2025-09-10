import unicodedata
from collections.abc import Collection
from typing import Any

from PyQt6.QtCore import QAbstractListModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QListView
from src.presenters.utilities.event import Event

FLAGS_CHECKABLE = (
    Qt.ItemFlag.ItemIsSelectable
    | Qt.ItemFlag.ItemIsEnabled
    | Qt.ItemFlag.ItemIsUserCheckable
)


class CheckableListModel(QAbstractListModel):
    def __init__(
        self, view: QListView, proxy: QSortFilterProxyModel | None, *, sort: bool = True
    ) -> None:
        super().__init__()
        self._list_view = view
        self._items = ()
        self._icons = None
        self._checked_items = []
        self._proxy = proxy
        self._sort = sort
        self.event_checked_items_changed = Event()

    @property
    def items(self) -> tuple[Any]:
        return tuple(self._items)

    @property
    def checked_items(self) -> tuple[Any]:
        return tuple(self._checked_items)

    def load_items(self, values: Collection[Any]) -> None:
        self._items = sorted(values, key=str) if self._sort else list(values)
        self._icons = None

    def load_items_with_icons(self, values: Collection[tuple[Any, QIcon]]) -> None:
        item_tuples = sorted(values, key=lambda x: str(x[0])) if self._sort else values
        self._items = [item_tuple[0] for item_tuple in item_tuples]
        self._icons = [item_tuple[1] for item_tuple in item_tuples]

    def load_checked_items(self, values: Collection[Any]) -> None:
        self._checked_items = sorted(values, key=str) if self._sort else list(values)
        for row in range(len(self._items)):
            index = self.createIndex(row, 0)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
        self.event_checked_items_changed()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if isinstance(parent, QModelIndex) and parent.isValid():
            return 0
        return len(self._items)

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole
    ) -> str | Qt.CheckState | QIcon | None:
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
        if role == Qt.ItemDataRole.DecorationRole and self._icons is not None:
            return self._icons[index.row()]
        return None

    def setData(
        self,
        index: QModelIndex,
        value: Any,  # noqa: ANN401
        role: int,
    ) -> bool | None:
        if role == Qt.ItemDataRole.CheckStateRole:
            item: str = self._items[index.row()]
            checked = value == Qt.CheckState.Checked.value
            if checked and item not in self._checked_items:
                self._checked_items.append(item)
                self.event_checked_items_changed()
            elif not checked and item in self._checked_items:
                self._checked_items.remove(item)
                self.event_checked_items_changed()
            return True
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return FLAGS_CHECKABLE

    def get_selected_item(self) -> Any | None:  # noqa: ANN401
        indexes = self._list_view.selectedIndexes()
        if self._proxy is not None:
            indexes = [self._proxy.mapToSource(index) for index in indexes]
        if len(indexes) == 0:
            return None
        return self._items[indexes[0].row()]

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
