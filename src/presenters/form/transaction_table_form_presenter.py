from collections.abc import Collection
from typing import TYPE_CHECKING
from uuid import UUID

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QWidget
from src.models.base_classes.transaction import Transaction
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.cash_objects import (
    CashTransaction,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.security_objects import (
    SecurityTransaction,
    SecurityTransfer,
)
from src.models.record_keeper import RecordKeeper
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
from src.presenters.utilities.event import Event
from src.view_models.transaction_table_model import TransactionTableModel
from src.views.constants import TransactionTableColumn
from src.views.forms.transaction_table_form import TransactionTableForm
from src.views.utilities.handle_exception import display_error_message

if TYPE_CHECKING:
    from presenters.dialog.transaction_dialog_presenter import (
        TransactionDialogPresenter,
    )

COLUMNS_SECURITY_RELATED = {
    TransactionTableColumn.SECURITY,
    TransactionTableColumn.SHARES,
    TransactionTableColumn.PRICE_PER_SHARE,
}
COLUMNS_CASH_TRANSFERS = {
    TransactionTableColumn.AMOUNT_RECEIVED,
    TransactionTableColumn.AMOUNT_SENT,
}
COLUMNS_HIDDEN_BY_DEFAULT = {
    TransactionTableColumn.UUID,
    TransactionTableColumn.DATETIME_CREATED,
    TransactionTableColumn.BALANCE,
}


class TransactionTableFormPresenter:
    def __init__(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

        self.event_data_changed = Event()
        self.event_form_closed = Event()

        self._form = TransactionTableForm(None)
        self._proxy = QSortFilterProxyModel(self._form)
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._model = TransactionTableModel(self._form.table_view, self._proxy, None)
        self._proxy.setSourceModel(self._model)
        self._form.table_view.setModel(self._proxy)
        self._form.signal_edit.connect(self._edit_transactions)
        self._form.signal_add_tags.connect(self._add_tags)
        self._form.signal_remove_tags.connect(self._remove_tags)
        self._form.signal_widget_closed.connect(self.event_form_closed)

        self._initialize_presenters()
        self._connect_events()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._cash_transaction_dialog_presenter.load_record_keeper(record_keeper)
        self._cash_transfer_dialog_presenter.load_record_keeper(record_keeper)
        self._security_transaction_dialog_presenter.load_record_keeper(record_keeper)
        self._security_transfer_dialog_presenter.load_record_keeper(record_keeper)
        self._refund_transaction_dialog_presenter.load_record_keeper(record_keeper)
        self._transaction_tags_dialog_presenter.load_record_keeper(record_keeper)

    def load_data(self, transactions: Collection[Transaction], title: str) -> None:
        transaction_uuid_dict = {
            transaction.uuid: transaction for transaction in transactions
        }

        self._model.pre_reset_model()
        self._model.load_data(
            transactions, transaction_uuid_dict, self._record_keeper.base_currency
        )

        header = self._form.table_view.horizontalHeader()
        if header.isSortIndicatorShown():
            sort_column = header.sortIndicatorSection()
            sort_order = header.sortIndicatorOrder()
            self._model.post_reset_model(sort_column, sort_order)
        else:
            self._model.post_reset_model()

        self._update_table_columns()
        self._form.table_view.resizeColumnsToContents()
        self._form.set_window_title(title)

    def show_form(self, parent: QWidget) -> None:
        self._form.setParent(parent, Qt.WindowType.Window)
        self._form.show_form()

    def _update_table_columns(self) -> None:
        visible_transactions = self._model.get_visible_items()

        any_security_related = False
        any_cash_transfers = False
        any_with_categories = False
        any_non_base_amount = False
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
            if (
                not any_non_base_amount
                and isinstance(transaction, CashTransaction | RefundTransaction)
                and transaction.currency != self._record_keeper.base_currency
            ):
                any_non_base_amount = True
            if (
                any_security_related
                and any_cash_transfers
                and any_with_categories
                and any_non_base_amount
            ):
                break

        for column in TransactionTableColumn:
            if column in COLUMNS_SECURITY_RELATED:
                self._form.table_view.setColumnHidden(column, not any_security_related)
            if column in COLUMNS_CASH_TRANSFERS:
                self._form.table_view.setColumnHidden(column, not any_cash_transfers)
            if column == TransactionTableColumn.CATEGORY:
                self._form.table_view.setColumnHidden(column, not any_with_categories)
            if column == TransactionTableColumn.AMOUNT_NATIVE:
                self._form.table_view.setColumnHidden(column, not any_non_base_amount)
            if column in COLUMNS_HIDDEN_BY_DEFAULT:
                self._form.table_view.setColumnHidden(column, True)  # noqa: FBT003

    def _initialize_presenters(self) -> None:
        self._cash_transaction_dialog_presenter = CashTransactionDialogPresenter(
            self._form, self._record_keeper
        )
        self._cash_transfer_dialog_presenter = CashTransferDialogPresenter(
            self._form, self._record_keeper
        )
        self._security_transaction_dialog_presenter = (
            SecurityTransactionDialogPresenter(self._form, self._record_keeper)
        )
        self._security_transfer_dialog_presenter = SecurityTransferDialogPresenter(
            self._form, self._record_keeper
        )
        self._refund_transaction_dialog_presenter = RefundTransactionDialogPresenter(
            self._form, self._record_keeper
        )

        self._transaction_tags_dialog_presenter = TransactionTagsDialogPresenter(
            self._form, self._record_keeper
        )

        self._transaction_dialog_presenters: tuple[TransactionDialogPresenter] = (
            self._cash_transaction_dialog_presenter,
            self._cash_transfer_dialog_presenter,
            self._security_transaction_dialog_presenter,
            self._security_transfer_dialog_presenter,
            self._refund_transaction_dialog_presenter,
        )

    def _connect_events(self) -> None:
        for presenter in self._transaction_dialog_presenters:
            presenter.event_update_model.append(self._update_model_data)
            presenter.event_data_changed.append(self._data_changed)
            presenter.event_pre_add.append(self._model.pre_add)
            presenter.event_post_add.append(self._model.post_add)

        self._transaction_tags_dialog_presenter.event_data_changed.append(
            self._data_changed
        )

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

    def _data_changed(self, uuids: Collection[UUID] | None = None) -> None:
        if uuids is not None:
            self._model.emit_data_changed_for_uuids(uuids)

        self._update_table_columns()
        self.event_data_changed(uuids)

    def _update_model_data(self) -> None:
        self._update_table_columns()
        self._form.table_view.resizeColumnsToContents()
