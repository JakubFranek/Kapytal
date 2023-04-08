import logging
from collections.abc import Collection
from enum import Enum

from PyQt6.QtWidgets import QWidget
from src.models.base_classes.account import Account
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.filter_mode_mixin import FilterMode
from src.models.transaction_filters.transaction_filter import TransactionFilter
from src.presenters.form.transaction_filter.tag_filter_presenter import (
    TagFilterPresenter,
)
from src.presenters.utilities.event import Event
from src.views.forms.transaction_filter_form import (
    AccountFilterMode,
    TransactionFilterForm,
)


class TransactionFilterFormPresenter:
    event_filter_changed = Event()

    def __init__(
        self,
        parent_view: QWidget,
        record_keeper: RecordKeeper,
        account_tree_shown_accounts: Collection[Account],
    ) -> None:
        self._parent_view = parent_view

        self._account_tree_shown_accounts = tuple(account_tree_shown_accounts)

        self._form = TransactionFilterForm(parent_view)

        self._tag_filter_presenter = TagFilterPresenter(self._form, record_keeper)
        self.load_record_keeper(record_keeper)
        self._transaction_filter = self._get_default_filter()

        self._form.signal_ok.connect(self._form_accepted)
        self._form.signal_restore_defaults.connect(self._restore_defaults)
        self._update_form_from_transaction_filter()

    @property
    def transaction_filter(self) -> TransactionFilter:
        return self._transaction_filter

    @transaction_filter.setter
    def transaction_filter(self, transaction_filter: TransactionFilter) -> None:
        self._transaction_filter = transaction_filter
        self._update_form_from_transaction_filter()

    @property
    def account_tree_shown_accounts(self) -> tuple[Account]:
        return self._account_tree_shown_accounts

    @account_tree_shown_accounts.setter
    def account_tree_shown_accounts(self, accounts: Collection[Account]) -> None:
        self._account_tree_shown_accounts = tuple(accounts)
        if self._form.account_filter_mode == AccountFilterMode.ACCOUNT_TREE:
            self._transaction_filter.set_account_filter(accounts, FilterMode.KEEP)

    @property
    def filter_active(self) -> bool:
        return self._transaction_filter != self._default_filter

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._tag_filter_presenter.load_record_keeper(record_keeper)
        self._setup_default_filter()

    def show_form(self) -> None:
        self._form.show_form()

    def _form_accepted(self) -> None:
        new_filter = self._get_transaction_filter_from_form()
        if self.transaction_filter != new_filter:
            if new_filter == self._default_filter:
                logging.info("TransactionFilter reverted to default")
                self._transaction_filter = new_filter
            else:
                self._log_filter_differences(new_filter)
                self._transaction_filter = new_filter
            self.event_filter_changed()
        self._form.close()

    def _get_transaction_filter_from_form(self) -> TransactionFilter:
        filter_ = TransactionFilter()
        filter_.set_type_filter(self._form.types, FilterMode.KEEP)
        filter_.set_datetime_filter(
            self._form.date_filter_start,
            self._form.date_filter_end,
            self._form.date_filter_mode,
        )
        filter_.set_description_filter(
            self._form.description_filter_pattern, self._form.description_filter_mode
        )

        if self._form.account_filter_mode != AccountFilterMode.ACCOUNT_TREE:
            # get selected Accounts
            # set AccountFilter
            raise NotImplementedError

        filter_.set_specific_tags_filter(
            self._tag_filter_presenter.checked_tags, FilterMode.KEEP
        )
        filter_.set_tagless_filter(self._tag_filter_presenter.tagless_filter_mode)
        filter_.set_split_tags_filter(self._tag_filter_presenter.split_tags_filter_mode)

        return filter_

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
        self._tag_filter_presenter.load_from_tag_filters(
            self._transaction_filter.specific_tags_filter,
            self._transaction_filter.tagless_filter,
            self._transaction_filter.split_tags_filter,
        )

    def _restore_defaults(self) -> None:
        logging.info("Restoring TransactionFilter to default")
        self._transaction_filter.restore_defaults()
        self._update_form_from_transaction_filter()

    def _setup_default_filter(self) -> None:
        self._default_filter = self._get_default_filter()

    def _get_default_filter(self) -> TransactionFilter:
        filter_ = TransactionFilter()
        filter_.set_specific_tags_filter(self._record_keeper.tags, FilterMode.KEEP)
        return filter_
