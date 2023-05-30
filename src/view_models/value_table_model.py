from collections.abc import Sequence
from datetime import date
from decimal import Decimal
from enum import Enum, auto

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QTableView
from src.views.constants import ValueTableColumn

ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class ValueType(Enum):
    EXCHANGE_RATE = auto()
    SECURITY_PRICE = auto()


class ValueTableModel(QAbstractTableModel):
    def __init__(
        self,
        view: QTableView,
        proxy: QSortFilterProxyModel,
        type_: ValueType,
    ) -> None:
        super().__init__()
        self._view = view
        self._proxy = proxy
        self._type = type_
        self._data = ()

        self.COLUMN_HEADERS = {ValueTableColumn.DATE: "Date"}
        if type_ == ValueType.EXCHANGE_RATE:
            self.COLUMN_HEADERS[ValueTableColumn.VALUE] = "Rate"
        else:
            self.COLUMN_HEADERS[ValueTableColumn.VALUE] = "Price"

    def load_data(self, date_value_pairs: Sequence[tuple[date, Decimal]]) -> None:
        self._data = tuple(date_value_pairs)

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self._data)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802, ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(self.COLUMN_HEADERS)
        return self._column_count

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | int | float | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(index.column(), self._data[index.row()])
        if role == Qt.ItemDataRole.UserRole:
            return self._get_user_role_data(index.column(), self._data[index.row()])
        column = index.column()
        if role == Qt.ItemDataRole.TextAlignmentRole and (
            column == ValueTableColumn.VALUE
        ):
            return ALIGNMENT_RIGHT
        return None

    def _get_display_role_data(
        self, column: int, data: tuple[date, Decimal]
    ) -> str | int | None:
        if column == ValueTableColumn.DATE:
            return data[0].strftime("%d.%m.%Y")
        if column == ValueTableColumn.VALUE:
            return f"{data[1]:,}"
        return None

    def _get_user_role_data(
        self, column: int, data: tuple[date, Decimal]
    ) -> str | int | float | None:
        # used for sorting
        if column == ValueTableColumn.DATE:
            return data[0].toordinal()
        if column == ValueTableColumn.VALUE:
            return float(data[1])
        return None

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.COLUMN_HEADERS[section]
            return str(section)
        return None

    def pre_add(self) -> None:
        self._proxy.setDynamicSortFilter(False)  # noqa: FBT003
        self._view.setSortingEnabled(False)  # noqa: FBT003
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())

    def post_add(self) -> None:
        self.endInsertRows()
        self._view.setSortingEnabled(True)  # noqa: FBT003
        self._proxy.setDynamicSortFilter(True)  # noqa: FBT003

    def pre_reset_model(self) -> None:
        self._view.setSortingEnabled(False)  # noqa: FBT003
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()
        self._view.setSortingEnabled(True)  # noqa: FBT003

    def pre_remove_item(self, date_: date) -> None:
        index = self.get_index_from_date(date_)
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def get_selected_dates(self) -> tuple[date, ...]:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        return tuple(self._data[index.row()][0] for index in source_indexes)

    def get_index_from_date(self, date_: date) -> QModelIndex:
        for index, data in enumerate(self._data):
            if data[0] == date_:
                row = index
                break
        else:
            raise ValueError(f"Date {date_.strftime('%Y-%m-%d')} not found")
        return QAbstractTableModel.createIndex(self, row, 0)
