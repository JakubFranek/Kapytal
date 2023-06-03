import unicodedata
from collections.abc import Collection

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QTableView
from src.models.model_objects.security_objects import Security
from src.views.constants import SecurityTableColumn

ALIGNMENT_LEFT = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
ALIGNMENT_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


class SecurityTableModel(QAbstractTableModel):
    COLUMN_HEADERS = {
        SecurityTableColumn.NAME: "Name",
        SecurityTableColumn.SYMBOL: "Symbol",
        SecurityTableColumn.TYPE: "Type",
        SecurityTableColumn.PRICE: "Latest price",
        SecurityTableColumn.LAST_DATE: "Latest date",
    }

    def __init__(
        self,
        view: QTableView,
        proxy: QSortFilterProxyModel,
    ) -> None:
        super().__init__()
        self._view = view
        self._securities = ()
        self._proxy = proxy

    @property
    def securities(self) -> tuple[Security, ...]:
        return self._securities

    def load_securities(self, securities: Collection[Security]) -> None:
        self._securities = tuple(securities)

    def rowCount(self, index: QModelIndex = ...) -> int:  # noqa: N802
        if isinstance(index, QModelIndex) and index.isValid():
            return 0
        return len(self._securities)

    def columnCount(self, index: QModelIndex = ...) -> int:  # noqa: N802, ARG002
        if not hasattr(self, "_column_count"):
            self._column_count = len(self.COLUMN_HEADERS)
        return self._column_count

    def headerData(  # noqa: N802
        self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole = ...
    ) -> str | int | None:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.COLUMN_HEADERS[section]
            return str(section)
        if (
            role == Qt.ItemDataRole.TextAlignmentRole
            and section == SecurityTableColumn.LAST_DATE
        ):
            return ALIGNMENT_LEFT
        return None

    def data(
        self, index: QModelIndex, role: Qt.ItemDataRole = ...
    ) -> str | Qt.AlignmentFlag | None:
        if not index.isValid():
            return None

        column = index.column()
        security = self._securities[index.row()]

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_role_data(column, security)
        if role == Qt.ItemDataRole.UserRole:
            return self._get_user_role_data(column, security)
        if (
            role == Qt.ItemDataRole.TextAlignmentRole
            and column == SecurityTableColumn.PRICE
        ):
            return ALIGNMENT_RIGHT
        return None

    def _get_display_role_data(self, column: int, security: Security) -> str | None:
        if column == SecurityTableColumn.NAME:
            return security.name
        if column == SecurityTableColumn.SYMBOL:
            return security.symbol
        if column == SecurityTableColumn.TYPE:
            return security.type_
        if column == SecurityTableColumn.PRICE:
            return security.price.to_str_normalized()
        if column == SecurityTableColumn.LAST_DATE:
            latest_date = security.latest_date
            return (
                latest_date.strftime("%d.%m.%Y") if latest_date is not None else "None"
            )
        return None

    def _get_user_role_data(  # noqa: PLR0911
        self,
        column: int,
        security: Security,
    ) -> str | None:
        if column == SecurityTableColumn.NAME:
            return unicodedata.normalize("NFD", security.name)
        if column == SecurityTableColumn.SYMBOL:
            return unicodedata.normalize("NFD", security.symbol)
        if column == SecurityTableColumn.TYPE:
            return unicodedata.normalize("NFD", security.type_)
        if column == SecurityTableColumn.PRICE:
            amount = security.price
            return float(amount.value_normalized)
        if column == SecurityTableColumn.LAST_DATE:
            latest_date = security.latest_date
            if latest_date is not None:
                return latest_date.toordinal()
            return None
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

    def pre_remove_item(self, item: Security) -> None:
        index = self.get_index_from_item(item)
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())

    def post_remove_item(self) -> None:
        self.endRemoveRows()

    def get_selected_item(self) -> Security | None:
        proxy_indexes = self._view.selectedIndexes()
        source_indexes = [self._proxy.mapToSource(index) for index in proxy_indexes]
        if len(source_indexes) == 0:
            return None
        return self._securities[source_indexes[0].row()]

    def get_index_from_item(self, item: Security | None) -> QModelIndex:
        if item is None:
            return QModelIndex()
        row = self.securities.index(item)
        return QAbstractTableModel.createIndex(self, row, 0)
