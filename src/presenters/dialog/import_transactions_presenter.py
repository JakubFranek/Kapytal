import csv
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from src.models.base_classes.account import Account
from src.models.custom_exceptions import NotFoundError
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.cash_objects import CashAccount
from src.models.record_keeper import RecordKeeper
from src.presenters.dialog.transaction_dialog_presenter import (
    TransactionDialogPresenter,
)
from src.presenters.utilities.event import Event
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
        cash_account_name = self._dialog.cash_account
        path_transaction_data = Path(self._dialog.path_transaction_data)
        path_import_profile = Path(self._dialog.path_import_profile)
        path_payee_map = Path(self._dialog.path_payee_mapping)

        profile_dict = _read_import_profile(path_import_profile)
        column_dict = profile_dict["columns"]

        with path_transaction_data.open(
            encoding=profile_dict["encoding"]
        ) as transaction_data_file:
            reader = csv.reader(
                transaction_data_file,
                delimiter=profile_dict["column_delimiter"],
                quotechar=profile_dict["quote_char"],
            )
            if profile_dict["has_header"]:
                next(reader)
            for row in reader:
                date_str = _parse_field(row, column_dict["date"])
                date = _parse_date(date_str, column_dict["date"])

                description = _parse_field(row, column_dict["description"])
                amount = _parse_amount(
                    _parse_field(row, column_dict["amount"]), column_dict["amount"]
                )
                iban = _parse_field(row, column_dict["iban"])
                payee = _parse_field(row, column_dict["payee"])
                category = _parse_field(row, column_dict["category"])
                tag = _parse_field(row, column_dict["tag"])
                pass

        # datetime_ = self._dialog.datetime_
        # if datetime_ is None:
        #     raise ValueError("Expected datetime_, received None.")
        # if not validate_datetime(datetime_, self._dialog):
        #     return
        # description = (
        #     self._dialog.description if self._dialog.description is not None else ""
        # )
        # security_name = self._dialog.security_name
        # type_ = self._dialog.type_
        # shares = self._dialog.shares
        # amount_per_share = self._dialog.amount_per_share
        # security_account_path = self._dialog.security_account_path
        # cash_account_path = self._dialog.cash_account_path
        # tag_names = self._dialog.tag_names

        # if not check_for_nonexistent_attributes(
        #     tag_names, self._record_keeper.tags, AttributeType.TAG, self._dialog
        # ):
        #     logging.debug("Dialog aborted")
        #     return

        # try:
        #     cash_account = self._record_keeper.get_account(
        #         cash_account_path, CashAccount
        #     )
        # except Exception as exception:  # noqa: BLE001
        #     handle_exception(exception)
        #     return

        # logging.info(
        #     f"Adding SecurityTransaction: {datetime_.strftime('%Y-%m-%d')}, "
        #     f"{description=}, type={type_.name}, security='{security_name}', "
        #     f"cash_account='{cash_account_path}', "
        #     f"security_account_path='{security_account_path}', shares={shares}, "
        #     f"amount_per_share={amount_per_share} {cash_account.currency.code}, "
        #     f"tags={tag_names}"
        # )
        # try:
        #     self._record_keeper.add_security_transaction(
        #         description,
        #         datetime_,
        #         type_,
        #         security_name,
        #         shares,
        #         amount_per_share,
        #         security_account_path,
        #         cash_account_path,
        #         tag_names,
        #     )
        # except Exception as exception:  # noqa: BLE001
        #     handle_exception(exception)
        #     return

        # self.event_pre_add()
        # self.event_update_model()
        # self.event_post_add()
        self._dialog.close()
        # self.event_data_changed()


def _read_import_profile(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8-sig") as import_profile_file:
        return json.load(import_profile_file)


def _parse_field(csv_row: str, profile: dict[str, Any]) -> str:
    # Constant value
    if "constant" in profile:
        return profile["constant"]

    # Multiple indices
    if "indices" in profile:
        if "join_with" in profile:  # Join non-empty strings from multiple indices
            return " ".join(
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
        raise ValueError("No non-empty index found")

    # Single index
    if "index" in profile:
        i = profile["index"]
        if i >= len(csv_row):
            raise ValueError(f"Index {i} out of range")
        return csv_row[i].strip()

    raise ValueError(f"Invalid profile: {profile}")


def _parse_amount(raw: str, profile: dict[str, Any]) -> Decimal | None:
    raw = raw.strip()
    raw = raw.replace(profile.get("thousand_separator", ""), "")
    raw = raw.replace(profile.get("decimal_separator", "."), ".")
    try:
        return Decimal(raw)
    except ValueError:
        return None


def _parse_date(raw: str, profile: dict[str, Any]) -> datetime:
    date_format = profile["format"]
    return datetime.strptime(raw.strip(), date_format)  # noqa: DTZ007
