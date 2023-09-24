from collections.abc import Collection
from pathlib import Path

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt
from PyQt6.QtWidgets import QListView


class BackupPathsListModel(QAbstractListModel):
    def __init__(self, view: QListView) -> None:
        super().__init__()
        self._view = view
        self._paths: tuple[Path, ...] = ()

    @property
    def paths(self) -> tuple[Path, ...]:
        return self._paths

    def load_paths(self, paths: Collection[Path]) -> None:
        self._paths = tuple(paths)

    def rowCount(self, index: QModelIndex = ...) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self.paths)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> str | None:
        if not index.isValid():
            return None
        if role == Qt.ItemDataRole.DisplayRole:
            return str(self._paths[index.row()])
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

    def get_selected_item(self) -> Path | None:
        indexes = self._view.selectedIndexes()
        if len(indexes) == 0:
            return None
        return self._paths[indexes[0].row()]

    def get_index_from_item(self, item: Path | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self._paths.index(item)
        return QAbstractListModel.createIndex(self, row, 0)
