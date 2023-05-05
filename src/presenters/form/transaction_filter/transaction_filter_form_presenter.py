import logging
from collections.abc import Collection

from PyQt6.QtWidgets import QWidget
from src.models.base_classes.account import Account
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import (
    CashTransactionType,
    CashTransfer,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import CashAmount
from src.models.model_objects.security_objects import (
    SecurityTransactionType,
    SecurityTransfer,
)
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.transaction_filters.transaction_filter import TransactionFilter
from src.presenters.form.transaction_filter.account_filter_presenter import (
    AccountFilterPresenter,
)
from src.presenters.form.transaction_filter.category_filter_presenter import (
    CategoryFilterPresenter,
)
from src.presenters.form.transaction_filter.currency_filter_presenter import (
    CurrencyFilterPresenter,
)
from src.presenters.form.transaction_filter.payee_filter_presenter import (
    PayeeFilterPresenter,
)
from src.presenters.form.transaction_filter.security_filter_presenter import (
    SecurityFilterPresenter,
)
from src.presenters.form.transaction_filter.tag_filter_presenter import (
    TagFilterPresenter,
)
from src.presenters.utilities.event import Event
from src.views.forms.transaction_filter_form import (
    AccountFilterMode,
    TransactionFilterForm,
)
from src.views.utilities.handle_exception import display_error_message
from src.views.utilities.message_box_functions import ask_yes_no_question

currency_related_types = {
    CashTransactionType.EXPENSE,
    CashTransactionType.INCOME,
    RefundTransaction,
    CashTransfer,
    SecurityTransactionType.BUY,
    SecurityTransactionType.SELL,
}
payee_related_types = {
    CashTransactionType.EXPENSE,
    CashTransactionType.INCOME,
    RefundTransaction,
}
security_related_types = {
    SecurityTransactionType.BUY,
    SecurityTransactionType.SELL,
    SecurityTransfer,
}
category_related_types = {
    CashTransactionType.EXPENSE,
    CashTransactionType.INCOME,
    RefundTransaction,
}

ordered_types = (
    CashTransactionType.INCOME,
    CashTransactionType.EXPENSE,
    RefundTransaction,
    CashTransfer,
    SecurityTransfer,
    SecurityTransactionType.BUY,
    SecurityTransactionType.SELL,
)


def get_type_names(
    types: Collection[
        type[Transaction] | CashTransactionType | SecurityTransactionType
    ],
) -> tuple[str]:
    type_names_: list[str] = []
    ordered_types_: list[
        type[Transaction] | CashTransactionType | SecurityTransactionType
    ] = order_subset(ordered_types, types)

    for type_ in ordered_types_:
        if isinstance(type_, CashTransactionType | SecurityTransactionType):
            type_names_.append(type_.name.capitalize())
        else:
            name = type_.__name__
            # insert space in front of each capital letter (except for the first one)
            for i in range(1, len(name)):
                if name[i].isupper():
                    name = name[:i] + " " + name[i:]
            type_names_.append(name)

    return tuple(type_names_)


def order_subset(reference_list: list, subset_list: list) -> list:
    index_dict = {item: index for index, item in enumerate(reference_list)}
    return sorted(subset_list, key=lambda x: index_dict[x])


class TransactionFilterFormPresenter:
    event_filter_changed = Event()

    def __init__(
        self,
        parent_view: QWidget,
        record_keeper: RecordKeeper,
        account_tree_shown_accounts: Collection[Account],
    ) -> None:
        self._parent_view = parent_view
        self._record_keeper = record_keeper

        self._account_tree_shown_accounts = tuple(account_tree_shown_accounts)

        base_currency_code = (
            record_keeper.base_currency.code
            if record_keeper.base_currency is not None
            else ""
        )
        self._form = TransactionFilterForm(parent_view, base_currency_code)

        self._account_filter_presenter = AccountFilterPresenter(
            self._form, record_keeper
        )
        self._tag_filter_presenter = TagFilterPresenter(self._form, record_keeper)
        self._payee_filter_presenter = PayeeFilterPresenter(self._form, record_keeper)
        self._category_filter_presenter = CategoryFilterPresenter(
            self._form, record_keeper
        )
        self._currency_filter_presenter = CurrencyFilterPresenter(
            self._form, record_keeper
        )
        self._security_filter_presenter = SecurityFilterPresenter(
            self._form, record_keeper
        )
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
        self._account_filter_presenter.load_record_keeper(record_keeper)
        self._tag_filter_presenter.load_record_keeper(record_keeper)
        self._payee_filter_presenter.load_record_keeper(record_keeper)
        self._category_filter_presenter.load_record_keeper(record_keeper)
        self._currency_filter_presenter.load_record_keeper(record_keeper)
        self._security_filter_presenter.load_record_keeper(record_keeper)
        self.reset_filter_to_default()

    def reset_filter_to_default(self) -> None:
        self._setup_default_filter()
        self._transaction_filter = self._get_default_filter()
        self._update_form_from_filter(self._transaction_filter)
        logging.debug("TransactionFilter reset to default")
        self.event_filter_changed()

    def show_form(self) -> None:
        self._update_form_from_filter(self._transaction_filter)
        self._form.show_form()

    def _form_accepted(self) -> None:
        if self._check_filter_form_sanity() is False:
            return
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

        if self._form.account_filter_mode == AccountFilterMode.SELECTION:
            filter_.set_account_filter(
                self._account_filter_presenter.checked_accounts, FilterMode.KEEP
            )

        filter_.set_specific_tags_filter(
            self._tag_filter_presenter.checked_tags,
            self._tag_filter_presenter.specific_tag_filter_mode,
        )
        filter_.set_tagless_filter(self._tag_filter_presenter.tagless_filter_mode)
        filter_.set_split_tags_filter(self._tag_filter_presenter.split_tags_filter_mode)
        filter_.set_payee_filter(
            self._payee_filter_presenter.checked_payees,
            self._payee_filter_presenter.payee_filter_mode,
        )
        filter_.set_specific_categories_filter(
            self._category_filter_presenter.checked_categories,
            self._category_filter_presenter.specific_categories_filter_mode,
        )
        filter_.set_multiple_categories_filter(
            self._category_filter_presenter.multiple_categories_filter_mode
        )
        filter_.set_currency_filter(
            self._currency_filter_presenter.checked_currencies,
            self._currency_filter_presenter.currency_filter_mode,
        )
        filter_.set_security_filter(
            self._security_filter_presenter.checked_securities,
            self._security_filter_presenter.security_filter_mode,
        )

        if self._record_keeper.base_currency is not None:
            minimum_cash_amount = CashAmount(
                self._form.cash_amount_filter_minimum, self._record_keeper.base_currency
            )
            maximum_cash_amount = CashAmount(
                self._form.cash_amount_filter_maximum, self._record_keeper.base_currency
            )
            filter_.set_cash_amount_filter(
                minimum_cash_amount,
                maximum_cash_amount,
                self._form.cash_amount_filter_mode,
            )

        return filter_

    def _update_form_from_filter(self, filter_: TransactionFilter) -> None:
        self._form.types = filter_.type_filter.types
        self._form.date_filter_mode = filter_.datetime_filter.mode
        self._form.date_filter_start = filter_.datetime_filter.start
        self._form.date_filter_end = filter_.datetime_filter.end
        self._form.description_filter_mode = filter_.description_filter.mode
        self._form.description_filter_pattern = filter_.description_filter.regex_pattern
        self._account_filter_presenter.load_from_account_filter(filter_.account_filter)
        self._tag_filter_presenter.load_from_tag_filters(
            filter_.specific_tags_filter,
            filter_.tagless_filter,
            filter_.split_tags_filter,
        )
        self._payee_filter_presenter.load_from_payee_filter(filter_.payee_filter)
        self._category_filter_presenter.load_from_category_filters(
            filter_.specific_categories_filter, filter_.multiple_categories_filter
        )
        self._currency_filter_presenter.load_from_currency_filter(
            filter_.currency_filter
        )
        self._security_filter_presenter.load_from_security_filter(
            filter_.security_filter
        )
        if filter_.cash_amount_filter is not None:
            self._form.base_currency_code = filter_.cash_amount_filter.currency.code
            self._form.cash_amount_filter_mode = filter_.cash_amount_filter.mode
            self._form.cash_amount_filter_minimum = (
                filter_.cash_amount_filter.minimum.value_rounded
            )
            self._form.cash_amount_filter_maximum = (
                filter_.cash_amount_filter.maximum.value_rounded
            )
        else:
            self._form.base_currency_code = ""

    def _restore_defaults(self) -> None:
        logging.info("Restoring TransactionFilterForm to default")
        self._update_form_from_filter(self._default_filter)

    def _setup_default_filter(self) -> None:
        self._default_filter = self._get_default_filter()

    def _get_default_filter(self) -> TransactionFilter:
        filter_ = TransactionFilter()
        filter_.set_specific_tags_filter(self._record_keeper.tags, FilterMode.KEEP)
        if self._record_keeper.base_currency is not None:
            filter_.set_cash_amount_filter(
                CashAmount(0, self._record_keeper.base_currency),
                CashAmount(0, self._record_keeper.base_currency),
                FilterMode.OFF,
            )
        return filter_

    def _log_filter_differences(  # noqa: C901, PLR0912
        self, new_filter: TransactionFilter
    ) -> None:
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
                f"tags={new_filter.specific_tags_filter.tag_names}"
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
        if old_filter.payee_filter != new_filter.payee_filter:
            logging.info(
                "PayeeFilter changed: "
                f"mode={new_filter.payee_filter.mode.name}, "
                f"payees={new_filter.payee_filter.payee_names}"
            )
        if (
            old_filter.specific_categories_filter
            != new_filter.specific_categories_filter
        ):
            logging.info(
                "SpecificCategoriesFilter changed: "
                f"mode={new_filter.specific_categories_filter.mode.name}, "
                f"category_paths={new_filter.specific_categories_filter.category_paths}"
            )
        if (
            old_filter.multiple_categories_filter
            != new_filter.multiple_categories_filter
        ):
            logging.info(
                "MultipleCategoriesFilter changed: "
                f"mode={new_filter.multiple_categories_filter.mode.name}"
            )
        if old_filter.currency_filter != new_filter.currency_filter:
            logging.info(
                "CurrencyFilter changed: "
                f"mode={new_filter.currency_filter.mode.name}, "
                f"currencies={new_filter.currency_filter.currency_codes}"
            )
        if old_filter.security_filter != new_filter.security_filter:
            logging.info(
                "SecurityFilter changed: "
                f"mode={new_filter.security_filter.mode.name}, "
                f"securities={new_filter.security_filter.security_names}"
            )
        if old_filter.cash_amount_filter != new_filter.cash_amount_filter:
            if new_filter.cash_amount_filter is None:
                logging.info("CashAmountFilter changed: mode=OFF")
            else:
                logging.info(
                    "CashAmountFilter changed: "
                    f"mode={new_filter.cash_amount_filter.mode.name}, "
                    f"min={new_filter.cash_amount_filter.minimum.to_str_rounded()}, "
                    f"max={new_filter.cash_amount_filter.maximum.to_str_rounded()}"
                )

    def _check_filter_form_sanity(self) -> None:
        types = self._form.types
        if not types:
            display_error_message(
                (
                    "No Transaction types selected in Type Filter, "
                    "all Transactions will be discarded."
                ),
                title="Warning",
            )

        if self._form.currency_filter_active:
            self._check_filter_related_types("Currency Filter", currency_related_types)
        if self._form.security_filter_active:
            self._check_filter_related_types("Security Filter", security_related_types)
        if self._form.payee_filter_active:
            self._check_filter_related_types("Payee Filter", payee_related_types)
        if self._form.category_filters_active:
            self._check_filter_related_types("Category Filter", category_related_types)

    def _check_filter_related_types(
        self,
        filter_name: str,
        related_types: set[
            type[Transaction] | CashTransactionType | SecurityTransactionType
        ],
    ) -> None:
        types = self._form.types
        field_name = filter_name.removesuffix(" Filter")
        unrelated_types = types.difference(related_types)
        if unrelated_types:
            unrelated_type_names = ", ".join(get_type_names(unrelated_types))
            question = (
                f"<html>{filter_name} has been activated but the following "
                f"Transaction types selected in the Type Filter are not {field_name} "
                "related:<br/>"
                f"<b><i>{unrelated_type_names}</i></b><br/><br/>"
                "Do you want to unselect these Transaction types in the "
                "Type Filter?</html>"
            )
            title = "Unselect unrelated Transaction types?"
            logging.info(
                f"{filter_name} activated with unrelated types, "
                "asking user to unselect them"
            )
            answer = ask_yes_no_question(self._form, question, title, warning=True)
            if answer:
                logging.info("User chose to unselect unrelated types in Type Filter")
                self._form.types = types - unrelated_types
                types = self._form.types
            else:
                logging.info("User chose to keep unrelated types in Type Filter")
        related_types = types.intersection(related_types)
        if not related_types:
            display_error_message(
                (
                    f"{filter_name} has been activated but none of the "
                    "Transaction types selected in the Type Filter are "
                    f"{field_name} related."
                ),
                title="Warning",
            )
