import logging
from collections.abc import Collection
from datetime import datetime
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QWidget
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    RefundTransaction,
)
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.transaction_table_model import TransactionTableModel
from src.views.dialogs.refund_transaction_dialog import RefundTransactionDialog
from src.views.utilities.handle_exception import display_error_message


class RefundTransactionDialogPresenter:
    event_update_model = Event()
    event_data_changed = Event()

    def __init__(
        self,
        parent_view: QWidget,
        record_keeper: RecordKeeper,
        model: TransactionTableModel,
    ) -> None:
        self._parent_view = parent_view
        self._record_keeper = record_keeper
        self._model = model

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

    def run_add_dialog(
        self,
        valid_accounts: Collection[CashAccount],
    ) -> None:
        logging.debug("Running RefundTransactionDialog (mode=ADD)")
        transactions = self._model.get_selected_items()
        if len(transactions) > 1:
            raise ValueError("Cannot refund multiple transactions.")

        refunded_transaction = transactions.pop()

        self._prepare_dialog(refunded_transaction, edited_refund=None)

        self._dialog.account = tuple(valid_accounts)[0].path
        self._dialog.datetime_ = datetime.now(user_settings.settings.time_zone)

        self._dialog.signal_do_and_close.connect(lambda: self._add_refund(close=True))

        self._dialog.exec()

    def _add_refund(self, *, close: bool) -> None:
        type_ = self._dialog.type_
        account = self._dialog.account
        payee = self._dialog.payee
        if not payee:
            display_error_message(
                "Payee name must be at least 1 character long.", title="Warning"
            )
            return
        datetime_ = self._dialog.datetime_
        if datetime_ is None:
            raise ValueError("Expected datetime_, received None.")
        description = self._dialog.description
        total_amount = self._dialog.amount
        if total_amount is None:
            raise ValueError("Expected Decimal, received None.")
        if total_amount <= 0:
            display_error_message(
                "Transaction amount must be positive.", title="Warning"
            )
            return
        category_amount_pairs = self._dialog.category_amount_pairs
        tag_amount_pairs = self._dialog.tag_amount_pairs
        if any(amount <= 0 for _, amount in tag_amount_pairs):
            display_error_message("Tag amounts must be positive.", title="Warning")
            return

        if category_amount_pairs is None:
            raise ValueError("Expected ((str, Decimal),...), received None.")
        categories = [category for category, _ in category_amount_pairs]
        if any(not category for category in categories):
            display_error_message("Empty Category paths are invalid.", title="Warning")
            return
        tags = [tag for tag, _ in tag_amount_pairs]
        if any(not tag for tag in tags):
            display_error_message("Empty Tag names are invalid.", title="Warning")
            return

        logging.info(
            f"Adding CashTransaction: {datetime_.strftime('%Y-%m-%d')}, "
            f"{description=}, type={type_.name}, {account=}, {payee=}, "
            f"amount={str(total_amount)} {self._dialog.currency_code}, "
            f"{categories=}, {tags=}"
        )
        try:
            self._record_keeper.add_cash_transaction(
                description,
                datetime_,
                type_,
                account,
                payee,
                category_amount_pairs,
                tag_amount_pairs,
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._model.pre_add()
        self.event_update_model()
        self._model.post_add()
        if close:
            self._dialog.close()
        self.event_data_changed()

    def _prepare_dialog(
        self,
        refunded_transaction: CashTransaction,
        edited_refund: RefundTransaction | None,
    ) -> bool:
        accounts = [
            account
            for account in self._record_keeper.accounts
            if isinstance(account, CashAccount)
            and account.currency == refunded_transaction.currency
        ]

        payees = sorted(payee.name for payee in self._record_keeper.payees)
        self._dialog = RefundTransactionDialog(
            self._parent_view, refunded_transaction, accounts, payees, edited_refund
        )
