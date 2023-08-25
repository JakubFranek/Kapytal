import logging
from collections.abc import Collection
from datetime import datetime, timedelta

from PyQt6.QtWidgets import QWidget
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    RefundTransaction,
)
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.check_for_nonexistent_attributes import (
    check_for_nonexistent_attributes,
)
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.presenters.utilities.validate_inputs import validate_datetime
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
    ) -> None:
        logging.debug("Running RefundTransactionDialog (adding)")
        transactions = self._model.get_selected_items()
        if len(transactions) > 1:
            raise ValueError("Cannot refund multiple transactions.")

        refunded_transaction: CashTransaction = transactions[0]
        self._prepare_dialog(refunded_transaction, edited_refund=None)

        self._dialog.account_path = refunded_transaction.account.path
        self._dialog.payee = refunded_transaction.payee.name
        self._dialog.datetime_ = datetime.now(user_settings.settings.time_zone).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        self._dialog.signal_do_and_close.connect(self._add_refund)
        self._dialog.exec()

    def run_edit_dialog(self) -> None:
        logging.debug("Running RefundTransactionDialog (editing)")
        transactions = self._model.get_selected_items()
        if len(transactions) > 1:
            display_error_message("Cannot edit multiple Refunds.", title="Warning")
            return

        refund: RefundTransaction = transactions[0]
        self._prepare_dialog(refund.refunded_transaction, edited_refund=refund)
        self._dialog.signal_do_and_close.connect(self._edit_refund)
        self._dialog.exec()

    def _add_refund(
        self,
    ) -> None:
        account = self._dialog.account_path
        payee = self._dialog.payee
        if not payee:
            display_error_message(
                "Payee name must be at least 1 character long.", title="Warning"
            )
            return
        if not check_for_nonexistent_attributes(
            [payee], self._record_keeper.payees, self._dialog
        ):
            logging.debug("Dialog aborted")
            return

        refunded_transaction_uuid = self._dialog.refunded_transaction.uuid
        refunded_transaction = self._dialog.refunded_transaction

        datetime_ = self._dialog.datetime_
        if datetime_ is None:
            raise ValueError("Expected datetime_, received None.")
        if not validate_datetime(datetime_, self._dialog):
            return
        if (
            datetime_.date() == refunded_transaction.datetime_.date()
            and datetime_ <= refunded_transaction.datetime_
        ):
            datetime_ = refunded_transaction.datetime_ + timedelta(seconds=1)
        description = self._dialog.description
        total_amount = self._dialog.amount
        if total_amount <= 0:
            display_error_message(
                "Transaction amount must be positive.", title="Warning"
            )
            return
        category_amount_pairs = self._dialog.category_amount_pairs
        tag_amount_pairs = self._dialog.tag_amount_pairs

        categories = [category for category, _ in category_amount_pairs]
        tags = [tag for tag, _ in tag_amount_pairs]

        logging.info(
            f"Adding RefundTransaction: {datetime_.strftime('%Y-%m-%d')}, "
            f"{description=}, {account=}, {payee=}, "
            f"amount={total_amount!s} {self._dialog.currency_code}, "
            f"{categories=}, {tags=}"
        )
        try:
            self._record_keeper.add_refund(
                description=description,
                datetime_=datetime_,
                refunded_transaction_uuid=refunded_transaction_uuid,
                refunded_account_path=account,
                payee_name=payee,
                category_path_amount_pairs=category_amount_pairs,
                tag_name_amount_pairs=tag_amount_pairs,
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._model.pre_add()
        self.event_update_model()
        self._model.post_add()
        self.event_data_changed()
        self._dialog.close()

    def _edit_refund(
        self,
    ) -> None:
        account = self._dialog.account_path
        payee = self._dialog.payee
        if not payee:
            display_error_message(
                "Payee name must be at least 1 character long.", title="Warning"
            )
            return
        if not check_for_nonexistent_attributes(
            [payee], self._record_keeper.payees, self._dialog
        ):
            logging.debug("Dialog aborted")
            return

        refunded_transaction = self._dialog.refunded_transaction

        datetime_ = self._dialog.datetime_
        if datetime_ is not None and not validate_datetime(datetime_, self._dialog):
            return
        if (
            datetime_.date() == refunded_transaction.datetime_.date()
            and datetime_ <= refunded_transaction.datetime_
        ):
            datetime_ = refunded_transaction.datetime_ + timedelta(seconds=1)

        description = self._dialog.description
        total_amount = self._dialog.amount
        if total_amount <= 0:
            display_error_message(
                "Transaction amount must be positive.", title="Warning"
            )
            return
        category_amount_pairs = self._dialog.category_amount_pairs
        tag_amount_pairs = self._dialog.tag_amount_pairs

        refund = self._dialog.edited_refund
        if refund is None:
            raise ValueError("Expected RefundTransaction, received None.")
        refund_uuid = refund.uuid

        log = []
        if description != refund.description:
            log.append(f"{description=}")
        if datetime_ != refund.datetime_:
            log.append(f"date={datetime_.strftime('%Y-%m-%d')}")
        if account != refund.account.path:
            log.append(f"{account=}")
        if payee != refund.payee.name:
            log.append(f"{payee=}")
        original_category_amount_pairs = tuple(
            (category.path, amount.value_rounded)
            for category, amount in refund.category_amount_pairs
        )
        if category_amount_pairs != original_category_amount_pairs:
            log.append(f"{category_amount_pairs=}")

        original_tag_amount_pairs = tuple(
            (tag.name, amount.value_rounded) for tag, amount in refund.tag_amount_pairs
        )
        if tag_amount_pairs != original_tag_amount_pairs:
            log.append(f"{tag_amount_pairs=}")
        logging.info(f"Editing RefundTransaction: {', '.join(log)}, uuid={refund_uuid}")
        try:
            self._record_keeper.edit_refunds(
                transaction_uuids=[refund_uuid],
                description=description,
                datetime_=datetime_,
                account_path=account,
                payee_name=payee,
                category_path_amount_pairs=category_amount_pairs,
                tag_name_amount_pairs=tag_amount_pairs,
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self.event_update_model()
        self._model.emit_data_changed_for_uuids([refund_uuid])
        self.event_data_changed()
        self._dialog.close()

    def _prepare_dialog(
        self,
        refunded_transaction: CashTransaction,
        edited_refund: RefundTransaction | None,
    ) -> bool:
        accounts = [
            account
            for account in self._record_keeper.cash_accounts
            if account.currency == refunded_transaction.currency
        ]

        payees = sorted(payee.name for payee in self._record_keeper.payees)
        self._dialog = RefundTransactionDialog(
            self._parent_view,
            refunded_transaction,
            accounts,
            payees,
            self._record_keeper.descriptions,
            edited_refund,
        )
