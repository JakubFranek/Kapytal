from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QWidget
from src.models.model_objects.security_objects import SecurityAccount
from src.models.record_keeper import RecordKeeper
from src.view_models.security_account_table_model import SecurityAccountTableModel
from src.views.constants import SecurityAccountTableColumn
from src.views.forms.security_account_form import SecurityAccountForm


class SecurityAccountFormPresenter:
    def __init__(self, parent: QWidget, record_keeper: RecordKeeper) -> None:
        self._parent = parent
        self._record_keeper = record_keeper
        self._view = SecurityAccountForm(parent=parent)

        security_account = next(
            (
                account
                for account in record_keeper.accounts
                if isinstance(account, SecurityAccount)
            ),
            None,
        )

        self._proxy = QSortFilterProxyModel(parent)
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._model = SecurityAccountTableModel(
            view=self._view.table_view,
            security_account=security_account,
            base_currency=record_keeper.base_currency,
            proxy=self._proxy,
        )
        self._proxy.setSourceModel(self._model)
        self._view.table_view.setModel(self._proxy)

    def show(self, security_account: SecurityAccount) -> None:
        self._model.pre_reset_model()
        self._model.security_account = security_account
        self._model.post_reset_model()

        if all(not security.symbol for security in security_account.securities):
            self._view.table_view.hideColumn(SecurityAccountTableColumn.SYMBOL)
        else:
            self._view.table_view.showColumn(SecurityAccountTableColumn.SYMBOL)
        if all(
            security.price.currency == self._model.base_currency
            for security in security_account.securities
        ):
            self._view.table_view.hideColumn(SecurityAccountTableColumn.AMOUNT_NATIVE)
        else:
            self._view.table_view.showColumn(SecurityAccountTableColumn.AMOUNT_NATIVE)
        self._view.table_view.resizeColumnsToContents()
        width, height = self._calculate_table_view_size()
        self._view.resize(width, height)
        self._view.show_form(security_account.path)

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._model.pre_reset_model()
        self._model.base_currency = record_keeper.base_currency
        self._model.post_reset_model()

    def _calculate_table_view_size(self) -> tuple[int, int]:
        """Calculates a good size for the table view which
        should fit it inside the parent widget. Returns (width, height)"""

        table = self._view.table_view
        width = table.horizontalHeader().length() + table.verticalHeader().width()
        height = table.verticalHeader().length() + table.horizontalHeader().height()
        return width + 35, height + 40
