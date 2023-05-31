import logging
from datetime import datetime
from decimal import Decimal

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.custom_exceptions import InvalidOperationError
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.currency_table_model import CurrencyTableModel
from src.view_models.exchange_rate_table_model import ExchangeRateTableModel
from src.view_models.value_table_model import ValueTableModel, ValueType
from src.views.dialogs.add_exchange_rate_dialog import AddExchangeRateDialog
from src.views.dialogs.currency_dialog import CurrencyDialog
from src.views.dialogs.set_exchange_rate_dialog import SetExchangeRateDialog
from src.views.forms.currency_form import CurrencyForm
from src.views.utilities.message_box_functions import ask_yes_no_question


class CurrencyFormPresenter:
    event_data_changed = Event()
    event_base_currency_changed = Event()

    def __init__(self, view: CurrencyForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._initialize_models()

        self._view.signal_add_currency.connect(self.run_add_currency_dialog)
        self._view.signal_set_base_currency.connect(self.set_base_currency)
        self._view.signal_remove_currency.connect(self.remove_currency)
        self._view.signal_add_exchange_rate.connect(self.run_add_exchange_rate_dialog)
        self._view.signal_remove_exchange_rate.connect(self.remove_exchange_rate)

        self._view.finalize_setup()

        self._view.signal_exchange_rate_selection_changed.connect(
            self._exchange_rate_selection_changed
        )
        self._view.signal_currency_selection_changed.connect(
            self._currency_selection_changed
        )
        self._exchange_rate_selection_changed()
        self._currency_selection_changed()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._currency_table_model.pre_reset_model()
        self._exchange_rate_table_model.pre_reset_model()
        self._record_keeper = record_keeper
        self._currency_table_model.currencies = record_keeper.currencies
        self._currency_table_model.base_currency = record_keeper.base_currency
        self._exchange_rate_table_model.exchange_rates = record_keeper.exchange_rates
        self._currency_table_model.post_reset_model()
        self._exchange_rate_table_model.post_reset_model()

    def show_form(self) -> None:
        self._view.show_form()

    def run_add_currency_dialog(self) -> None:
        self._dialog = CurrencyDialog(self._view)
        self._dialog.signal_ok.connect(self.add_currency)
        logging.debug("Running CurrencyDialog")
        self._dialog.exec()

    def add_currency(self) -> None:
        previous_base_currency = self._record_keeper.base_currency
        code = self._dialog.currency_code
        places = self._dialog.currency_places

        logging.info(f"Adding Currency: {code=}, {places=}")
        try:
            self._record_keeper.add_currency(code, places)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._currency_table_model.pre_add()
        self._currency_table_model.currencies = self._record_keeper.currencies
        self._currency_table_model.base_currency = self._record_keeper.base_currency
        self._currency_table_model.post_add()
        self._dialog.close()
        self.event_data_changed()
        if self._record_keeper.base_currency != previous_base_currency:
            self.event_base_currency_changed()

    def set_base_currency(self) -> None:
        currency = self._currency_table_model.get_selected_item()
        if currency is None:
            raise InvalidOperationError("Cannot set an unselected Currency as base.")

        logging.info(f"Setting {currency.code} as base currency")
        try:
            self._record_keeper.set_base_currency(currency.code)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._currency_table_model.currencies = self._record_keeper.currencies
        self._currency_table_model.base_currency = self._record_keeper.base_currency
        self.event_base_currency_changed()
        self.event_data_changed()
        self._view.refresh_currency_table()

    def remove_currency(self) -> None:
        previous_base_currency = self._record_keeper.base_currency
        currency = self._currency_table_model.get_selected_item()
        if currency is None:
            raise InvalidOperationError("Cannot remove an unselected Currency.")

        logging.info(f"Removing Currency: {currency.code}")
        try:
            self._record_keeper.remove_currency(currency.code)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._currency_table_model.pre_remove_item(currency)
        self._currency_table_model.currencies = self._record_keeper.currencies
        self._currency_table_model.base_currency = self._record_keeper.base_currency
        self._currency_table_model.post_remove_item()
        self.event_data_changed()
        if self._record_keeper.base_currency != previous_base_currency:
            self.event_base_currency_changed()

    def run_add_exchange_rate_dialog(self) -> None:
        codes = [currency.code for currency in self._record_keeper.currencies]
        self._dialog = AddExchangeRateDialog(currency_codes=codes, parent=self._view)
        self._dialog.signal_ok.connect(self.add_exchange_rate)
        logging.debug("Running AddExchangeRateDialog")
        self._dialog.exec()

    def add_exchange_rate(self) -> None:
        primary_code = self._dialog.primary_currency_code
        secondary_code = self._dialog.secondary_currency_code

        logging.info(f"Adding ExchangeRate: {primary_code}/{secondary_code}")
        try:
            self._record_keeper.add_exchange_rate(primary_code, secondary_code)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._exchange_rate_table_model.pre_add()
        self._exchange_rate_table_model.exchange_rates = (
            self._record_keeper.exchange_rates
        )
        self._exchange_rate_table_model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def run_set_exchange_rate_dialog(self) -> None:
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        if exchange_rate is None:
            raise ValueError("An ExchangeRate must be selected to set its value.")
        exchange_rate_code = str(exchange_rate)
        last_value = exchange_rate.latest_rate
        last_value = last_value if last_value.is_finite() else Decimal(1)
        self._dialog = SetExchangeRateDialog(
            date_today=datetime.now(user_settings.settings.time_zone).date(),
            exchange_rate=exchange_rate_code,
            last_value=last_value,
            parent=self._view,
        )
        self._dialog.signal_ok.connect(self.set_exchange_rate)
        logging.debug("Running SetExchangeRateDialog")
        self._dialog.exec()

    def set_exchange_rate(self) -> None:
        value = self._dialog.value.normalize()
        date_ = self._dialog.date_
        exchange_rate_code = self._dialog.exchange_rate_code
        logging.info(
            f"Setting ExchangeRate {exchange_rate_code}: "
            f"{value!s} on {date_.strftime('%Y-%m-%d')}"
        )
        try:
            self._record_keeper.set_exchange_rate(exchange_rate_code, value, date_)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._exchange_rate_table_model.exchange_rates = (
            self._record_keeper.exchange_rates
        )
        self._dialog.close()
        self.event_data_changed()

    def remove_exchange_rate(self) -> None:
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        if exchange_rate is None:
            raise InvalidOperationError("Cannot remove an unselected ExchangeRate.")

        logging.debug(
            "ExchangeRate deletion requested, asking the user for confirmation"
        )
        if not ask_yes_no_question(
            self._view,
            question=f"Do you want to delete the {exchange_rate!s} exchange rate?",
            title="Are you sure?",
        ):
            logging.debug("User cancelled the ExchangeRate deletion")
            return

        logging.info(f"Removing ExchangeRate: {exchange_rate!s}")
        try:
            self._record_keeper.remove_exchange_rate(str(exchange_rate))
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._exchange_rate_table_model.pre_remove_item(exchange_rate)
        self._exchange_rate_table_model.exchange_rates = (
            self._record_keeper.exchange_rates
        )
        self._exchange_rate_table_model.post_remove_item()
        self.event_data_changed()

    def _exchange_rate_selection_changed(self) -> None:
        item = self._exchange_rate_table_model.get_selected_item()
        is_exchange_rate_selected = item is not None
        self._view.set_exchange_rate_actions(
            is_exchange_rate_selected=is_exchange_rate_selected
        )

        if item is not None and self._exchange_rate_selection != item:
            self._view.set_history_group_box_title(str(item) + " history")
            self._exchange_rate_history_model.pre_reset_model()
            self._exchange_rate_history_model.load_data(item.rate_history_pairs)
            self._exchange_rate_history_model.post_reset_model()
            dates, rates = zip(*item.rate_history_pairs, strict=True)
            self._view.load_chart_data(dates, rates)

        self._exchange_rate_selection = item

    def _currency_selection_changed(self) -> None:
        item = self._currency_table_model.get_selected_item()
        is_currency_selected = item is not None
        self._view.set_currency_actions(is_currency_selected=is_currency_selected)

    def _initialize_models(self) -> None:
        self._currency_table_proxy = QSortFilterProxyModel(self._view)
        self._currency_table_model = CurrencyTableModel(
            self._view.currencyTable,
            self._currency_table_proxy,
            self._record_keeper.currencies,
            self._record_keeper.base_currency,
        )
        self._currency_table_proxy.setSourceModel(self._currency_table_model)
        self._view.currencyTable.setModel(self._currency_table_proxy)

        self._exchange_rate_table_proxy = QSortFilterProxyModel(self._view)
        self._exchange_rate_table_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._exchange_rate_table_model = ExchangeRateTableModel(
            self._view.exchangeRateTable,
            self._exchange_rate_table_proxy,
            self._record_keeper.exchange_rates,
        )
        self._exchange_rate_table_proxy.setSourceModel(self._exchange_rate_table_model)
        self._view.exchangeRateTable.setModel(self._exchange_rate_table_proxy)

        self._exchange_rate_history_proxy = QSortFilterProxyModel(self._view)
        self._exchange_rate_history_model = ValueTableModel(
            self._view.exchangeRateHistoryTable,
            self._exchange_rate_history_proxy,
            ValueType.EXCHANGE_RATE,
        )
        self._exchange_rate_history_proxy.setSourceModel(
            self._exchange_rate_history_model
        )
        self._view.exchangeRateHistoryTable.setModel(self._exchange_rate_history_proxy)
