import logging
from enum import Enum

from PyQt6.QtWidgets import QWidget
from src.models.record_keeper import RecordKeeper
from src.models.utilities.transaction_filter import FilterMode, TransactionFilter
from src.presenters.utilities.event import Event
from src.views.forms.transaction_filter_form import TransactionFilterForm


class TransactionFilterFormPresenter:
    event_filter_changed = Event()

    def __init__(self, parent_view: QWidget, record_keeper: RecordKeeper) -> None:
        self._parent_view = parent_view

        self._form = TransactionFilterForm(parent_view)
        self._transaction_filter = TransactionFilter()

        self._form.signal_ok.connect(self._form_accepted)
        self._form.signal_restore_defaults.connect(
            self._transaction_filter.restore_defaults
        )
        self.load_record_keeper(record_keeper)
        self._update_form_from_transaction_filter()

    @property
    def transaction_filter(self) -> TransactionFilter:
        return self._transaction_filter

    @transaction_filter.setter
    def transaction_filter(self, transaction_filter: TransactionFilter) -> None:
        self._transaction_filter = transaction_filter
        self._update_form_from_transaction_filter()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

    def show_form(self) -> None:
        self._form.show_form()

    def _form_accepted(self) -> None:
        new_filter = self._get_transaction_filter_from_form()
        if self.transaction_filter != new_filter:
            self._log_filter_differences(new_filter)
            self._transaction_filter = new_filter
            self.event_filter_changed()
        self._form.close()

    def _get_transaction_filter_from_form(self) -> TransactionFilter:
        transaction_filter = TransactionFilter()
        transaction_filter.set_type_filter(self._form.types, FilterMode.KEEP)
        transaction_filter.set_datetime_filter(
            self._form.date_filter_start,
            self._form.date_filter_end,
            self._form.date_filter_mode,
        )
        transaction_filter.set_description_filter(
            self._form.description_filter_pattern, self._form.description_filter_mode
        )
        return transaction_filter

    def _log_filter_differences(self, new_filter: TransactionFilter) -> None:
        logging.info("TransactionFilter changed, see log records below")
        old_filter = self._transaction_filter

        if old_filter.type_filter != new_filter.type_filter:
            types = []
            for type_ in new_filter.type_filter.types:
                if isinstance(type_, Enum):
                    types.append(type_.name)
                else:
                    types.append(type_.__name__)
            logging.info(
                f"TypeFilter changed: mode={new_filter.type_filter.mode.name}, "
                f"types={types}"
            )
        if old_filter.datetime_filter != new_filter.datetime_filter:
            logging.info(
                f"DateTimeFilter changed: mode={new_filter.datetime_filter.mode.name}, "
                f"start={new_filter.datetime_filter.start.strftime('%Y-%m-%d')}, "
                f"end={new_filter.datetime_filter.end.strftime('%Y-%m-%d')}"
            )
        if old_filter.description_filter != new_filter.description_filter:
            logging.info(
                "DescriptionFilter changed: "
                f"mode={new_filter.description_filter.mode.name}, "
                f"pattern='{new_filter.description_filter.regex_pattern}'"
            )
        if old_filter.account_filter != new_filter.account_filter:
            logging.info(
                f"AccountFilter changed: mode={new_filter.account_filter.mode.name}, "
                f"accounts={new_filter.account_filter.accounts}"
            )

    def _update_form_from_transaction_filter(self) -> None:
        self._form.types = self._transaction_filter.type_filter.types
        self._form.date_filter_mode = self._transaction_filter.datetime_filter.mode
        self._form.date_filter_start = self._transaction_filter.datetime_filter.start
        self._form.date_filter_end = self._transaction_filter.datetime_filter.end
        self._form.description_filter_mode = (
            self._transaction_filter.description_filter.mode
        )
        self._form.description_filter_pattern = (
            self._transaction_filter.description_filter.regex_pattern
        )
