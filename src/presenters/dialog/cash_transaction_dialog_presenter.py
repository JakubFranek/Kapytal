import logging
from collections.abc import Collection, Sequence
from datetime import datetime
from typing import TYPE_CHECKING

from src.models.model_objects.attributes import AttributeType
from src.models.model_objects.cash_objects import (
    CashAccount,
    CashTransaction,
    CashTransactionType,
)
from src.models.user_settings import user_settings
from src.presenters.dialog.transaction_dialog_presenter import (
    TransactionDialogPresenter,
)
from src.presenters.utilities.check_for_nonexistent_attributes import (
    check_for_nonexistent_attributes,
    check_for_nonexistent_categories,
)
from src.presenters.utilities.handle_exception import handle_exception
from src.presenters.utilities.validate_inputs import validate_datetime
from src.views.dialogs.cash_transaction_dialog import CashTransactionDialog, EditMode
from src.views.utilities.handle_exception import display_error_message

if TYPE_CHECKING:
    from src.models.model_objects.attributes import Category


class CashTransactionDialogPresenter(TransactionDialogPresenter):
    def run_add_dialog(
        self, type_: CashTransactionType, valid_accounts: Collection[CashAccount]
    ) -> None:
        logging.debug("Running CashTransactionDialog (edit_mode=ADD)")

        if len(self._record_keeper.cash_accounts) == 0:
            display_error_message(
                "Create at least one Cash Account before creating a Cash Transaction.",
                title="Warning",
            )
            return

        self._prepare_dialog(edit_mode=EditMode.ADD)

        _valid_accounts = sorted(
            (account for account in valid_accounts if isinstance(account, CashAccount)),
            key=lambda account: account.path.lower(),
        )
        if len(_valid_accounts) == 1:
            self._dialog.account_path = _valid_accounts[0].path

        self._dialog.type_ = type_
        self._dialog.datetime_ = datetime.now(user_settings.settings.time_zone).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        self._dialog.signal_do_and_close.connect(
            lambda: self._add_cash_transaction(close=True)
        )
        self._dialog.signal_do_and_continue.connect(
            lambda: self._add_cash_transaction(close=False)
        )

        self._dialog.exec()

    def run_duplicate_dialog(self, transaction: CashTransaction) -> None:
        logging.debug("Running duplicate CashTransactionDialog (edit_mode=ADD)")
        self._prepare_dialog(edit_mode=EditMode.ADD)

        self._dialog.type_ = transaction.type_
        self._dialog.account_path = transaction.account.path
        self._dialog.amount_decimals = transaction.account.currency.decimals
        self._dialog.currency_code = transaction.account.currency.code
        self._dialog.payee = transaction.payee.name
        self._dialog.datetime_ = transaction.datetime_
        self._dialog.description = transaction.description
        self._dialog.amount = transaction.amount.value_rounded
        category_amount_pairs = [
            (category.path, amount.value_rounded)
            for category, amount in transaction.category_amount_pairs
        ]
        self._dialog.category_amount_pairs = category_amount_pairs
        tag_amount_pairs = [
            (tag.name, amount.value_rounded)
            for tag, amount in transaction.tag_amount_pairs
        ]
        self._dialog.tag_amount_pairs = tag_amount_pairs

        self._dialog.signal_do_and_close.connect(
            lambda: self._add_cash_transaction(close=True)
        )
        self._dialog.signal_do_and_continue.connect(
            lambda: self._add_cash_transaction(close=False)
        )
        self._dialog.exec()

    def run_edit_dialog(self, transactions: Sequence[CashTransaction]) -> None:
        if len(transactions) == 1:
            edit_mode = EditMode.EDIT_SINGLE
        elif all(
            transaction.currency == transactions[0].currency
            for transaction in transactions
        ):
            edit_mode = EditMode.EDIT_MULTIPLE
        else:
            edit_mode = EditMode.EDIT_MULTIPLE_MIXED_CURRENCY

        logging.debug(f"Running CashTransactionDialog (edit_mode={edit_mode.name})")
        if not all(
            transaction.type_ == transactions[0].type_ for transaction in transactions
        ):
            display_error_message(
                "All edited Cash Transactions must be of the same type.",
                title="Warning",
            )
            return

        self._prepare_dialog(edit_mode=edit_mode)

        self._dialog.type_ = transactions[0].type_

        accounts = {transaction.account.path for transaction in transactions}
        self._dialog.account_path = accounts.pop() if len(accounts) == 1 else ""

        currencies = {transaction.currency for transaction in transactions}
        first_currency = currencies.pop()
        self._dialog.amount_decimals = first_currency.decimals
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

        self._dialog.signal_do_and_close.connect(
            lambda: self._edit_cash_transactions(transactions)
        )

        if any(transaction.is_refunded for transaction in transactions):
            self._dialog.disable_all_widgets()
            display_error_message(
                "Cannot edit Cash Transactions that have been refunded. "
                "Remove the corresponding Refunds first.",
                title="Warning",
            )

        self._dialog.exec()

    def _add_cash_transaction(self, *, close: bool) -> None:
        type_ = self._dialog.type_
        account = self._dialog.account_path
        payee = self._dialog.payee

        if not payee:
            display_error_message(
                "Payee name must be at least 1 character long.", title="Warning"
            )
            return

        datetime_ = self._dialog.datetime_
        if datetime_ is None:
            raise ValueError("Expected datetime_, received None.")
        if not validate_datetime(datetime_, self._dialog):
            return

        description = self._dialog.description if self._dialog.description else ""

        total_amount = self._dialog.amount
        if total_amount is None:
            raise ValueError("Expected Decimal, received None.")
        if total_amount <= 0:
            display_error_message(
                "Transaction amount must be positive.", title="Warning"
            )
            return

        category_amount_pairs = self._dialog.category_amount_pairs
        if category_amount_pairs is None:
            raise ValueError("Expected ((str, Decimal),...), received None.")
        categories = [category for category, _ in category_amount_pairs]
        if any(not category for category in categories):
            display_error_message("Empty Category paths are invalid.", title="Warning")
            return

        tag_amount_pairs = self._dialog.tag_amount_pairs
        if tag_amount_pairs is None:
            raise ValueError("Expected ((str, Decimal),...), received None.")
        if any(amount <= 0 for _, amount in tag_amount_pairs):
            display_error_message("Tag amounts must be positive.", title="Warning")
            return
        tag_names = [tag for tag, _ in tag_amount_pairs]
        if any(not tag for tag in tag_names):
            display_error_message("Empty Tag names are invalid.", title="Warning")
            return

        if (
            not check_for_nonexistent_attributes(
                [payee], self._record_keeper.payees, AttributeType.PAYEE, self._dialog
            )
            or not check_for_nonexistent_categories(
                categories, self._record_keeper.categories, self._dialog
            )
            or not check_for_nonexistent_attributes(
                tag_names, self._record_keeper.tags, AttributeType.TAG, self._dialog
            )
        ):
            logging.debug("Dialog aborted")
            return

        logging.info(
            f"Adding CashTransaction: {datetime_.strftime('%Y-%m-%d')}, "
            f"{description=}, type={type_.name}, {account=}, {payee=}, "
            f"amount={total_amount!s} {self._dialog.currency_code}, "
            f"{categories=}, {tag_names=}"
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

        self.event_pre_add()
        self.event_update_model()
        self.event_post_add()
        if close:
            self._dialog.close()
        self.event_data_changed()

    def _edit_cash_transactions(self, transactions: Sequence[CashTransaction]) -> None:
        uuids = [transaction.uuid for transaction in transactions]
        change_type = any(
            transaction.type_ != transactions[0].type_ for transaction in transactions
        )

        type_ = self._dialog.type_
        account = self._dialog.account_path
        payee = self._dialog.payee

        datetime_ = self._dialog.datetime_
        if datetime_ is not None and not validate_datetime(datetime_, self._dialog):
            return

        description = self._dialog.description

        category_amount_pairs = self._dialog.category_amount_pairs

        if category_amount_pairs is not None:
            categories = [category for category, _ in category_amount_pairs]
            if any(not category for category in categories):
                display_error_message(
                    "Empty Category paths are invalid.", title="Warning"
                )
                return

            for category, _ in category_amount_pairs:
                if category is None:
                    display_error_message(
                        "A Category must be set if the Amount is also set.",
                        title="Warning",
                    )
                    return

            if not check_for_nonexistent_categories(
                categories, self._record_keeper.categories, self._dialog
            ):
                logging.debug("Dialog aborted")
                return

        tag_amount_pairs = self._dialog.tag_amount_pairs
        if tag_amount_pairs is not None:
            if any(amount <= 0 for _, amount in tag_amount_pairs if amount is not None):
                display_error_message("Tag amounts must be positive.", title="Warning")
                return
            tag_names = [tag for tag, _ in tag_amount_pairs]
            if any(not tag for tag in tag_names):
                display_error_message("Empty Tag names are invalid.", title="Warning")
                return
            if not check_for_nonexistent_attributes(
                tag_names, self._record_keeper.tags, AttributeType.TAG, self._dialog
            ):
                logging.debug("Dialog aborted")
                return

        if not check_for_nonexistent_attributes(
            [payee], self._record_keeper.payees, AttributeType.PAYEE, self._dialog
        ):
            logging.debug("Dialog aborted")
            return

        log = []
        if description is not None:
            log.append(f"{description=}")
        if datetime_ is not None:
            log.append(f"date={datetime_.strftime('%Y-%m-%d')}")
        if change_type:
            log.append(f"type='{type_.name}'")
        if account is not None:
            log.append(f"{account=}")
        if payee is not None:
            log.append(f"{payee=}")
        if category_amount_pairs is not None:
            log.append(f"{category_amount_pairs=}")
        if tag_amount_pairs is not None:
            log.append(f"{tag_amount_pairs=}")
        logging.info(
            f"Editing {len(transactions)} CashTransaction(s): {', '.join(log)}, "
            f"uuids={[str(uuid) for uuid in uuids]}"
        )
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
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._dialog.close()
        self.event_update_model()
        self.event_data_changed(uuids)

    def _prepare_dialog(self, edit_mode: EditMode) -> None:
        payees = sorted(payee.name for payee in self._record_keeper.payees)
        categories_income = (
            self._record_keeper.income_categories
            + self._record_keeper.dual_purpose_categories
        )
        categories_expense = (
            self._record_keeper.expense_categories
            + self._record_keeper.dual_purpose_categories
        )
        category_income_paths = tuple(category.path for category in categories_income)
        category_expense_paths = tuple(category.path for category in categories_expense)
        tag_names = sorted(tag.name for tag in self._record_keeper.tags)
        self._dialog = CashTransactionDialog(
            self._parent_view,
            self._record_keeper.cash_accounts,
            payees,
            category_income_paths,
            category_expense_paths,
            tag_names,
            self._record_keeper.descriptions,
            edit_mode=edit_mode,
        )
