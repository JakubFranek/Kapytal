import logging
from collections.abc import Sequence
from datetime import datetime

from PyQt6.QtWidgets import QWidget
from src.models.model_objects.security_objects import SecurityTransfer
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.check_for_nonexistent_attributes import (
    check_for_nonexistent_attributes,
)
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.presenters.utilities.validate_inputs import validate_datetime
from src.view_models.transaction_table_model import TransactionTableModel
from src.views.dialogs.security_transfer_dialog import EditMode, SecurityTransferDialog
from src.views.utilities.handle_exception import display_error_message


class SecurityTransferDialogPresenter:
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

    def run_add_dialog(self) -> None:
        logging.debug("Running SecurityTransferDialog (edit_mode=ADD)")
        if len(self._record_keeper.security_accounts) < 2:  # noqa: PLR2004
            display_error_message(
                "Create at least two Security Accounts before creating a "
                "Security transfer.",
                title="Warning",
            )
            return

        self._prepare_dialog(edit_mode=EditMode.ADD)
        self._dialog.datetime_ = datetime.now(user_settings.settings.time_zone)

        self._dialog.signal_do_and_close.connect(
            lambda: self._add_security_transfer(close=True)
        )
        self._dialog.signal_do_and_continue.connect(
            lambda: self._add_security_transfer(close=False)
        )

        self._dialog.exec()

    def run_duplicate_dialog(self, transaction: SecurityTransfer) -> None:
        logging.debug("Running duplicate SecurityTransactionDialog (edit_mode=ADD)")
        self._prepare_dialog(edit_mode=EditMode.ADD)

        self._dialog.security_name = transaction.security.name
        self._dialog.sender_path = transaction.sender.path
        self._dialog.recipient_path = transaction.recipient.path
        self._dialog.shares = transaction.shares
        self._dialog.datetime_ = transaction.datetime_
        self._dialog.description = transaction.description
        self._dialog.tag_names = [tag.name for tag in transaction.tags]

        self._dialog.signal_do_and_close.connect(
            lambda: self._add_security_transfer(close=True)
        )
        self._dialog.signal_do_and_continue.connect(
            lambda: self._add_security_transfer(close=False)
        )
        self._dialog.exec()

    def run_edit_dialog(self, transfers: Sequence[SecurityTransfer]) -> None:
        if len(transfers) == 1:
            edit_mode = EditMode.EDIT_SINGLE
        elif len(transfers) > 1:
            edit_mode = EditMode.EDIT_MULTIPLE
        else:
            raise ValueError(
                "Expected 'transfers' to be a non-empty Sequence of SecurityTransfers."
            )

        logging.debug(f"Running SecurityTransferDialog (edit_mode={edit_mode.name})")

        self._prepare_dialog(edit_mode=edit_mode)

        datetimes = {
            transaction.datetime_.replace(hour=0, minute=0, second=0, microsecond=0)
            for transaction in transfers
        }
        self._dialog.datetime_ = (
            datetimes.pop() if len(datetimes) == 1 else self._dialog.min_datetime
        )

        descriptions = {transaction.description for transaction in transfers}
        self._dialog.description = descriptions.pop() if len(descriptions) == 1 else ""

        security_names = {transaction.security.name for transaction in transfers}
        self._dialog.security_name = (
            security_names.pop() if len(security_names) == 1 else ""
        )

        sender_paths = {transfer.sender.path for transfer in transfers}
        self._dialog.sender_path = sender_paths.pop() if len(sender_paths) == 1 else ""

        recipient_paths = {transfer.recipient.path for transfer in transfers}
        self._dialog.recipient_path = (
            recipient_paths.pop() if len(recipient_paths) == 1 else ""
        )

        shares = {transaction.shares for transaction in transfers}
        self._dialog.shares = shares.pop() if len(shares) == 1 else 0

        tag_names_frozensets = set()
        for transaction in transfers:
            tag_names_frozenset = frozenset(tag.name for tag in transaction.tags)
            tag_names_frozensets.add(tag_names_frozenset)

        self._dialog.tag_names = (
            sorted(tag_names_frozensets.pop()) if len(tag_names_frozensets) == 1 else ()
        )

        self._dialog.signal_do_and_close.connect(self._edit_security_transfers)
        self._dialog.exec()

    def _add_security_transfer(self, *, close: bool) -> None:
        datetime_ = self._dialog.datetime_
        if datetime_ is None:
            raise ValueError("Expected datetime_, received None.")
        if not validate_datetime(datetime_, self._dialog):
            return
        description = (
            self._dialog.description if self._dialog.description is not None else ""
        )
        security_name = self._dialog.security_name
        shares = self._dialog.shares
        sender_path = self._dialog.sender_path
        recipient_path = self._dialog.recipient_path
        tag_names = self._dialog.tag_names

        if not check_for_nonexistent_attributes(
            tag_names, self._record_keeper.tags, self._dialog
        ):
            logging.debug("Dialog aborted")
            return

        logging.info(
            f"Adding SecurityTransfer: {datetime_.strftime('%Y-%m-%d')}, "
            f"{description=}, security='{security_name}', sender='{sender_path}', "
            f"recipient='{recipient_path}', shares={shares}, tags={tag_names}"
        )
        try:
            self._record_keeper.add_security_transfer(
                description,
                datetime_,
                security_name,
                shares,
                sender_path,
                recipient_path,
                tag_names,
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

    def _edit_security_transfers(self) -> None:
        transactions: list[SecurityTransfer] = self._model.get_selected_items()
        uuids = [transaction.uuid for transaction in transactions]

        datetime_ = self._dialog.datetime_
        if datetime_ is not None and not validate_datetime(datetime_, self._dialog):
            return
        description = self._dialog.description

        security_name = self._dialog.security_name
        sender_path = self._dialog.sender_path
        recipient_path = self._dialog.recipient_path
        shares = self._dialog.shares
        tag_names = self._dialog.tag_names

        if tag_names is not None and not check_for_nonexistent_attributes(
            tag_names, self._record_keeper.tags, self._dialog
        ):
            logging.debug("Dialog aborted")
            return

        log = []
        if description is not None:
            log.append(f"{description=}")
        if datetime_ is not None:
            log.append(f"date={datetime_.strftime('%Y-%m-%d')}")
        if security_name is not None:
            log.append(f"security='{security_name}'")
        if sender_path is not None:
            log.append(f"sender='{sender_path}'")
        if recipient_path is not None:
            log.append(f"recipient='{recipient_path}'")
        if shares is not None:
            log.append(f"shares={shares}")
        if tag_names is not None:
            log.append(f"tags={tag_names}")
        logging.info(
            f"Editing {len(transactions)} SecurityTransfer(s): {', '.join(log)}, "
            f"uuids={[str(uuid) for uuid in uuids]}"
        )
        try:
            self._record_keeper.edit_security_transfers(
                uuids,
                description,
                datetime_,
                security_name,
                shares,
                sender_path,
                recipient_path,
                tag_names,
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._dialog.close()
        self.event_update_model()
        self._model.emit_data_changed_for_uuids(uuids)
        self.event_data_changed()

    def _prepare_dialog(self, edit_mode: EditMode) -> bool:
        securities = self._record_keeper.securities
        tag_names = sorted(tag.name for tag in self._record_keeper.tags)
        self._dialog = SecurityTransferDialog(
            self._parent_view,
            securities,
            self._record_keeper.security_accounts,
            tag_names,
            self._record_keeper.descriptions,
            edit_mode=edit_mode,
        )
