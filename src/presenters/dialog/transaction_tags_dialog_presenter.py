import logging
from collections.abc import Collection

from PyQt6.QtWidgets import QWidget
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import AttributeType
from src.models.record_keeper import RecordKeeper
from src.presenters.utilities.check_for_nonexistent_attributes import (
    check_for_nonexistent_attributes,
)
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.views.dialogs.transaction_tags_dialog import TransactionTagsDialog


class TransactionTagsDialogPresenter:
    def __init__(
        self,
        parent_view: QWidget,
        record_keeper: RecordKeeper,
    ) -> None:
        self._parent_view = parent_view
        self._record_keeper = record_keeper
        self.event_data_changed = Event()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

    def run_add_dialog(self, transactions: Collection[Transaction]) -> None:
        logging.debug("Running TransactionTagsDialog (Add)")

        tag_names = [tag.name for tag in self._record_keeper.tags]
        if len(transactions) < 1:
            raise ValueError(
                "At least one Transaction must be selected to add Tags to it."
            )
        self._transactions = transactions
        self._dialog = TransactionTagsDialog(self._parent_view, tag_names, add=True)
        self._dialog.signal_ok.connect(self._add_tags)
        self._dialog.exec()

    def run_remove_dialog(self, transactions: Collection[Transaction]) -> None:
        logging.debug("Running TransactionTagsDialog (Remove)")

        tag_names = [tag.name for tag in self._record_keeper.tags]
        if len(transactions) < 1:
            raise ValueError(
                "At least one Transaction must be selected to remove Tags from it."
            )
        self._transactions = transactions
        self._dialog = TransactionTagsDialog(self._parent_view, tag_names, add=False)
        self._dialog.signal_ok.connect(self._remove_tags)
        self._dialog.exec()

    def _add_tags(self) -> None:
        tag_names = self._dialog.tags

        if not check_for_nonexistent_attributes(
            tag_names, self._record_keeper.tags, AttributeType.TAG, self._dialog
        ):
            logging.debug("Dialog aborted")
            return

        uuids = [transaction.uuid for transaction in self._transactions]
        try:
            self._record_keeper.add_tags_to_transactions(uuids, tag_names)
            logging.info(f"Added Tags {tag_names} to Transactions: {uuids}")
            self.event_data_changed()
            self._dialog.close()
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)

    def _remove_tags(self) -> None:
        tag_names = self._dialog.tags

        if not check_for_nonexistent_attributes(
            tag_names, self._record_keeper.tags, AttributeType.TAG, self._dialog
        ):
            logging.debug("Dialog aborted")
            return

        uuids = [transaction.uuid for transaction in self._transactions]
        try:
            self._record_keeper.remove_tags_from_transactions(uuids, tag_names)
            logging.info(f"Removed Tags {tag_names} from Transactions: {uuids}")
            self.event_data_changed()
            self._dialog.close()
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
