from collections.abc import Collection
from typing import Any

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtWidgets import QApplication, QTableView
from src.models.model_objects.currency_objects import ExchangeRate
from src.models.model_objects.security_objects import Security
from src.presenters.utilities.event import Event
from src.views import icons
from src.views.constants import QuotesUpdateTableColumn

COLUMN_HEADERS = {
    QuotesUpdateTableColumn.ITEM: "Item",
    QuotesUpdateTableColumn.LATEST_DATE: "Latest Date",
    QuotesUpdateTableColumn.LATEST_QUOTE: "Latest Quote",
}
COLUMNS_ALIGNED_RIGHT = {
    QuotesUpdateTableColumn.LATEST_QUOTE,
    QuotesUpdateTableColumn.LATEST_DATE,
}
FLAGS_DEFAULT = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
FLAGS_CHECKABLE = (
    Qt.ItemFlag.ItemIsSelectable
    | Qt.ItemFlag.ItemIsEnabled
    | Qt.ItemFlag.ItemIsUserCheckable
)
ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class QuotesUpdateTableModel(QAbstractTableModel):
    def __init__(
        self,
        view: QTableView,
    ) -> None:
        super().__init__()
        self._table_view = view
        self._items = []
        self._checked_items = []
        self.event_checked_items_changed = Event()

    @property
    def items(self) -> tuple[ExchangeRate | Security, ...]:
        return tuple(item[0] for item in self._items)

    @property
    def checked_items(self) -> tuple[ExchangeRate | Security, ...]:
        return tuple(item[0] for item in self._items if item[0] in self._checked_items)

    def load_data(
        self, values: Collection[tuple[ExchangeRate | Security, str, str]]
    ) -> None:
        self._items = list(values)

    def load_single_data(self, data: tuple[Security | ExchangeRate, str, str]) -> None:
        for item in self._items:
            if item[0] == data[0]:
                index = self._items.index(item)
                break
        else:
            raise ValueError(f"Item not found: {data[0]}")
        self._items[index] = data
        self.dataChanged.emit(self.createIndex(index, 0), self.createIndex(index, 2))
        QApplication.processEvents()

    def load_checked_items(self, values: Collection[ExchangeRate | Security]) -> None:
        self._checked_items = list(values)
        for row in range(len(self._items)):
            index = self.createIndex(row, 0)
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
        self.event_checked_items_changed()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        if isinstance(parent, QModelIndex) and parent.isValid():
            return 0
        return len(self._items)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return 0 if isinstance(parent, QModelIndex) and parent.isValid() else 3

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = ...
    ) -> Any:  # noqa: ANN401
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return COLUMN_HEADERS[section]
        return None

    def data(self, index: QModelIndex, role: int = ...) -> str | None:
        if not index.isValid():
            return None

        item = self._items[index.row()]
        column = index.column()

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(item, column)
        if (
            role == Qt.ItemDataRole.DecorationRole
            and column == QuotesUpdateTableColumn.ITEM
        ):
            return (
                icons.exchange_rate
                if isinstance(item[0], ExchangeRate)
                else icons.security
            )
        if (
            index.column() == QuotesUpdateTableColumn.ITEM
            and role == Qt.ItemDataRole.CheckStateRole
        ):
            return (
                Qt.CheckState.Checked
                if item[0] in self._checked_items
                else Qt.CheckState.Unchecked
            )
        if (
            column in COLUMNS_ALIGNED_RIGHT
            and role == Qt.ItemDataRole.TextAlignmentRole
        ):
            return ALIGNMENT_RIGHT
        return None

    def setData(  # type: ignore[override]
        self,
        index: QModelIndex,
        value: object,
        role: int = ...,
    ) -> bool | None:
        if role == Qt.ItemDataRole.CheckStateRole:
            item = self._items[index.row()]
            checked = value == Qt.CheckState.Checked.value
            if checked and item[0] not in self._checked_items:
                self._checked_items.append(item[0])
                self.event_checked_items_changed()
            elif not checked and item[0] in self._checked_items:
                self._checked_items.remove(item[0])
                self.event_checked_items_changed()
            return True
        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        if index.column() == 0:
            return FLAGS_CHECKABLE
        return FLAGS_DEFAULT

    def pre_reset_model(self) -> None:
        self.beginResetModel()

    def post_reset_model(self) -> None:
        self.endResetModel()

    def _get_display_role_data(
        self, item: tuple[ExchangeRate | Security, str, str], column: int
    ) -> str:
        if column == QuotesUpdateTableColumn.LATEST_QUOTE:
            return item[2]
        if column == QuotesUpdateTableColumn.LATEST_DATE:
            return item[1]
        _item = item[0]
        if isinstance(_item, Security):
            return _item.symbol
        return str(_item)
