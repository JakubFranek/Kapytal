import logging
from collections.abc import Collection, Sequence
from datetime import datetime
from typing import TYPE_CHECKING

from PyQt6.QtWidgets import QWidget
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
)
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.transaction_table_model import TransactionTableModel
from src.views.dialogs.cash_transaction_dialog import CashTransactionDialog, EditMode
from src.views.utilities.handle_exception import display_error_message

if TYPE_CHECKING:
    from src.models.model_objects.attributes import Category


class CashTransactionDialogPresenter:
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
        self, type_: CashTransactionType, valid_accounts: Collection[CashAccount]
    ) -> None:
        if len(valid_accounts) == 0:
            display_error_message(
                "Create at least one Cash Account before creating a transaction.",
                title="Warning",
            )
            return

        self._prepare_dialog(edit_mode=EditMode.ADD)

        self._dialog.type_ = type_
        self._dialog.account = tuple(valid_accounts)[0].path
        self._dialog.datetime_ = datetime.now(user_settings.settings.time_zone)

        self._dialog.signal_account_changed.connect(self._dialog_account_changed)
        self._dialog.signal_do_and_close.connect(
            lambda: self._add_cash_transaction(close=True)
        )
        self._dialog.signal_do_and_continue.connect(
            lambda: self._add_cash_transaction(close=False)
        )
        self._dialog_account_changed()
        self._dialog.exec()

    def run_duplicate_dialog(self, transaction: CashTransaction) -> None:
        self._prepare_dialog(edit_mode=EditMode.ADD)

        self._dialog.type_ = transaction.type_
        self._dialog.account = transaction.account.path
        self._dialog.amount_decimals = transaction.account.currency.places
        self._dialog.currency_code = transaction.account.currency.code
        self._dialog.payee = transaction.payee.name
        self._dialog.datetime_ = transaction.datetime_
        self._dialog.description = transaction.description
        self._dialog.amount = transaction.amount.value_rounded
        category_amount_pairs = [
            (category.name, amount.value_rounded)
            for category, amount in transaction.category_amount_pairs
        ]
        self._dialog.category_amount_pairs = category_amount_pairs
        tag_amount_pairs = [
            (tag.name, amount.value_rounded)
            for tag, amount in transaction.tag_amount_pairs
        ]
        self._dialog.tag_amount_pairs = tag_amount_pairs

        self._dialog.signal_account_changed.connect(self._dialog_account_changed)
        self._dialog.signal_do_and_close.connect(
            lambda: self._add_cash_transaction(close=True)
        )
        self._dialog.signal_do_and_continue.connect(
            lambda: self._add_cash_transaction(close=False)
        )
        self._dialog_account_changed()
        self._dialog.exec()

    def run_edit_dialog(self, transactions: Sequence[CashTransaction]) -> None:
        if not all(
            transaction.type_ == transactions[0].type_ for transaction in transactions
        ):
            display_error_message(
                "All edited Cash Transactions must be of the same type.",
                title="Warning",
            )
            return

        if len(transactions) == 1:
            edit_mode = EditMode.EDIT_SINGLE
        elif all(
            transaction.currency == transactions[0].currency
            for transaction in transactions
        ):
            edit_mode = EditMode.EDIT_MULTIPLE
        else:
            edit_mode = EditMode.EDIT_MULTIPLE_MIXED_CURRENCY

        self._prepare_dialog(edit_mode=edit_mode)

        self._dialog.type_ = transactions[0].type_

        accounts = {transaction.account.path for transaction in transactions}
        self._dialog.account = accounts.pop() if len(accounts) == 1 else ""

        currencies = {transaction.currency for transaction in transactions}
        first_currency = currencies.pop()
        self._dialog.amount_decimals = first_currency.places
        self._dialog.currency_code = first_currency.code

        payees = {transaction.payee.name for transaction in transactions}
        self._dialog.payee = payees.pop() if len(payees) == 1 else ""

        datetimes = {transaction.datetime_ for transaction in transactions}
        self._dialog.datetime_ = (
            datetimes.pop() if len(datetimes) == 1 else self._dialog.min_datetime
        )

        descriptions = {transaction.description for transaction in transactions}
        self._dialog.description = descriptions.pop() if len(descriptions) == 1 else ""

        amounts = {transaction.amount.value_rounded for transaction in transactions}
        self._dialog.amount = (
            amounts.pop() if len(amounts) == 1 else self._dialog.min_amount
        )

        category_amount_pairs_set = {
            transaction.category_amount_pairs for transaction in transactions
        }
        if len(category_amount_pairs_set) == 1:
            pairs = category_amount_pairs_set.pop()
            category_amount_pairs = [
                (category.path, amount.value_rounded) for category, amount in pairs
            ]
        else:
            unique_categories: set[Category] = set()
            for pairs in category_amount_pairs_set:
                for category, _ in pairs:
                    unique_categories.add(category)

            if len(unique_categories) == 1:
                category_amount_pairs = ((unique_categories.pop().path, None),)
            else:
                category_amount_pairs = ()
        self._dialog.category_amount_pairs = category_amount_pairs

        tag_amount_pairs = {
            transaction.tag_amount_pairs for transaction in transactions
        }
        if len(tag_amount_pairs) == 1:
            pairs = tag_amount_pairs.pop()
            tag_amount_pairs = [
                (tag.name, amount.value_rounded) for tag, amount in pairs
            ]
        else:
            tag_amount_pairs = ()
        self._dialog.tag_amount_pairs = tag_amount_pairs

        self._dialog.signal_account_changed.connect(self._dialog_account_changed)
        self._dialog.signal_do_and_close.connect(self._edit_cash_transactions)
        self._dialog_account_changed()
        self._dialog.exec()

    def _dialog_account_changed(self) -> None:
        account_path = self._dialog.account
        if account_path is None:
            return
        for account in self._record_keeper.accounts:
            if account.path == account_path:
                _account: CashAccount = account
                break
        else:
            raise ValueError(f"Invalid Account path: {account_path}")
        self._dialog.currency_code = _account.currency.code
        self._dialog.amount_decimals = _account.currency.places

    def _add_cash_transaction(self, *, close: bool) -> None:
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

        logging.debug("Adding CashTransaction")
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
            logging.info(
                f"Added CashTransaction: {datetime_.strftime('%Y-%m-%d')}, "
                f"{description=}, type={type_.name}, {account=}, {payee=}, "
                f"amount={str(total_amount)} {self._dialog.currency_code}, "
                f"{categories=}, {tags=}"
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

    def _edit_cash_transactions(self) -> None:
        transactions = self._model.get_selected_items()
        uuids = [str(transaction.uuid) for transaction in transactions]

        type_ = self._dialog.type_
        account = self._dialog.account
        payee = self._dialog.payee
        datetime_ = self._dialog.datetime_
        description = self._dialog.description
        category_amount_pairs = self._dialog.category_amount_pairs
        tag_amount_pairs = self._dialog.tag_amount_pairs

        if category_amount_pairs is not None:
            for category, _ in category_amount_pairs:
                if category is None:
                    display_error_message(
                        "A Category must be set if the Amount is also set.",
                        title="Warning",
                    )
                    return

        logging.debug(f"Editing {len(transactions)} CashTransaction")
        try:
            self._record_keeper.edit_cash_transactions(
                uuids,
                description,
                datetime_,
                type_,
                account,
                payee,
                category_amount_pairs,
                tag_amount_pairs,
            )
            logging.info(f"Edited {len(transactions)} CashTransaction(s): {uuids}")
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._dialog.close()
        self.event_update_model()
        self.event_data_changed()

    def _prepare_dialog(self, edit_mode: EditMode) -> bool:
        accounts = [
            account
            for account in self._record_keeper.accounts
            if isinstance(account, CashAccount)
        ]

        payees = sorted(payee.name for payee in self._record_keeper.payees)
        categories_income = (
            self._record_keeper.income_categories
            + self._record_keeper.income_and_expense_categories
        )
        categories_expense = (
            self._record_keeper.expense_categories
            + self._record_keeper.income_and_expense_categories
        )
        category_income_paths = tuple(category.path for category in categories_income)
        category_expense_paths = tuple(category.path for category in categories_expense)
        tag_names = sorted(tag.name for tag in self._record_keeper.tags)
        self._dialog = CashTransactionDialog(
            self._parent_view,
            accounts,
            payees,
            category_income_paths,
            category_expense_paths,
            tag_names,
            edit_mode=edit_mode,
        )
