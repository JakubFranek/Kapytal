import logging
from collections.abc import Collection

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.base_classes.account import Account
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.security_objects import SecurityRelatedTransaction
from src.models.record_keeper import RecordKeeper
from src.presenters.cash_transaction_dialog_presenter import (
    CashTransactionDialogPresenter,
)
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.transaction_table_model import TransactionTableModel
from src.views.constants import TransactionTableColumn
from src.views.utilities.handle_exception import display_error_message
from src.views.widgets.transaction_table_widget import TransactionTableWidget


class TransactionsPresenter:
    event_data_changed = Event()
    event_refresh_account_tree = Event()

    def __init__(
        self, view: TransactionTableWidget, record_keeper: RecordKeeper
    ) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._valid_accounts = record_keeper.accounts

        self._setup_model()

        self._cash_transaction_dialog_presenter = CashTransactionDialogPresenter(
            view, record_keeper, self._model
        )

        self._setup_view()
        self._connect_signals()
        self._view.finalize_setup()

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
        self._update_table_columns()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._cash_transaction_dialog_presenter.load_record_keeper(record_keeper)
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

    def _update_table_columns(self) -> None:
        any_security_related = any(
            isinstance(transaction, SecurityRelatedTransaction)
            for transaction in self._model.transactions
        )
        any_cash_transfers = any(
            isinstance(transaction, CashTransfer)
            for transaction in self._model.transactions
        )
        any_with_categories = any(
            isinstance(transaction, CashTransaction | RefundTransaction)
            for transaction in self._model.transactions
        )
        single_cash_account = len(self._valid_accounts) == 1 and isinstance(
            self._valid_accounts[0], CashAccount
        )

        for column in TransactionTableColumn:
            if (
                column == TransactionTableColumn.COLUMN_SECURITY
                or column == TransactionTableColumn.COLUMN_SHARES
            ):
                self._view.set_column_visibility(column, show=any_security_related)
            if (
                column == TransactionTableColumn.COLUMN_AMOUNT_RECEIVED
                or column == TransactionTableColumn.COLUMN_AMOUNT_SENT
            ):
                self._view.set_column_visibility(column, show=any_cash_transfers)
            if column == TransactionTableColumn.COLUMN_CATEGORY:
                self._view.set_column_visibility(column, show=any_with_categories)
            if column == TransactionTableColumn.COLUMN_BALANCE:
                self._view.set_column_visibility(column, show=single_cash_account)

    def _filter(self) -> None:
        pattern = self._view.search_bar_text
        logging.debug(f"Filtering Transactions: {pattern=}")
        self._proxy_model.setFilterWildcard(pattern)

    def _setup_model(self) -> None:
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

    def _setup_view(self) -> None:
        self._view.resize_table_to_contents()
        self._view.set_column_visibility(TransactionTableColumn.COLUMN_UUID, show=False)

    def _connect_signals(self) -> None:
        self._view.signal_search_text_changed.connect(self._filter)

        self._view.signal_income.connect(
            lambda: self._cash_transaction_dialog_presenter.run_add_dialog(
                CashTransactionType.INCOME, self.valid_accounts
            )
        )
        self._view.signal_expense.connect(
            lambda: self._cash_transaction_dialog_presenter.run_add_dialog(
                CashTransactionType.EXPENSE, self.valid_accounts
            )
        )
        self._view.signal_delete.connect(self._delete_transactions)
        self._view.signal_duplicate.connect(self._duplicate_transaction)
        self._view.signal_edit.connect(self._edit_transactions)

        # TODO: add and remove tags: separate presenter/dialog or just dialog?
        self._view.signal_add_tags.connect()

        self._cash_transaction_dialog_presenter.event_update_model.append(
            self.update_model_data
        )
        self._cash_transaction_dialog_presenter.event_data_changed.append(
            self.event_data_changed
        )

    def _delete_transactions(self) -> None:
        transactions = self._model.get_selected_items()
        if len(transactions) == 0:
            raise ValueError("Cannot delete unselected Transaction.")

        any_deleted = False

        for transaction in transactions:
            try:
                self._record_keeper.remove_transactions(str(transaction.uuid))
                logging.info(
                    f"Removed {transaction.__class__.__name__}: "
                    f"uuid={str(transaction.uuid)}"
                )
                self._model.pre_remove_item(transaction)
                self.update_model_data()
                self._model.post_remove_item()
                any_deleted = True
            except Exception as exception:  # noqa: BLE001
                handle_exception(exception)
            finally:
                if any_deleted:
                    self.event_data_changed()
                    self.event_refresh_account_tree()

    def _duplicate_transaction(self) -> None:
        transactions = self._model.get_selected_items()
        if len(transactions) != 1:
            raise ValueError("Only a single Transaction can be duplicated.")

        transaction = transactions[0]
        if isinstance(transaction, CashTransaction):
            self._cash_transaction_dialog_presenter.run_duplicate_dialog(transaction)

    def _edit_transactions(self) -> None:
        transactions = self._model.get_selected_items()
        if len(transactions) == 0:
            raise ValueError("Cannot edit zero Transactions.")

        if all(
            isinstance(transaction, CashTransaction) for transaction in transactions
        ):
            self._cash_transaction_dialog_presenter.run_edit_dialog(transactions)
            return

        display_error_message(
            "All edited Transactions must be of the same type.", title="Warning"
        )
