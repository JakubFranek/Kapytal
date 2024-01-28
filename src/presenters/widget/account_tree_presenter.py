import logging

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.base_classes.account import Account
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.currency_objects import (
    ConversionFactorNotFoundError,
)
from src.models.model_objects.security_objects import SecurityAccount
from src.models.record_keeper import RecordKeeper
from src.presenters.dialog.account_group_dialog_presenter import (
    AccountGroupDialogPresenter,
)
from src.presenters.dialog.cash_account_dialog_presenter import (
    CashAccountDialogPresenter,
)
from src.presenters.dialog.security_account_dialog_presenter import (
    SecurityAccountDialogPresenter,
)
from src.presenters.form.security_account_form_presenter import (
    SecurityAccountFormPresenter,
)
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.account_tree_model import AccountTreeModel
from src.views.constants import AccountTreeColumn
from src.views.utilities.message_box_functions import ask_yes_no_question
from src.views.widgets.account_tree_widget import AccountTreeWidget


class AccountTreePresenter:
    event_data_changed = Event()
    event_check_state_changed = Event()

    def __init__(self, view: AccountTreeWidget, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._initialize_models()

        self._account_group_dialog_presenter = AccountGroupDialogPresenter(
            view, self._model, record_keeper
        )
        self._cash_account_dialog_presenter = CashAccountDialogPresenter(
            view, self._model, record_keeper
        )
        self._security_account_dialog_presenter = SecurityAccountDialogPresenter(
            view, self._model, record_keeper
        )
        self._security_account_form_presenter = SecurityAccountFormPresenter(
            view, record_keeper
        )

        self._initialize_signals()
        self._initialize_events()
        self._view.finalize_setup()
        self._view.treeView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)
        self._check_state_changed()

    @property
    def checked_accounts(self) -> frozenset[Account]:
        return self._model.get_checked_accounts()

    @property
    def checked_account_items(self) -> frozenset[Account | AccountGroup]:
        return self._model.get_checked_account_items()

    def set_widget_visibility(self, *, visible: bool) -> None:
        if visible and self._view.isHidden():
            logging.debug("Showing AccountTreeWidget")
            self._view.show()
        elif not visible and not self._view.isHidden():
            logging.debug("Hiding AccountTreeWidget")
            self._view.hide()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._model.pre_reset_model()
        self.update_model_data()
        self._model.post_reset_model()
        self._security_account_form_presenter.load_record_keeper(record_keeper)
        self._account_group_dialog_presenter.load_record_keeper(record_keeper)
        self._cash_account_dialog_presenter.load_record_keeper(record_keeper)
        self._security_account_dialog_presenter.load_record_keeper(record_keeper)
        self.set_check_state_all(visible=True)
        self._set_native_balance_column_visibility()

    def refresh_view(self) -> None:
        self._view.refresh()

    def update_geometries(self) -> None:
        self._view.treeView.updateGeometries()

    def update_model_data(self) -> None:
        self._model.load_data(
            self._record_keeper.account_items, self._record_keeper.base_currency
        )
        hide_native = all(
            account.currency == self._record_keeper.base_currency
            for account in self._record_keeper.cash_accounts
        )
        self._view.treeView.setColumnHidden(
            AccountTreeColumn.BALANCE_NATIVE, hide_native
        )
        self._set_native_balance_column_visibility()
        self._update_checked_account_balance()

    def expand_all_below(self) -> None:
        indexes = self._view.treeView.selectedIndexes()
        if len(indexes) == 0:
            raise InvalidOperationError("No index to expand recursively selected.")
        item = self._model.get_selected_item()
        logging.debug(f"Expanding all nodes below {item}")
        self._view.treeView.expandRecursively(indexes[0])  # view index required here

    def remove_item(self) -> None:
        item = self._model.get_selected_item()
        if item is None:
            raise InvalidOperationError("Cannot delete non-existent item.")

        if isinstance(item, CashAccount) and item.initial_balance.value_normalized > 0:
            logging.debug(
                "Deletion of CashAccount with non-zero initial balance"
                "requested, asking the user for confirmation"
            )
            if not ask_yes_no_question(
                self._view,
                f"<html>Cash Account <b>{item.path}</b> has non-zero initial balance "
                f"({item.initial_balance.to_str_rounded()}).<br/>Delete anyway?</html>",
                "Are you sure?",
            ):
                logging.debug("User cancelled the CashAccount deletion")
                return

        logging.info(f"Removing {item.__class__.__name__} at path='{item.path}'")
        try:
            if isinstance(item, AccountGroup):
                self._record_keeper.remove_account_group(item.path)
            else:
                self._record_keeper.remove_account(item.path)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._model.pre_remove_item(item)
        self.update_model_data()
        self._model.post_remove_item()
        self.event_data_changed()

    def _initialize_models(self) -> None:
        self._proxy = QSortFilterProxyModel(self._view)
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setFilterRole(Qt.ItemDataRole.UserRole + 1)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setRecursiveFilteringEnabled(True)
        self._model = AccountTreeModel(
            view=self._view.treeView,
            proxy=self._proxy,
        )
        self._proxy.setSourceModel(self._model)
        self._view.treeView.setModel(self._proxy)

    def _initialize_signals(self) -> None:
        self._view.signal_selection_changed.connect(self._selection_changed)
        self._view.signal_expand_below.connect(self.expand_all_below)

        self._view.signal_show_all.connect(
            lambda: self.set_check_state_all(visible=True)
        )
        self._view.signal_show_selection_only.connect(self._set_check_state_only)
        self._view.signal_hide_all.connect(
            lambda: self.set_check_state_all(visible=False)
        )
        self._view.signal_select_all_cash_accounts_below.connect(
            self._check_all_cash_accounts_below
        )
        self._view.signal_select_all_security_accounts_below.connect(
            self._check_all_security_accounts_below
        )

        self._view.signal_add_account_group.connect(
            self._account_group_dialog_presenter.run_add_dialog
        )
        self._view.signal_add_security_account.connect(
            self._security_account_dialog_presenter.run_add_dialog
        )
        self._view.signal_add_cash_account.connect(
            self._cash_account_dialog_presenter.run_add_dialog
        )

        self._view.signal_edit_item.connect(self._edit_item)
        self._view.signal_delete_item.connect(self.remove_item)

        self._view.signal_show_securities.connect(self._show_security_account_contents)

        self._view.signal_search_text_changed.connect(self._filter)
        self._view.signal_tree_double_clicked.connect(self._double_clicked)

        self._model.signal_check_state_changed.connect(self._check_state_changed)

        self._view.treeView.expanded.connect(self._set_native_balance_column_visibility)
        self._view.treeView.collapsed.connect(
            self._set_native_balance_column_visibility
        )
        self._view.signal_tree_expanded_state_changed.connect(
            self._set_native_balance_column_visibility
        )

        self._selection_changed()  # called to ensure context menu is OK at start of run

    def _initialize_events(self) -> None:
        self._account_group_dialog_presenter.event_update_model.append(
            self.update_model_data
        )
        self._cash_account_dialog_presenter.event_update_model.append(
            self.update_model_data
        )
        self._security_account_dialog_presenter.event_update_model.append(
            self.update_model_data
        )

        self._account_group_dialog_presenter.event_data_changed.append(
            self.event_data_changed
        )
        self._cash_account_dialog_presenter.event_data_changed.append(
            self.event_data_changed
        )
        self._security_account_dialog_presenter.event_data_changed.append(
            self.event_data_changed
        )

        self._account_group_dialog_presenter.event_selection_changed.append(
            self._selection_changed
        )
        self._cash_account_dialog_presenter.event_selection_changed.append(
            self._selection_changed
        )
        self._security_account_dialog_presenter.event_selection_changed.append(
            self._selection_changed
        )

    def _selection_changed(self) -> None:
        item = self._model.get_selected_item()

        enable_modify_object = item is not None
        enable_add_objects = item is None or isinstance(item, AccountGroup)
        enable_expand_below = isinstance(item, AccountGroup)
        enable_show_securities = isinstance(item, SecurityAccount)

        self._view.enable_actions(
            enable_add_objects=enable_add_objects,
            enable_modify_object=enable_modify_object,
            enable_expand_below=enable_expand_below,
            enable_show_securities=enable_show_securities,
        )

    def _update_checked_account_balance(self) -> None:
        if self._record_keeper.base_currency is not None:
            try:
                total = sum(
                    (
                        item.get_balance(self._record_keeper.base_currency)
                        for item in self.checked_accounts
                    ),
                    start=self._record_keeper.base_currency.zero_amount,
                )
                total = total.to_str_rounded()
            except ConversionFactorNotFoundError:
                total = "Error!"
        else:
            total = "N/A"
        self._view.set_checked_account_balance(total)

    def set_check_state_all(self, *, visible: bool) -> None:
        self._model.set_check_state_all(checked=visible)
        self._view.refresh()
        self._check_state_changed()

    def _set_check_state_only(self) -> None:
        self._model.set_selected_check_state(checked=True, only=True)
        self._view.refresh()
        self._check_state_changed()

    def _check_all_cash_accounts_below(self) -> None:
        account_group = self._model.get_selected_item()
        if not isinstance(account_group, AccountGroup):
            raise TypeError(f"Selected item is not an AccountGroup: {account_group}")
        logging.debug(f"Selecting all Cash Accounts below path='{account_group.path}'")
        self._model.check_all_cash_accounts_below(account_group)
        self._check_state_changed()

    def _check_all_security_accounts_below(self) -> None:
        account_group = self._model.get_selected_item()
        if not isinstance(account_group, AccountGroup):
            raise TypeError(f"Selected item is not an AccountGroup: {account_group}")
        logging.debug(
            f"Selecting all Security Accounts below path='{account_group.path}'"
        )
        self._model.check_all_security_accounts_below(account_group)
        self._check_state_changed()

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._proxy.setFilterWildcard(pattern)
        self._view.treeView.expandAll()

    def _show_security_account_contents(self) -> None:
        selected_item = self._model.get_selected_item()
        if not isinstance(selected_item, SecurityAccount):
            raise TypeError(f"Selected item is not a SecurityAccount: {selected_item}")
        self._security_account_form_presenter.show(selected_item)

    def _edit_item(self) -> None:
        selected_item = self._model.get_selected_item()
        if selected_item is None:
            raise ValueError("No item selected for editing.")
        if isinstance(selected_item, AccountGroup):
            self._account_group_dialog_presenter.run_edit_dialog()
        if isinstance(selected_item, CashAccount):
            self._cash_account_dialog_presenter.run_edit_dialog()
        if isinstance(selected_item, SecurityAccount):
            self._security_account_dialog_presenter.run_edit_dialog()

    def _set_native_balance_column_visibility(self) -> None:
        show_native_balance_column = False
        non_native_cash_accounts = [
            account
            for account in self._record_keeper.cash_accounts
            if account.currency != self._record_keeper.base_currency
        ]
        for account in non_native_cash_accounts:
            show_native_balance_column = self._is_item_visible(account)
            if show_native_balance_column:
                break
        self._view.treeView.setColumnHidden(
            AccountTreeColumn.BALANCE_NATIVE, not show_native_balance_column
        )

    def _is_item_visible(self, item: Account | AccountGroup) -> bool:
        if item.parent is None:
            return True
        index = self._model.get_index_from_item(item.parent)
        index = self._proxy.mapFromSource(index)
        if self._view.treeView.isExpanded(index):
            return self._is_item_visible(item.parent)
        return False

    def _check_state_changed(self) -> None:
        self._update_checked_account_balance()
        self.event_check_state_changed()

    def _double_clicked(self) -> None:
        selection = self._model.get_selected_item()
        if isinstance(selection, SecurityAccount):
            self._security_account_form_presenter.show(selection)
