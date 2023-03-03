import typing
from collections.abc import Collection
from pathlib import Path

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt
from PyQt6.QtWidgets import QListView


class BackupPathsListModel(QAbstractListModel):
    def __init__(self, view: QListView, paths: Collection[Path]) -> None:
        super().__init__()
        self._list = view
        self.paths = tuple(paths)

    @property
    def paths(self) -> tuple[Path]:
        return self._paths

    @paths.setter
    def paths(self, paths: Collection[Path]) -> None:
        self._paths = tuple(paths)

    def rowCount(self, index: QModelIndex = ...) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self.paths)

    def index(
        self, row: int, column: int, parent: QModelIndex = ...  # noqa: U100
    ) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if not QAbstractListModel.hasIndex(self, row, 0, QModelIndex()):
            return QModelIndex()
        item = self.paths[row]
        return QAbstractListModel.createIndex(self, row, 0, item)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> typing.Any:
        if not index.isValid():
            return None
        path = self.paths[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return str(path)
        return None

    def pre_add(self) -> None:
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

    def post_add(self) -> None:
        self.endInsertRows()

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def pre_remove_item(self, item: Path) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def get_selected_item_index(self) -> QModelIndex:
        indexes = self._list.selectedIndexes()
        if len(indexes) == 0:
            return QModelIndex()
        return indexes[0]

    def get_selected_item(self) -> Path | None:
        indexes = self._list.selectedIndexes()
        if len(indexes) == 0:
            return None
        return indexes[0].internalPointer()

    def get_index_from_item(self, item: Path | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self._paths.index(item)
        return QAbstractListModel.createIndex(self, row, 0, item)
