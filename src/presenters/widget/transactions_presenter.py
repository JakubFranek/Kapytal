import logging
import re
from collections.abc import Collection

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication
from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.security_objects import (
    SecurityTransaction,
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.transaction_filter import TransactionFilter
from src.presenters.dialog.cash_transaction_dialog_presenter import (
    CashTransactionDialogPresenter,
)
from src.presenters.dialog.cash_transfer_dialog_presenter import (
    CashTransferDialogPresenter,
)
from src.presenters.dialog.refund_transaction_dialog_presenter import (
    RefundTransactionDialogPresenter,
)
from src.presenters.dialog.security_transaction_dialog_presenter import (
    SecurityTransactionDialogPresenter,
)
from src.presenters.dialog.security_transfer_dialog_presenter import (
    SecurityTransferDialogPresenter,
)
from src.presenters.dialog.transaction_tags_dialog_presenter import (
    TransactionTagsDialogPresenter,
)
from src.presenters.form.transaction_filter.transaction_filter_form_presenter import (
    TransactionFilterFormPresenter,
)
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.proxy_models.transaction_table_proxy_model import (
    TransactionTableProxyModel,
)
from src.view_models.transaction_table_model import TransactionTableModel
from src.views.constants import TransactionTableColumn
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.utilities.handle_exception import display_error_message
from src.views.utilities.message_box_functions import ask_yes_no_question
from src.views.widgets.transaction_table_widget import TransactionTableWidget


class TransactionsPresenter:
    event_data_changed = Event()

    def __init__(
        self, view: TransactionTableWidget, record_keeper: RecordKeeper
    ) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._account_tree_shown_accounts = record_keeper.accounts

        self._initialize_model()
        self._initialize_presenters()
        self._initialize_view()
        self._connect_to_signals()
        self._connect_events()
        self._update_model_data()
        self._view.finalize_setup()

    @property
    def transaction_filter_form_presenter(self) -> TransactionFilterFormPresenter:
        return self._transaction_filter_form_presenter

    @property
    def checked_accounts(self) -> frozenset[Account]:
        return self._transaction_filter_form_presenter.checked_accounts

    @property
    def checked_account_items(self) -> frozenset[Account | AccountGroup]:
        return self._transaction_filter_form_presenter.checked_account_items

    def load_account_tree_checked_items(
        self, account_items: Collection[Account | AccountGroup]
    ) -> None:
        accounts = frozenset(
            account for account in account_items if isinstance(account, Account)
        )
        self._account_tree_shown_accounts = accounts
        self._model.valid_accounts = accounts
        self._transaction_filter_form_presenter.update_account_tree_checked_items(
            account_items
        )

    def get_visible_transactions(self) -> tuple[Transaction, ...]:
        return self._model.get_visible_items()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._cash_transaction_dialog_presenter.load_record_keeper(record_keeper)
        self._cash_transfer_dialog_presenter.load_record_keeper(record_keeper)
        self._security_transaction_dialog_presenter.load_record_keeper(record_keeper)
        self._security_transfer_dialog_presenter.load_record_keeper(record_keeper)
        self._refund_transaction_dialog_presenter.load_record_keeper(record_keeper)
        self._transaction_tags_dialog_presenter.load_record_keeper(record_keeper)
        self._transaction_filter_form_presenter.load_record_keeper(record_keeper)
        self._account_tree_shown_accounts = record_keeper.accounts
        self._reset_model()
        self._update_number_of_shown_transactions()
        self._update_table_columns()
        self._view.resize_table_to_contents()

    def update_base_currency(self) -> None:
        self._model.base_currency = self._record_keeper.base_currency

    def update_filter_models(self) -> None:
        self._transaction_filter_form_presenter.load_record_keeper(self._record_keeper)

    def refresh_view(self) -> None:
        self._view.tableView.viewport().update()

    def resize_table_to_contents(self) -> None:
        self._view.resize_table_to_contents()

    def reapply_sort(self) -> None:
        self._proxy_regex_sort_filter.setDynamicSortFilter(True)  # noqa: FBT003

    def _reset_model(self) -> None:
        """Resets the TransactionTableModel only."""
        self._model.pre_reset_model()
        self._update_model_data()
        self._model.post_reset_model()

    def _update_model_data(self) -> None:
        self._model.load_data(
            self._record_keeper.transactions,
            self._record_keeper.transaction_uuid_dict,
            self._record_keeper.base_currency,
        )

    def _update_table_columns(self) -> None:
        visible_transactions = self._model.get_visible_items()

        any_security_related = False
        any_cash_transfers = False
        any_with_categories = False
        for transaction in visible_transactions:
            if not any_security_related and isinstance(
                transaction, SecurityTransaction
            ):
                any_security_related = True
            if not any_cash_transfers and isinstance(transaction, CashTransfer):
                any_cash_transfers = True
            if not any_with_categories and isinstance(
                transaction, CashTransaction | RefundTransaction
            ):
                any_with_categories = True

        shown_accounts = tuple(self._account_tree_shown_accounts)
        single_cash_account = len(shown_accounts) == 1 and isinstance(
            shown_accounts[0], CashAccount
        )

        for column in TransactionTableColumn:
            if (
                column == TransactionTableColumn.SECURITY
                or column == TransactionTableColumn.SHARES
                or column == TransactionTableColumn.PRICE_PER_SHARE
            ):
                self._view.set_column_visibility(column, show=any_security_related)
            if (
                column == TransactionTableColumn.AMOUNT_RECEIVED
                or column == TransactionTableColumn.AMOUNT_SENT
            ):
                self._view.set_column_visibility(column, show=any_cash_transfers)
            if column == TransactionTableColumn.CATEGORY:
                self._view.set_column_visibility(column, show=any_with_categories)
            if column == TransactionTableColumn.BALANCE:
                self._view.set_column_visibility(column, show=single_cash_account)

    def _search_filter(self, pattern: str) -> None:
        if self._validate_regex(pattern) is False:
            return
        self._proxy_regex_sort_filter.setFilterRegularExpression(pattern)
        self._update_number_of_shown_transactions()
        self._update_table_columns()
        self.resize_table_to_contents()

    def _validate_regex(self, pattern: str) -> bool:
        try:
            re.compile(pattern)
        except re.error:
            return False
        else:
            return True

    def _initialize_model(self) -> None:
        self._proxy_transaction_filter = TransactionTableProxyModel(
            self._view, TransactionFilter()
        )
        self._proxy_regex_sort_filter = QSortFilterProxyModel(self._view)

        self._model = TransactionTableModel(
            self._view.tableView,
            self._proxy_regex_sort_filter,
            self._proxy_transaction_filter,
        )
        self._proxy_transaction_filter.setSourceModel(self._model)

        self._proxy_regex_sort_filter.setSourceModel(self._proxy_transaction_filter)
        self._proxy_regex_sort_filter.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        self._proxy_regex_sort_filter.setFilterKeyColumn(-1)
        self._proxy_regex_sort_filter.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy_regex_sort_filter.setSortCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        self._proxy_regex_sort_filter.sort(0, Qt.SortOrder.DescendingOrder)

        self._view.tableView.setModel(self._proxy_regex_sort_filter)

    def _initialize_presenters(self) -> None:
        self._cash_transaction_dialog_presenter = CashTransactionDialogPresenter(
            self._view, self._record_keeper, self._model
        )
        self._cash_transfer_dialog_presenter = CashTransferDialogPresenter(
            self._view, self._record_keeper, self._model
        )
        self._security_transaction_dialog_presenter = (
            SecurityTransactionDialogPresenter(
                self._view, self._record_keeper, self._model
            )
        )
        self._security_transfer_dialog_presenter = SecurityTransferDialogPresenter(
            self._view, self._record_keeper, self._model
        )
        self._refund_transaction_dialog_presenter = RefundTransactionDialogPresenter(
            self._view, self._record_keeper, self._model
        )
        self._transaction_tags_dialog_presenter = TransactionTagsDialogPresenter(
            self._view, self._record_keeper
        )
        self._transaction_filter_form_presenter = TransactionFilterFormPresenter(
            self._view, self._record_keeper, self._account_tree_shown_accounts
        )

    def _initialize_view(self) -> None:
        self._view.resize_table_to_contents()
        self._view.set_column_visibility(TransactionTableColumn.UUID, show=False)
        self._view.set_column_visibility(
            TransactionTableColumn.DATETIME_CREATED, show=False
        )

    def _connect_to_signals(self) -> None:
        self._view.signal_search_text_changed.connect(self._search_filter)

        self._view.signal_income.connect(
            lambda: self._cash_transaction_dialog_presenter.run_add_dialog(
                CashTransactionType.INCOME, self._account_tree_shown_accounts
            )
        )
        self._view.signal_expense.connect(
            lambda: self._cash_transaction_dialog_presenter.run_add_dialog(
                CashTransactionType.EXPENSE, self._account_tree_shown_accounts
            )
        )
        self._view.signal_cash_transfer.connect(
            lambda: self._cash_transfer_dialog_presenter.run_add_dialog(
                self._account_tree_shown_accounts, self._record_keeper.cash_accounts
            )
        )
        self._view.signal_buy.connect(
            lambda: self._security_transaction_dialog_presenter.run_add_dialog(
                SecurityTransactionType.BUY, self._account_tree_shown_accounts
            )
        )
        self._view.signal_sell.connect(
            lambda: self._security_transaction_dialog_presenter.run_add_dialog(
                SecurityTransactionType.SELL, self._account_tree_shown_accounts
            )
        )
        self._view.signal_security_transfer.connect(
            lambda: self._security_transfer_dialog_presenter.run_add_dialog(
                self._account_tree_shown_accounts
            )
        )

        self._view.signal_delete.connect(self._delete_transactions)
        self._view.signal_duplicate.connect(self._duplicate_transaction)
        self._view.signal_edit.connect(self._edit_transactions)

        self._view.signal_filter_transactions.connect(
            self._show_filter_transactions_form
        )

        self._view.signal_add_tags.connect(self._add_tags)
        self._view.signal_remove_tags.connect(self._remove_tags)

        self._view.signal_selection_changed.connect(self._selection_changed)
        self._view.signal_refund.connect(self._refund_transaction)
        self._view.signal_find_related.connect(self._find_related)
        self._view.signal_reset_columns.connect(self._reset_columns)

    def _connect_events(self) -> None:
        self._cash_transaction_dialog_presenter.event_update_model.append(
            self._update_model_data
        )
        self._cash_transaction_dialog_presenter.event_data_changed.append(
            self._data_changed
        )

        self._cash_transfer_dialog_presenter.event_update_model.append(
            self._update_model_data
        )
        self._cash_transfer_dialog_presenter.event_data_changed.append(
            self._data_changed
        )

        self._security_transaction_dialog_presenter.event_update_model.append(
            self._update_model_data
        )
        self._security_transaction_dialog_presenter.event_data_changed.append(
            self._data_changed
        )

        self._security_transfer_dialog_presenter.event_update_model.append(
            self._update_model_data
        )
        self._security_transfer_dialog_presenter.event_data_changed.append(
            self._data_changed
        )

        self._transaction_tags_dialog_presenter.event_data_changed.append(
            self._data_changed
        )

        self._refund_transaction_dialog_presenter.event_update_model.append(
            self._update_model_data
        )
        self._refund_transaction_dialog_presenter.event_data_changed.append(
            self._data_changed
        )

        self._transaction_filter_form_presenter.event_filter_changed.append(
            self._filter_changed
        )

    def _delete_transactions(self) -> None:
        transactions = self._model.get_selected_items()
        no_of_transactions = len(transactions)
        if no_of_transactions == 0:
            raise ValueError("Cannot delete unselected Transaction.")

        logging.debug(
            f"Asking user to confirm deletion of {no_of_transactions} Transaction(s)"
        )
        if not ask_yes_no_question(
            self._view,
            f"Are you sure you want to delete {no_of_transactions} Transaction(s)?",
            "Remove Transactions?",
        ):
            logging.debug("User cancelled Transaction(s) deletion")
            return

        any_deleted = False
        for transaction in transactions:
            try:
                self._record_keeper.remove_transactions((transaction.uuid,))
                logging.info(
                    f"Removed {transaction.__class__.__name__}: "
                    f"uuid={transaction.uuid!s}"
                )
                self._model.pre_remove_item(transaction)
                self._update_model_data()
                self._model.post_remove_item()
                any_deleted = True
            except Exception as exception:  # noqa: BLE001
                handle_exception(exception)
        if any_deleted:
            self._update_number_of_shown_transactions()
            self.event_data_changed()

    def _duplicate_transaction(self) -> None:
        transactions = self._model.get_selected_items()
        if len(transactions) != 1:
            raise InvalidOperationError("Only a single Transaction can be duplicated.")

        transaction = transactions[0]
        if isinstance(transaction, CashTransaction):
            self._cash_transaction_dialog_presenter.run_duplicate_dialog(transaction)
        if isinstance(transaction, CashTransfer):
            self._cash_transfer_dialog_presenter.run_duplicate_dialog(transaction)
        if isinstance(transaction, SecurityTransaction):
            self._security_transaction_dialog_presenter.run_duplicate_dialog(
                transaction
            )
        if isinstance(transaction, SecurityTransfer):
            self._security_transfer_dialog_presenter.run_duplicate_dialog(transaction)
        if isinstance(transaction, RefundTransaction):
            raise InvalidOperationError("Cannot duplicate RefundTransaction.")

    def _edit_transactions(self) -> None:
        transactions = self._model.get_selected_items()
        if len(transactions) == 0:
            raise InvalidOperationError("Cannot edit zero Transactions.")

        if all(
            isinstance(transaction, CashTransaction) for transaction in transactions
        ):
            self._cash_transaction_dialog_presenter.run_edit_dialog(transactions)
            return
        if all(isinstance(transaction, CashTransfer) for transaction in transactions):
            self._cash_transfer_dialog_presenter.run_edit_dialog(transactions)
            return
        if all(
            isinstance(transaction, RefundTransaction) for transaction in transactions
        ):
            self._refund_transaction_dialog_presenter.run_edit_dialog()
            return
        if all(
            isinstance(transaction, SecurityTransaction) for transaction in transactions
        ):
            self._security_transaction_dialog_presenter.run_edit_dialog(transactions)
            return
        if all(
            isinstance(transaction, SecurityTransfer) for transaction in transactions
        ):
            self._security_transfer_dialog_presenter.run_edit_dialog(transactions)
            return

        display_error_message(
            "All edited Transactions must be of the same type.", title="Warning"
        )

    def _refund_transaction(self) -> None:
        self._refund_transaction_dialog_presenter.run_add_dialog(
            self._account_tree_shown_accounts
        )

    def _add_tags(self) -> None:
        transactions = self._model.get_selected_items()
        if len(transactions) == 0:
            raise InvalidOperationError("Cannot add Tags to zero Transactions.")

        if any(
            isinstance(transaction, RefundTransaction) for transaction in transactions
        ):
            display_error_message("Cannot add Tags to a Refund.", title="Warning")
            return

        self._transaction_tags_dialog_presenter.run_add_dialog(transactions)

    def _remove_tags(self) -> None:
        transactions = self._model.get_selected_items()
        if len(transactions) == 0:
            raise InvalidOperationError("Cannot remove Tags from zero Transactions.")

        if any(
            isinstance(transaction, RefundTransaction) for transaction in transactions
        ):
            display_error_message("Cannot remove Tags from a Refund.", title="Warning")
            return

        self._transaction_tags_dialog_presenter.run_remove_dialog(transactions)

    def _selection_changed(self) -> None:
        transactions = self._model.get_selected_items()

        enable_refund = False
        enable_find_related = False
        enable_duplicate = True
        if len(transactions) == 1:
            transaction = transactions[0]
            if (
                isinstance(transaction, CashTransaction)
                and transaction.type_ == CashTransactionType.EXPENSE
            ):
                enable_refund = True
                enable_find_related = transaction.is_refunded
            if isinstance(transaction, RefundTransaction):
                enable_duplicate = False
                enable_find_related = True

        self._view.set_actions(
            enable_refund=enable_refund,
            enable_find_related=enable_find_related,
            enable_duplicate=enable_duplicate,
        )

    def _find_related(self) -> None:
        transactions = self._model.get_selected_items()
        if len(transactions) > 1:
            raise ValueError(
                "Cannot find related Transactions for more than one Transaction."
            )

        transaction = transactions[0]
        if not isinstance(transaction, CashTransaction) and not isinstance(
            transaction, RefundTransaction
        ):
            raise TypeError(
                "Cannot find related Transactions for a Transaction which is not a "
                "CashTransaction nor a RefundTransaction."
            )

        if isinstance(transaction, RefundTransaction):
            refunded_transaction = transaction.refunded_transaction
        else:
            refunded_transaction = transaction

        refunds = refunded_transaction.refunds
        uuids = [str(refund.uuid) for refund in refunds] + [
            str(refunded_transaction.uuid)
        ]
        pattern = "|".join(uuids)
        self._view.search_bar_text = pattern

    def _show_filter_transactions_form(self) -> None:
        self._transaction_filter_form_presenter.show_form()

    def _filter_changed(self) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self._view, "Filtering Transactions, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        QApplication.processEvents()  # needs to be called twice to show dialog reliably

        try:
            self._proxy_transaction_filter.transaction_filter = (
                self._transaction_filter_form_presenter.transaction_filter
            )
            self._view.set_filter_active(
                active=self._transaction_filter_form_presenter.filter_active
            )
            self._update_number_of_shown_transactions()
            self._update_table_columns()
            self.resize_table_to_contents()
            self._view.set_filter_tooltip(
                self._transaction_filter_form_presenter.active_filter_names
            )
        except:  # noqa: TRY302
            raise
        finally:
            self._busy_dialog.close()

    def _data_changed(self) -> None:
        self._update_number_of_shown_transactions()
        self.event_data_changed()

    def _update_number_of_shown_transactions(self) -> None:
        n_visible = self._proxy_regex_sort_filter.rowCount()
        n_total = len(self._record_keeper.transactions)
        logging.debug(f"Visible transactions: {n_visible:,}/{n_total:,}")
        self._view.set_shown_transactions(n_visible, n_total)
        self._view.set_shown_transactions(n_visible, n_total)

    def _reset_columns(self) -> None:
        self._view.set_column_visibility(TransactionTableColumn.UUID, show=False)
        self._view.set_column_visibility(
            TransactionTableColumn.DATETIME_CREATED, show=False
        )
        self._update_table_columns()
        self._view.reset_column_order()
