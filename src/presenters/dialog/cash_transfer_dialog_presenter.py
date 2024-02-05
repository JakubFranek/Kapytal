import logging
from collections.abc import Collection, Sequence
from datetime import datetime

from src.models.base_classes.account import Account
from src.models.model_objects.attributes import AttributeType
from src.models.model_objects.cash_objects import CashAccount, CashTransfer
from src.models.user_settings import user_settings
from src.presenters.dialog.transaction_dialog_presenter import (
    TransactionDialogPresenter,
)
from src.presenters.utilities.check_for_nonexistent_attributes import (
    check_for_nonexistent_attributes,
)
from src.presenters.utilities.handle_exception import handle_exception
from src.presenters.utilities.validate_inputs import validate_datetime
from src.views.dialogs.cash_transfer_dialog import CashTransferDialog, EditMode
from src.views.utilities.handle_exception import display_error_message


class CashTransferDialogPresenter(TransactionDialogPresenter):
    def run_add_dialog(self, selected_accounts: Collection[Account]) -> None:
        logging.debug("Running CashTransferDialog (edit_mode=ADD)")
        if len(self._record_keeper.cash_accounts) <= 1:
            display_error_message(
                "Create at least two Cash Accounts before creating a Cash Transfer.",
                title="Warning",
            )
            return

        self._prepare_dialog(edit_mode=EditMode.ADD)

        _selected_cash_accounts = tuple(
            account for account in selected_accounts if isinstance(account, CashAccount)
        )
        if len(_selected_cash_accounts) == 1:
            self._dialog.sender_path = _selected_cash_accounts[0].path
        elif len(_selected_cash_accounts) == 2:
            self._dialog.sender_path = _selected_cash_accounts[0].path
            self._dialog.recipient_path = _selected_cash_accounts[1].path

        self._dialog.datetime_ = datetime.now(user_settings.settings.time_zone).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        self._dialog.signal_do_and_close.connect(
            lambda: self._add_cash_transfer(close=True)
        )
        self._dialog.signal_do_and_continue.connect(
            lambda: self._add_cash_transfer(close=False)
        )

        self._dialog.exec()

    def run_duplicate_dialog(self, transfer: CashTransfer) -> None:
        logging.debug("Running duplicate CashTransferDialog (edit_mode=ADD)")
        self._prepare_dialog(edit_mode=EditMode.ADD)

        self._dialog.sender_path = transfer.sender.path
        self._dialog.recipient_path = transfer.recipient.path
        self._dialog.amount_sent = transfer.amount_sent.value_rounded
        self._dialog.amount_received = transfer.amount_received.value_rounded
        self._dialog.datetime_ = transfer.datetime_
        self._dialog.description = transfer.description
        self._dialog.tag_names = [tag.name for tag in transfer.tags]

        self._dialog.signal_do_and_close.connect(
            lambda: self._add_cash_transfer(close=True)
        )
        self._dialog.signal_do_and_continue.connect(
            lambda: self._add_cash_transfer(close=False)
        )
        self._dialog.exec()

    def run_edit_dialog(self, transfers: Sequence[CashTransfer]) -> None:
        sender_paths = {transfer.sender.path for transfer in transfers}
        recipient_paths = {transfer.recipient.path for transfer in transfers}

        sender_currencies = {transfer.sender.currency for transfer in transfers}
        recipient_currencies = {transfer.recipient.currency for transfer in transfers}

        if len(transfers) == 1:
            edit_mode = EditMode.EDIT_SINGLE
        elif len(sender_paths) > 1 and len(recipient_paths) > 1:
            edit_mode = EditMode.EDIT_MULTIPLE_MIXED_CURRENCY
        elif len(sender_currencies) > 1:
            edit_mode = EditMode.EDIT_MULTIPLE_SENDER_MIXED_CURRENCY
        elif len(recipient_currencies) > 1:
            edit_mode = EditMode.EDIT_MULTIPLE_RECIPIENT_MIXED_CURRENCY
        else:
            edit_mode = EditMode.EDIT_MULTIPLE

        logging.debug(f"Running CashTransactionDialog (edit_mode={edit_mode.name})")

        self._prepare_dialog(edit_mode=edit_mode)

        self._dialog.sender_path = sender_paths.pop() if len(sender_paths) == 1 else ""
        self._dialog.recipient_path = (
            recipient_paths.pop() if len(recipient_paths) == 1 else ""
        )

        datetimes = {transfer.datetime_ for transfer in transfers}
        self._dialog.datetime_ = (
            datetimes.pop() if len(datetimes) == 1 else self._dialog.min_datetime
        )

        descriptions = {transfer.description for transfer in transfers}
        self._dialog.description = descriptions.pop() if len(descriptions) == 1 else ""

        amounts_sent = {transfer.amount_sent.value_rounded for transfer in transfers}
        amounts_received = {
            transfer.amount_received.value_rounded for transfer in transfers
        }
        self._dialog.amount_sent = amounts_sent.pop() if len(amounts_sent) == 1 else 0
        self._dialog.amount_received = (
            amounts_received.pop() if len(amounts_received) == 1 else 0
        )

        tag_names_frozensets = set()
        for transfer in transfers:
            tag_names_frozenset = frozenset(tag.name for tag in transfer.tags)
            tag_names_frozensets.add(tag_names_frozenset)

        self._dialog.tag_names = (
            sorted(tag_names_frozensets.pop()) if len(tag_names_frozensets) == 1 else ()
        )

        self._dialog.signal_do_and_close.connect(
            lambda: self._edit_cash_transfers(transfers)
        )
        self._dialog.exec()

    def _add_cash_transfer(self, *, close: bool) -> None:
        sender_path = self._dialog.sender_path
        recipient_path = self._dialog.recipient_path
        datetime_ = self._dialog.datetime_
        if datetime_ is None:
            raise ValueError("Expected datetime_, received None.")
        if not validate_datetime(datetime_, self._dialog):
            return
        description = (
            self._dialog.description if self._dialog.description is not None else ""
        )
        amount_sent = self._dialog.amount_sent
        if amount_sent is None:
            raise ValueError("Expected Decimal, received None.")
        amount_received = self._dialog.amount_received
        if amount_received is None:
            raise ValueError("Expected Decimal, received None.")
        if amount_sent <= 0 or amount_received <= 0:
            display_error_message(
                "Sent and received amounts must be positive.", title="Warning"
            )
            return
        tag_names = self._dialog.tag_names

        if not check_for_nonexistent_attributes(
            tag_names, self._record_keeper.tags, AttributeType.TAG, self._dialog
        ):
            logging.debug("Dialog aborted")
            return

        logging.info(
            f"Adding CashTransfer: {datetime_.strftime('%Y-%m-%d')}, "
            f"{description=}, sender={sender_path}, sent={amount_sent}, "
            f"recipient={recipient_path}, received={amount_received}, {tag_names=}"
        )
        try:
            self._record_keeper.add_cash_transfer(
                description,
                datetime_,
                sender_path,
                recipient_path,
                amount_sent,
                amount_received,
                tag_names,
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self.event_pre_add()
        self.event_update_model()
        self.event_post_add()
        if close:
            self._dialog.close()
        self.event_data_changed()

    def _edit_cash_transfers(self, transactions: Sequence[CashTransfer]) -> None:
        uuids = [transaction.uuid for transaction in transactions]

        sender_path = self._dialog.sender_path
        recipient_path = self._dialog.recipient_path
        amount_sent = self._dialog.amount_sent
        amount_received = self._dialog.amount_received
        datetime_ = self._dialog.datetime_
        if datetime_ is not None and not validate_datetime(datetime_, self._dialog):
            return
        description = self._dialog.description
        tag_names = self._dialog.tag_names

        if tag_names is not None and not check_for_nonexistent_attributes(
            tag_names, self._record_keeper.tags, AttributeType.TAG, self._dialog
        ):
            logging.debug("Dialog aborted")
            return

        log = []
        if description is not None:
            log.append(f"{description=}")
        if datetime_ is not None:
            log.append(f"date={datetime_.strftime('%Y-%m-%d')}")
        if sender_path is not None:
            log.append(f"sender='{sender_path}'")
        if recipient_path is not None:
            log.append(f"recipient='{recipient_path}'")
        if amount_sent is not None:
            log.append(f"sent={amount_sent}")
        if amount_received is not None:
            log.append(f"received={amount_received}")
        if tag_names is not None:
            log.append(f"tags={tag_names}")
        logging.info(
            f"Editing {len(transactions)} CashTransaction(s): {', '.join(log)}, "
            f"uuids={[str(uuid) for uuid in uuids]}"
        )
        try:
            self._record_keeper.edit_cash_transfers(
                uuids,
                description,
                datetime_,
                sender_path,
                recipient_path,
                amount_sent,
                amount_received,
                tag_names,
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._dialog.close()
        self.event_update_model()
        self.event_data_changed(uuids)

    def _prepare_dialog(self, edit_mode: EditMode) -> bool:
        tag_names = sorted(tag.name for tag in self._record_keeper.tags)
        self._dialog = CashTransferDialog(
            self._parent_view,
            self._record_keeper.cash_accounts,
            tag_names,
            self._record_keeper.descriptions,
            edit_mode=edit_mode,
        )
