import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.account_filter import AccountFilter
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.view_models.checkable_account_tree_model import CheckableAccountTreeModel
from src.views.forms.transaction_filter_form import (
    AccountFilterMode,
    TransactionFilterForm,
)


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
        if self._form.account_filter_mode == AccountFilterMode.ACCOUNT_TREE:
            return

        if account_filter.mode == FilterMode.OFF:
            self._form.account_filter_mode = AccountFilterMode.ACCOUNT_TREE
        elif account_filter.mode == FilterMode.KEEP:
            self._model.checked_accounts = account_filter.accounts
        else:
            self._model.checked_accounts = [
                account
                for account in self._record_keeper.accounts
                if account not in account_filter.accounts
            ]

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        logging.debug(f"Filtering Account Tree items: {pattern=}")
        self._proxy.setFilterWildcard(pattern)
        self._form.account_tree_view.expandAll()

    def _initialize_models(self) -> None:
        self._proxy = QSortFilterProxyModel(self._form)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setRecursiveFilteringEnabled(True)  # noqa: FBT003
        self._proxy.setFilterRole(Qt.ItemDataRole.UserRole)

        self._model = CheckableAccountTreeModel(
            self._form.account_tree_view, self._proxy, self._record_keeper.account_items
        )

        self._proxy.setSourceModel(self._model)
        self._form.account_tree_view.setModel(self._proxy)

    def _connect_to_signals(self) -> None:
        self._form.signal_accounts_search_text_changed.connect(self._filter)
        self._form.signal_accounts_select_all.connect(lambda: self._model.select_all())
        self._form.signal_accounts_unselect_all.connect(
            lambda: self._model.unselect_all()
        )
        self._form.signal_accounts_expand_all_below.connect(
            lambda: self._expand_all_below_current_selection()
        )
        self._form.signal_accounts_select_all_cash_accounts_below.connect(
            self._select_all_cash_accounts_below
        )
        self._form.signal_accounts_select_all_security_accounts_below.connect(
            self._select_all_security_accounts_below
        )
        self._form.account_tree_view.selectionModel().selectionChanged.connect(
            self._selection_changed
        )

    def _expand_all_below_current_selection(self) -> None:
        indexes = self._form.account_tree_view.selectedIndexes()
        if len(indexes) == 0:
            raise ValueError("No index to expand recursively selected.")
        item = self._model.get_selected_item()
        logging.debug(f"Expanding all nodes below {item}")
        self._form.account_tree_view.expandRecursively(indexes[0])

    def _select_all_cash_accounts_below(self) -> None:
        account_group = self._model.get_selected_item()
        if not isinstance(account_group, AccountGroup):
            raise TypeError(f"Selected item is not an AccountGroup: {account_group}")
        logging.debug(f"Selecting all Cash Accounts below path='{account_group.path}'")
        self._model.select_all_cash_accounts_below(account_group)

    def _select_all_security_accounts_below(self) -> None:
        account_group = self._model.get_selected_item()
        if not isinstance(account_group, AccountGroup):
            raise TypeError(f"Selected item is not an AccountGroup: {account_group}")
        logging.debug(
            f"Selecting all Security Accounts below path='{account_group.path}'"
        )
        self._model.select_all_security_accounts_below(account_group)

    def _selection_changed(self) -> None:
        item = self._model.get_selected_item()
        account_group_selected = isinstance(item, AccountGroup)
        self._form.set_account_filter_action_states(
            account_group_selected=account_group_selected
        )
