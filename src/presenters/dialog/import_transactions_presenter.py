import csv
import json
import logging
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.models.custom_exceptions import NotFoundError
from src.models.model_objects.attributes import CategoryType
from src.models.model_objects.cash_objects import CashAccount, CashTransactionType
from src.models.model_objects.currency_objects import Currency
from src.presenters.dialog.transaction_dialog_presenter import (
    TransactionDialogPresenter,
)
from src.presenters.utilities.handle_exception import handle_exception
from src.views.dialogs.import_transactions_dialog import ImportTransactionsDialog
from src.views.utilities.handle_exception import display_error_message


class ImportTransactionsDialogPresenter(TransactionDialogPresenter):
    def run_dialog(self) -> None:
        logging.debug("Running ImportTransactionsDialog")
        if len(self._record_keeper.cash_accounts) == 0:
            display_error_message(
                "Create at least one Cash Account before importing Transactions.",
                title="Warning",
            )
            return

        account_paths = (account.path for account in self._record_keeper.cash_accounts)
        self._dialog = ImportTransactionsDialog(self._parent_view, account_paths)

        self._dialog.signal_ok.connect(self._import_transactions)

        self._dialog.exec()

    def _import_transactions(self) -> None:
        cash_account_path = self._dialog.cash_account
        try:
            currency = self._record_keeper.get_account(
                cash_account_path, CashAccount
            ).currency
        except NotFoundError:
            display_error_message(
                f"Could not find Cash Account at {cash_account_path}.",
                title="Error",
            )
            return

        path_transaction_data = Path(self._dialog.path_transaction_data)
        path_import_profile = Path(self._dialog.path_import_profile)
        path_payee_map = Path(self._dialog.path_payee_mapping)

        try:
            profile_dict = _read_json(path_import_profile)
            payee_map = _read_json(path_payee_map)
            column_dict = profile_dict["columns"]
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        transactions_added = 0

        if not path_transaction_data.exists():
            display_error_message(
                f"Could not find transaction data at {path_transaction_data}.",
                title="Error",
            )
            return
        with path_transaction_data.open(
            encoding=profile_dict["encoding"]
        ) as transaction_data_file:
            reader = csv.reader(
                transaction_data_file,
                delimiter=profile_dict["column_delimiter"],
                quotechar=profile_dict["quote_char"],  # TODO: test this
            )
            if profile_dict["has_header"]:
                next(reader)
            for row in reader:
                try:
                    date_str = _parse_field(row, column_dict["date"])
                    datetime_ = _parse_date(date_str, column_dict["date"])

                    description = _parse_field(row, column_dict["description"])
                    amount = _parse_amount(
                        _parse_field(row, column_dict["amount"]), column_dict["amount"]
                    )
                    iban = _parse_field(row, column_dict["iban"])
                    payee = _parse_field(row, column_dict["payee"])
                    payee = payee_map.get(
                        payee, payee
                    )  # Replace payee with mapped payee
                    category = _parse_field(row, column_dict["category"])
                    tag = _parse_field(row, column_dict["tag"])

                    iban_account_path = (
                        self._get_account_path_from_iban(iban) if iban else ""
                    )
                    if iban_account_path:
                        # IBAN account found, this is going to be a Cash Transfer
                        self._add_cash_transfer(
                            description=description,
                            datetime_=datetime_,
                            amount=amount,
                            currency=currency,
                            cash_account_path=cash_account_path,
                            iban_account_path=iban_account_path,
                            tag=tag,
                        )
                    else:
                        # IBAN account not found, this is going to be a Cash Transaction
                        self._add_cash_transaction(
                            description=description,
                            datetime_=datetime_,
                            amount=amount,
                            currency=currency,
                            cash_account_path=cash_account_path,
                            payee=payee,
                            category=category,
                            tag=tag,
                        )

                    transactions_added += 1
                except Exception as exception:  # noqa: BLE001
                    handle_exception(exception)
                    break  # Stop adding transactions upon error

        self.event_pre_add(transactions_added)
        self.event_update_model()
        self.event_post_add()
        self._dialog.close()
        self.event_data_changed()

    def _get_account_path_from_iban(self, iban: str) -> str:
        for account in self._record_keeper.cash_accounts:
            if account.iban == iban:
                return account.path
        return ""

    def _add_cash_transaction(
        self,
        description: str,
        datetime_: datetime,
        amount: Decimal,
        currency: Currency,
        cash_account_path: str,
        payee: str,
        category: str,
        tag: str,
    ) -> None:
        if amount < 0:
            transaction_type = CashTransactionType.EXPENSE
        else:
            transaction_type = CashTransactionType.INCOME

        try:
            self._record_keeper.get_category(category)
        except NotFoundError:
            logging.info(
                f"Adding Category: path={category}, type={CategoryType.DUAL_PURPOSE}"
            )
            self._record_keeper.add_category(category, CategoryType.DUAL_PURPOSE)

        logging.info(
            f"Adding CashTransaction: {datetime_.strftime('%Y-%m-%d')}, "
            f"{description=}, type={transaction_type.name}, "
            f"{cash_account_path=}, {payee=}, "
            f"amount={amount!s} {currency.code}, "
            f"{category=}, {tag=}"
        )

        self._record_keeper.add_cash_transaction(
            description=description,
            datetime_=datetime_,
            transaction_type=transaction_type,
            account_path=cash_account_path,
            payee_name=payee,
            category_path_amount_pairs=((category, abs(amount)),),
            tag_name_amount_pairs=((tag, abs(amount)),),
        )

    def _add_cash_transfer(
        self,
        description: str,
        datetime_: datetime,
        amount: Decimal,
        currency: Currency,
        cash_account_path: str,
        iban_account_path: str,
        tag: str,
    ) -> None:
        if amount < 0:
            sender_path = cash_account_path
            recipient_path = iban_account_path
        else:
            sender_path = iban_account_path
            recipient_path = cash_account_path

        logging.info(
            f"Adding CashTransfer: {datetime_.strftime('%Y-%m-%d')}, "
            f"{description=}, sender={sender_path}, "
            f"sent={amount} {currency.code}, recipient={recipient_path}, "
            f"received={amount} {currency.code}, {tag=}"
        )

        self._record_keeper.add_cash_transfer(
            description=description,
            datetime_=datetime_,
            account_sender_path=sender_path,
            account_recipient_path=recipient_path,
            amount_sent=abs(amount),
            amount_received=abs(amount),
            tag_names=(tag,),
        )


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open(encoding="utf-8-sig") as import_profile_file:
        return json.load(import_profile_file)


