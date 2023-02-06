import logging
from datetime import datetime

from src.models.constants import tzinfo
from src.models.record_keeper import RecordKeeper
from src.presenters.utilities.event import Event
from src.presenters.view_models.currency_table_model import CurrencyTableModel
from src.presenters.view_models.exchange_rate_table_model import ExchangeRateTableModel
from src.utilities.general import get_exception_display_info
from src.views.dialogs.add_exchange_rate_dialog import AddExchangeRateDialog
from src.views.dialogs.currency_dialog import CurrencyDialog
from src.views.dialogs.set_exchange_rate_dialog import SetExchangeRateDialog
from src.views.forms.currency_form import CurrencyForm
from src.views.utilities.handle_exception import display_error_message


class CurrencyFormPresenter:
    event_data_changed = Event()
    event_base_currency_changed = Event()

    def __init__(self, view: CurrencyForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._currency_table_model = CurrencyTableModel(
            self._view.currencyTable,
            record_keeper.currencies,
            record_keeper.base_currency,
        )
        self._view.currencyTable.setModel(self._currency_table_model)

        self._exchange_rate_table_model = ExchangeRateTableModel(
            self._view.exchangeRateTable, record_keeper.exchange_rates
        )
        self._view.exchangeRateTable.setModel(self._exchange_rate_table_model)

        self._view.signal_add_currency.connect(self.run_add_currency_dialog)
        self._view.signal_set_base_currency.connect(self.set_base_currency)
        self._view.signal_remove_currency.connect(self.remove_currency)
        self._view.signal_add_exchange_rate.connect(self.run_add_exchange_rate_dialog)
        self._view.signal_set_exchange_rate.connect(self.run_set_exchange_rate_dialog)
        self._view.signal_remove_exchange_rate.connect(self.remove_exchange_rate)

        self._view.exchangeRateTable.selectionModel().selectionChanged.connect(
            self._exchange_rate_selection_changed
        )
        self._view.currencyTable.selectionModel().selectionChanged.connect(
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
        self._dialog.signal_OK.connect(self.add_currency)
        logging.debug("Running CurrencyDialog")
        self._dialog.exec()

    def add_currency(self) -> None:
        previous_base_currency = self._record_keeper.base_currency
        code = self._dialog.currency_code
        places = self._dialog.currency_places

        logging.info(f"Adding Currency(code='{code}', places='{places}')")
        try:
            self._record_keeper.add_currency(code, places)
        except Exception:
            self._handle_exception()
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
            return

        logging.info(f"Setting {currency} as base currency")
        try:
            self._record_keeper.set_base_currency(currency.code)
        except Exception:
            self._handle_exception()
            return

        self._currency_table_model.currencies = self._record_keeper.currencies
        self._currency_table_model.base_currency = self._record_keeper.base_currency
        self.event_base_currency_changed()
        self.event_data_changed()
        self._view.currencyTable.viewport().update()

    def remove_currency(self) -> None:
        previous_base_currency = self._record_keeper.base_currency
        currency = self._currency_table_model.get_selected_item()
        if currency is None:
            return

        logging.info(f"Removing {currency}")
        try:
            self._record_keeper.remove_currency(currency.code)
        except Exception:
            self._handle_exception()
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
        self._dialog.signal_OK.connect(self.add_exchange_rate)
        logging.debug("Running AddExchangeRateDialog")
        self._dialog.exec()

    def add_exchange_rate(self) -> None:
        primary_code = self._dialog.primary_currency_code
        secondary_code = self._dialog.secondary_currency_code

        logging.info(f"Adding ExchangeRate({primary_code}/{secondary_code})")
        try:
            self._record_keeper.add_exchange_rate(primary_code, secondary_code)
        except Exception:
            self._handle_exception()
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
        self._dialog = SetExchangeRateDialog(
            date_today=datetime.now(tzinfo).date(),
            exchange_rate=exchange_rate_code,
            last_value=last_value,
            parent=self._view,
        )
        self._dialog.signal_OK.connect(self.set_exchange_rate)
        logging.debug("Running SetExchangeRateDialog")
        self._dialog.exec()

    def set_exchange_rate(self) -> None:
        value = self._dialog.value
        date_ = self._dialog.date_
        exchange_rate_code = self._dialog.exchange_rate_code
        logging.info(f"Setting ExchangeRate({exchange_rate_code}): {value} on {date_}")
        try:
            self._record_keeper.set_exchange_rate(exchange_rate_code, value, date_)
        except Exception:
            self._handle_exception()
            return

        self._exchange_rate_table_model.exchange_rates = (
            self._record_keeper.exchange_rates
        )
        self._dialog.close()
        self.event_data_changed()

    def remove_exchange_rate(self) -> None:
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        if exchange_rate is None:
            return

        logging.info(f"Removing {repr(exchange_rate)}")
        try:
            self._record_keeper.remove_exchange_rate(str(exchange_rate))
        except Exception:
            self._handle_exception()
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
        self._view.setExchangeRateButton.setEnabled(is_exchange_rate_selected)

    def _currency_selection_changed(self) -> None:
        item = self._currency_table_model.get_selected_item()
        is_currency_selected = item is not None
        self._view.setBaseCurrencyButton.setEnabled(is_currency_selected)
        self._view.removeCurrencyButton.setEnabled(is_currency_selected)

    def _handle_exception(self) -> None:
        display_text, display_details = get_exception_display_info()  # type: ignore
        display_error_message(display_text, display_details)
