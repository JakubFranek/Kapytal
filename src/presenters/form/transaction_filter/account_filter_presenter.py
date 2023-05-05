import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.base_classes.account import Account
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.account_filter import AccountFilter
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.view_models.checkable_account_tree_model import CheckableAccountTreeModel
from src.views.forms.transaction_filter_form import TransactionFilterForm


class AccountFilterPresenter:
    def __init__(
        self, form: TransactionFilterForm, record_keeper: RecordKeeper
    ) -> None:
        self._form = form
        self._record_keeper = record_keeper
        self._initialize_models()
        self._connect_to_signals()

    @property
    def checked_accounts(self) -> tuple[Account, ...]:
        return self._model.checked_accounts

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._model.pre_reset_model()
        self._model.flat_account_items = record_keeper.account_items
        self._model.post_reset_model()

    def load_from_account_filter(
        self,
        account_filter: AccountFilter,
    ) -> None:
        self._model.pre_reset_model()
        if account_filter.mode == FilterMode.OFF:
            pass
        elif account_filter.mode == FilterMode.KEEP:
            self._model.checked_accounts = account_filter.accounts
        else:
            self._model.checked_accounts = [
                account
                for account in self._record_keeper.accounts
                if account not in account_filter.accounts
            ]
        self._model.post_reset_model()

    # FIXME: weird filtering: typing "Degiro" does not show children...
    # potential solution: filter based on user role returning full path
    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        logging.debug(f"Filtering Account Tree items: {pattern=}")
        self._proxy.setFilterWildcard(pattern)

    def _initialize_models(self) -> None:
        self._proxy = QSortFilterProxyModel(self._form)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setRecursiveFilteringEnabled(True)  # noqa: FBT003

        self._model = CheckableAccountTreeModel(
            self._form.account_tree_view, self._proxy, self._record_keeper.account_items
        )

        self._proxy.setSourceModel(self._model)
        self._form.account_tree_view.setModel(self._proxy)

    def _connect_to_signals(self) -> None:
        self._form.signal_accounts_search_text_changed.connect(
            lambda pattern: self._filter(pattern)
        )
