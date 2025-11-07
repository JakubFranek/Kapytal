import logging

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
