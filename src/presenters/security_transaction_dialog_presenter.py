import logging
from collections.abc import Collection, Sequence
from datetime import datetime

from PyQt6.QtWidgets import QWidget
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.security_objects import (
    SecurityAccount,
    SecurityTransactionType,
)
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.presenters.utilities.validate_inputs import validate_datetime
from src.view_models.transaction_table_model import TransactionTableModel
from src.views.dialogs.security_transaction_dialog import (
    EditMode,
    SecurityTransactionDialog,
)
from src.views.utilities.handle_exception import display_error_message


class SecurityTransactionDialogPresenter:
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
        type_: SecurityTransactionType,
        valid_accounts: Collection[CashAccount | SecurityAccount],
    ) -> None:
        logging.debug("Running CashTransactionDialog (edit_mode=ADD)")
        valid_cash_accounts = [
            account for account in valid_accounts if isinstance(account, CashAccount)
        ]
        valid_security_accounts = [
            account
            for account in valid_accounts
            if isinstance(account, SecurityAccount)
        ]
        if len(valid_cash_accounts) == 0 or len(valid_security_accounts) == 0:
            display_error_message(
                "Create at least one Cash Account and one Security Account before "
                "creating a Security transaction.",
                title="Warning",
            )
            return

        self._prepare_dialog(edit_mode=EditMode.ADD)

        self._dialog.type_ = type_
        self._dialog.cash_account_path = valid_cash_accounts[0].path
        self._dialog.security_account_path = valid_security_accounts[0].path
        self._dialog.datetime_ = datetime.now(user_settings.settings.time_zone)

        # self._dialog.signal_do_and_close.connect(
        #     lambda: self._add_cash_transaction(close=True)
        # )
        # self._dialog.signal_do_and_continue.connect(
        #     lambda: self._add_cash_transaction(close=False)
        # )

        self._dialog.exec()

    def _prepare_dialog(self, edit_mode: EditMode) -> bool:
        securities = self._record_keeper.securities
        cash_accounts = [
            account
            for account in self._record_keeper.accounts
            if isinstance(account, CashAccount)
        ]
        security_accounts = [
            account
            for account in self._record_keeper.accounts
            if isinstance(account, SecurityAccount)
        ]
        tag_names = sorted(tag.name for tag in self._record_keeper.tags)
        self._dialog = SecurityTransactionDialog(
            self._parent_view,
            securities,
            cash_accounts,
            security_accounts,
            tag_names,
            edit_mode=edit_mode,
        )
