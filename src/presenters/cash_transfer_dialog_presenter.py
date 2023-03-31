import logging
from collections.abc import Collection, Sequence
from datetime import datetime

from PyQt6.QtWidgets import QWidget
from src.models.model_objects.cash_objects import CashAccount, CashTransfer
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.transaction_table_model import TransactionTableModel
from src.views.dialogs.cash_transfer_dialog import CashTransferDialog, EditMode
from src.views.utilities.handle_exception import display_error_message


class CashTransferDialogPresenter:
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

    def run_add_dialog(self, valid_accounts: Collection[CashAccount]) -> None:
        logging.debug("Running CashTransferDialog (edit_mode=ADD)")
        if len(valid_accounts) <= 1:
            display_error_message(
                "Create at least two Cash Accounts before creating a Cash Transfer.",
                title="Warning",
            )
            return

        self._prepare_dialog(edit_mode=EditMode.ADD)

        self._dialog.sender_path = tuple(valid_accounts)[0].path
        self._dialog.recipient_path = tuple(valid_accounts)[0].path
        self._dialog.datetime_ = datetime.now(user_settings.settings.time_zone)

        self._dialog.exec()

    def _prepare_dialog(self, edit_mode: EditMode) -> bool:
        accounts = [
            account
            for account in self._record_keeper.accounts
            if isinstance(account, CashAccount)
        ]
        tag_names = sorted(tag.name for tag in self._record_keeper.tags)
        self._dialog = CashTransferDialog(
            self._parent_view,
            accounts,
            tag_names,
            edit_mode=edit_mode,
        )
