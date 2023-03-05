import logging
from collections.abc import Collection

from PyQt6.QtCore import QSortFilterProxyModel, Qt

from src.models.base_classes.account import Account
from src.models.record_keeper import RecordKeeper
from src.presenters.utilities.event import Event
from src.view_models.transaction_table_model import TransactionTableModel
from src.views.widgets.transaction_table_widget import TransactionTableWidget

# TODO: show/hide columns based on selection


class TransactionsPresenter:
    event_data_changed = Event()

    def __init__(
        self, view: TransactionTableWidget, record_keeper: RecordKeeper
    ) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._valid_accounts = record_keeper.accounts

        self._proxy_model = QSortFilterProxyModel(self._view.tableView)
        self._model = TransactionTableModel(
            self._view.tableView,
            [],
            self._record_keeper.base_currency,
            self._proxy_model,
        )
        self.update_model_data()
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy_model.sort(0, Qt.SortOrder.DescendingOrder)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy_model.setFilterKeyColumn(-1)

        self._view.tableView.setModel(self._proxy_model)
        self._view.resize_table_to_contents()
        self._view.signal_search_text_changed.connect(self._filter)

    @property
    def valid_accounts(self) -> tuple[Account, ...]:
        return self._valid_accounts

    @valid_accounts.setter
    def valid_accounts(self, accounts: Collection[Account]) -> None:
        self._valid_accounts = tuple(accounts)
        self.reset_model()

    def reset_model(self) -> None:
        self._model.pre_reset_model()
        self.update_model_data()
        self._model.post_reset_model()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._valid_accounts = record_keeper.accounts
        self.reset_model()
        self._view.resize_table_to_contents()

    def update_model_data(self) -> None:
        if len(self._valid_accounts) == 0:
            self._model.transactions = ()
        else:
            self._model.transactions = [
                transaction
                for transaction in self._record_keeper.transactions
                if transaction.is_accounts_related(self._valid_accounts)
            ]
        self._model.base_currency = self._record_keeper.base_currency

    def _filter(self) -> None:
        pattern = self._view.search_bar_text
        logging.debug(f"Filtering Transaction: {pattern=}")
        self._proxy_model.setFilterWildcard(pattern)
