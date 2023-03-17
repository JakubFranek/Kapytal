from datetime import datetime

from PyQt6.QtWidgets import QWidget
from src.models.model_objects.cash_objects import CashAccount, CashTransactionType
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.views.dialogs.cash_transaction_dialog import CashTransactionDialog
from src.views.utilities.handle_exception import display_error_message

# TODO: allow adding and editing of CashTransactions


class CashTransactionDialogPresenter:
    def __init__(self, parent_view: QWidget, record_keeper: RecordKeeper) -> None:
        self._parent_view = parent_view
        self.record_keeper = record_keeper

    def run_add_dialog(self, type_: CashTransactionType) -> None:
        accounts = [
            account
            for account in self.record_keeper.accounts
            if isinstance(account, CashAccount)
        ]
        if len(accounts) == 0:
            display_error_message(
                "Create at least one Cash Account first!", title="Warning"
            )
            return

        payees = [payee.name for payee in self.record_keeper.payees]
        categories_income = (
            self.record_keeper.income_categories
            + self.record_keeper.income_and_expense_categories
        )
        categories_expense = (
            self.record_keeper.expense_categories
            + self.record_keeper.income_and_expense_categories
        )
        category_income_paths = tuple(category.path for category in categories_income)
        category_expense_paths = tuple(category.path for category in categories_expense)
        tag_names = sorted(tag.name for tag in self.record_keeper.tags)
        self._dialog = CashTransactionDialog(
            self._parent_view,
            accounts,
            payees,
            category_income_paths,
            category_expense_paths,
            tag_names,
            type_,
            edit=False,
        )
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

    def _dialog_account_changed(self) -> None:
        account_path = self._dialog.account
        for account in self.record_keeper.accounts:
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
        datetime_ = self._dialog.datetime_
        description = self._dialog.description
        category_amount_pairs = self._dialog.category_amount_pairs
        tag_amount_pairs = self._dialog.tag_amount_pairs
        pass