def _parse_field(csv_row: str, profile: dict[str, Any]) -> str:
    # Constant value
    if "constant" in profile:
        return profile["constant"]

    # Multiple indices
    if "indices" in profile:
        if "join_with" in profile:  # Join non-empty strings from multiple indices
            return profile["join_with"].join(
                [
                    csv_row[i].strip()
                    for i in profile["indices"]
                    if i < len(csv_row) and csv_row[i].strip() != ""
                ]
            )

        # Use the first index which is not empty, and ignore the rest
        for i in profile["indices"]:
            if i < len(csv_row) and csv_row[i].strip() != "":
                return csv_row[i].strip()
        if "fallback" in profile:
            return profile["fallback"]
        raise ValueError("No non-empty index found")

    # Single index
    if "index" in profile:
        i = profile["index"]
        if i >= len(csv_row):
            raise ValueError(f"Index {i} out of range")
        return csv_row[i].strip()

    raise ValueError(f"Invalid profile: {profile}")


def _parse_amount(raw: str, profile: dict[str, Any]) -> Decimal:
    raw = raw.strip()
    raw = raw.replace(profile.get("thousand_separator", ""), "")
    raw = raw.replace(profile.get("decimal_separator", "."), ".")
    return Decimal(raw)


def _parse_date(raw: str, profile: dict[str, Any]) -> datetime:
    date_format = profile["format"]
    return datetime.strptime(raw.strip(), date_format)  # noqa: DTZ007
