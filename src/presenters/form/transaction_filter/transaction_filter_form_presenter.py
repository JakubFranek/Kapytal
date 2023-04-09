import logging
from collections.abc import Collection

from PyQt6.QtWidgets import QWidget
from src.models.base_classes.account import Account
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.base_transaction_filter import FilterMode
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
        self._update_form_from_filter(self._transaction_filter)

    @property
    def transaction_filter(self) -> TransactionFilter:
        return self._transaction_filter

    @transaction_filter.setter
    def transaction_filter(self, transaction_filter: TransactionFilter) -> None:
        self._transaction_filter = transaction_filter
        self._update_form_from_filter(self._transaction_filter)

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
        self._transaction_filter = self._get_default_filter()
        self._update_form_from_filter(self._transaction_filter)
        logging.debug("TransactionFilter reverted to default")
        self.event_filter_changed()

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
        old_filter = self._transaction_filter

        if new_filter == self._default_filter:
            logging.info("TransactionFilter reverted to default")
            return

        if old_filter.type_filter != new_filter.type_filter:
            logging.info(
                f"TypeFilter changed: mode={new_filter.type_filter.mode.name}, "
                f"types={new_filter.type_filter.type_names}"
            )
        if old_filter.datetime_filter != new_filter.datetime_filter:
            logging.info(
                f"DatetimeFilter changed: mode={new_filter.datetime_filter.mode.name}, "
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
        if old_filter.specific_tags_filter != new_filter.specific_tags_filter:
            logging.info(
                "SpecificTagsFilter changed: "
                f"mode={new_filter.specific_tags_filter.mode.name}, "
                f"tags={new_filter.specific_tags_filter.tags}"
            )
        if old_filter.tagless_filter != new_filter.tagless_filter:
            logging.info(
                f"TaglessFilter changed: mode={new_filter.tagless_filter.mode.name}"
            )
        if old_filter.split_tags_filter != new_filter.split_tags_filter:
            logging.info(
                "SplitTagsFilter changed: "
                f"mode={new_filter.split_tags_filter.mode.name}"
            )

    def _update_form_from_filter(self, filter_: TransactionFilter) -> None:
        self._form.types = filter_.type_filter.types
        self._form.date_filter_mode = filter_.datetime_filter.mode
        self._form.date_filter_start = filter_.datetime_filter.start
        self._form.date_filter_end = filter_.datetime_filter.end
        self._form.description_filter_mode = filter_.description_filter.mode
        self._form.description_filter_pattern = filter_.description_filter.regex_pattern
        self._tag_filter_presenter.load_from_tag_filters(
            filter_.specific_tags_filter,
            filter_.tagless_filter,
            filter_.split_tags_filter,
        )

    def _restore_defaults(self) -> None:
        logging.info("Restoring TransactionFilterForm to default")
        self._update_form_from_filter(self._default_filter)

    def _setup_default_filter(self) -> None:
        self._default_filter = self._get_default_filter()

    def _get_default_filter(self) -> TransactionFilter:
        filter_ = TransactionFilter()
        filter_.set_specific_tags_filter(self._record_keeper.tags, FilterMode.KEEP)
        return filter_
