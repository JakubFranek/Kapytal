import logging
from collections.abc import Collection, Sequence
from datetime import datetime

from PyQt6.QtWidgets import QWidget
from src.models.base_classes.account import Account
from src.models.model_objects.cash_objects import CashAccount
from src.models.model_objects.security_objects import (
    SecurityAccount,
    SecurityTransaction,
    SecurityTransactionType,
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
        valid_accounts: Collection[Account],
    ) -> None:
        logging.debug("Running SecurityTransactionDialog (edit_mode=ADD)")
        valid_cash_accounts = [
            account for account in valid_accounts if isinstance(account, CashAccount)
        ]
        valid_security_accounts = [
            account
            for account in valid_accounts
            if isinstance(account, SecurityAccount)
        ]
        # FIXME: use RecordKeeper accounts here, not valid (checked) accounts
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

        self._dialog.signal_do_and_close.connect(
            lambda: self._add_security_transaction(close=True)
        )
        self._dialog.signal_do_and_continue.connect(
            lambda: self._add_security_transaction(close=False)
        )

        self._dialog.exec()

    def run_duplicate_dialog(self, transaction: SecurityTransaction) -> None:
        logging.debug("Running duplicate SecurityTransactionDialog (edit_mode=ADD)")
        self._prepare_dialog(edit_mode=EditMode.ADD)

        self._dialog.type_ = transaction.type_
        self._dialog.security_name = transaction.security.name
        self._dialog.cash_account_path = transaction.cash_account.path
        self._dialog.security_account_path = transaction.security_account.path
        self._dialog.shares = transaction.shares
        self._dialog.price_per_share = transaction.price_per_share.value_rounded
        self._dialog.datetime_ = transaction.datetime_
        self._dialog.description = transaction.description
        self._dialog.tag_names = [tag.name for tag in transaction.tags]

        self._dialog.signal_do_and_close.connect(
            lambda: self._add_security_transaction(close=True)
        )
        self._dialog.signal_do_and_continue.connect(
            lambda: self._add_security_transaction(close=False)
        )
        self._dialog.exec()

    def run_edit_dialog(self, transactions: Sequence[SecurityTransaction]) -> None:
        if len(transactions) == 1:
            edit_mode = EditMode.EDIT_SINGLE
        elif len(transactions) > 1:
            currencies = {transaction.currency for transaction in transactions}
            if len(currencies) == 1:
                edit_mode = EditMode.EDIT_MULTIPLE
            else:
                edit_mode = EditMode.EDIT_MULTIPLE_MIXED_CURRENCY
        else:
            raise ValueError(
                "Expected 'transactions' to be a non-empty Sequence of "
                "SecurityTransactions."
            )

        logging.debug(f"Running SecurityTransactionDialog (edit_mode={edit_mode.name})")

        types = {transaction.type_ for transaction in transactions}
        if len(types) > 1:
            display_error_message(
                "Cannot edit multiple Security Transactions with different types.",
                title="Error",
            )
            return

        self._prepare_dialog(edit_mode=edit_mode)

        datetimes = {
            transaction.datetime_.replace(hour=0, minute=0, second=0, microsecond=0)
            for transaction in transactions
        }
        self._dialog.datetime_ = (
            datetimes.pop() if len(datetimes) == 1 else self._dialog.min_datetime
        )

        descriptions = {transaction.description for transaction in transactions}
        self._dialog.description = descriptions.pop() if len(descriptions) == 1 else ""

        self._dialog.type_ = types.pop()

        security_names = {transaction.security.name for transaction in transactions}
        self._dialog.security_name = (
            security_names.pop() if len(security_names) == 1 else ""
        )

        cash_account_paths = {
            transaction.cash_account.path for transaction in transactions
        }
        self._dialog.cash_account_path = (
            cash_account_paths.pop() if len(cash_account_paths) == 1 else ""
        )

        security_account_paths = {
            transaction.security_account.path for transaction in transactions
        }
        self._dialog.security_account_path = (
            security_account_paths.pop() if len(security_account_paths) == 1 else ""
        )

        shares = {transaction.shares for transaction in transactions}
        self._dialog.shares = shares.pop() if len(shares) == 1 else 0

        prices = {transaction.price_per_share for transaction in transactions}
        self._dialog.price_per_share = (
            prices.pop().value_rounded if len(prices) == 1 else 0
        )

        tag_names_frozensets = set()
        for transaction in transactions:
            tag_names_frozenset = frozenset(tag.name for tag in transaction.tags)
            tag_names_frozensets.add(tag_names_frozenset)

        self._dialog.tag_names = (
            sorted(tag_names_frozensets.pop()) if len(tag_names_frozensets) == 1 else ()
        )

        self._dialog.signal_do_and_close.connect(self._edit_security_transactions)
        self._dialog.exec()

    def _add_security_transaction(self, *, close: bool) -> None:
        datetime_ = self._dialog.datetime_
        if datetime_ is None:
            raise ValueError("Expected datetime_, received None.")
        if not validate_datetime(datetime_, self._dialog):
            return
        description = (
            self._dialog.description if self._dialog.description is not None else ""
        )
        security_name = self._dialog.security_name
        type_ = self._dialog.type_
        shares = self._dialog.shares
        price_per_share = self._dialog.price_per_share
        security_account_path = self._dialog.security_account_path
        cash_account_path = self._dialog.cash_account_path
        tag_names = self._dialog.tag_names

        cash_account = self._record_keeper.get_account(cash_account_path, CashAccount)

        logging.info(
            f"Adding SecurityTransaction: {datetime_.strftime('%Y-%m-%d')}, "
            f"{description=}, type={type_.name}, security='{security_name}', "
            f"cash_account='{cash_account_path}', "
            f"security_account_path='{security_account_path}', shares={shares}, "
            f"price_per_share={price_per_share} {cash_account.currency.code}, "
            f"tags={tag_names}"
        )
        try:
            self._record_keeper.add_security_transaction(
                description,
                datetime_,
                type_,
                security_name,
                shares,
                price_per_share,
                security_account_path,
                cash_account_path,
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

    def _edit_security_transactions(self) -> None:
        transactions: list[SecurityTransaction] = self._model.get_selected_items()
        uuids = [transaction.uuid for transaction in transactions]

        datetime_ = self._dialog.datetime_
        if datetime_ is not None and not validate_datetime(datetime_, self._dialog):
            return
        description = self._dialog.description

        type_ = self._dialog.type_
        security_name = self._dialog.security_name
        cash_account_path = self._dialog.cash_account_path
        security_account_path = self._dialog.security_account_path
        shares = self._dialog.shares
        price_per_share = self._dialog.price_per_share
        tag_names = self._dialog.tag_names

        if not check_for_nonexistent_attributes(
            tag_names, self._record_keeper.tags, self._dialog, "Tag"
        ):
            logging.info("Dialog aborted")
            return

        log = []
        if description is not None:
            log.append(f"{description=}")
        if datetime_ is not None:
            log.append(f"date={datetime_.strftime('%Y-%m-%d')}")
        if type_ is not None:
            log.append(f"type={type_.name}")
        if security_name is not None:
            log.append(f"security='{security_name}'")
        if cash_account_path is not None:
            log.append(f"cash_account='{cash_account_path}'")
        if security_account_path is not None:
            log.append(f"security_account='{security_account_path}'")
        if shares is not None:
            log.append(f"shares={shares}")
        if price_per_share is not None:
            log.append(
                f"price_per_share={price_per_share} {self._dialog.currency_code}"
            )
        if tag_names is not None:
            log.append(f"tags={tag_names}")
        logging.info(
            f"Editing {len(transactions)} SecurityTransaction(s): {', '.join(log)}, "
            f"uuids={[str(uuid) for uuid in uuids]}"
        )
        try:
            self._record_keeper.edit_security_transactions(
                uuids,
                description,
                datetime_,
                type_,
                security_name,
                cash_account_path,
                security_account_path,
                price_per_share,
                shares,
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
        self._dialog = SecurityTransactionDialog(
            self._parent_view,
            securities,
            self._record_keeper.cash_accounts,
            self._record_keeper.security_accounts,
            tag_names,
            edit_mode=edit_mode,
        )