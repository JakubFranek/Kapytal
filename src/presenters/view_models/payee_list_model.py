import typing

from PyQt6.QtCore import QAbstractListModel, QModelIndex, Qt
from PyQt6.QtWidgets import QTableView

from src.models.model_objects.attributes import Attribute


class PayeeListModel(QAbstractListModel):
    COLUMN_HEADERS = {"Payee name"}

    def __init__(
        self,
        view: QTableView,
        payees: tuple[Attribute, ...],
    ) -> None:
        super().__init__()
        self._list = view
        self.payees = payees

    def rowCount(self, index: QModelIndex = ...) -> int:
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self.payees)

    def index(
        self, row: int, column: int, parent: QModelIndex = ...  # noqa: U100
    ) -> QModelIndex:
        if parent.isValid():
            return QModelIndex()
        if not QAbstractListModel.hasIndex(self, row, 0, QModelIndex()):
            return QModelIndex()
        item = self.payees[row]
        return QAbstractListModel.createIndex(self, row, 0, item)

    def data(self, index: QModelIndex, role: Qt.ItemDataRole = ...) -> typing.Any:
        if not index.isValid():
            return None
        payee = self.payees[index.row()]
        if role == Qt.ItemDataRole.DisplayRole:
            return payee.name
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.COLUMN_HEADERS[section]
            return str(section)
        return None

    def pre_add(self) -> None:
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

    def post_add(self) -> None:
        self.endInsertRows()

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def pre_delete_item(self, index: QModelIndex) -> None:
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_delete_item(self) -> None:
        self.endRemoveRows()

    def get_selected_item_index(self) -> QModelIndex:
        indexes = self._list.selectedIndexes()
        if len(indexes) == 0:
            return QModelIndex()
        return indexes[0]

    def get_selected_item(self) -> Attribute | None:
        indexes = self._list.selectedIndexes()
        if len(indexes) == 0:
            return None
        return indexes[0].internalPointer()

    def get_index_from_item(self, item: Attribute | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self.payees.index(item)
        return QAbstractListModel.createIndex(self, row, 0, item)
