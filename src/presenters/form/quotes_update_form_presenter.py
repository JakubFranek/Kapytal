import logging
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QWidget
from src.models.model_objects.currency_objects import CashAmount, ExchangeRate
from src.models.model_objects.security_objects import Security
from src.models.online_quotes.functions import QuoteUpdateError, get_latest_quote
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.quotes_update_table_model import QuotesUpdateTableModel
from src.views.forms.quotes_update_form import QuotesUpdateForm
from src.views.utilities.handle_exception import display_error_message
from src.views.utilities.message_box_functions import ask_yes_no_question, show_info_box

if TYPE_CHECKING:
    from datetime import date
    from decimal import Decimal


class QuotesUpdateFormPresenter:
    event_data_changed = Event()

    def __init__(
        self,
        view: QuotesUpdateForm,
        record_keeper: RecordKeeper,
    ) -> None:
        self._view = view
        self._unsaved_quotes = False
        self._record_keeper = record_keeper
        self._quotes: dict[str, tuple[date, Decimal | CashAmount]] = {}
        self._initialize_models()
        self._connect_to_signals()
        self._update_button_states()
        self._view.finalize_setup()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

    def show_form(self, parent_widget: QWidget | None = None) -> None:
        if parent_widget is not None:
            self._view.setParent(parent_widget)
        self._view.setWindowFlag(Qt.WindowType.Window)
        self._reset_model_data()
        self._view.show_form()

    def _reset_model_data(self) -> None:
        exchange_rates = list(self._record_keeper.exchange_rates)
        securities = [
            security for security in self._record_keeper.securities if security.symbol
        ]
        items = exchange_rates + securities
        data = [(item, "", "") for item in items]
        self._unsaved_quotes = False
        self._quotes = {}
        self._model.pre_reset_model()
        self._model.load_data(data)
        self._model.post_reset_model()
        self._unselect_all()

    def _initialize_models(self) -> None:
        self._proxy = QSortFilterProxyModel()
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self._model = QuotesUpdateTableModel(self._view.table_view)
        self._view.table_view.setModel(self._proxy)
        self._model.event_checked_items_changed.append(self._update_button_states)

        self._proxy.setSourceModel(self._model)

    def _connect_to_signals(self) -> None:
        self._view.signal_save.connect(self._save_quotes)
        self._view.signal_download.connect(self._download_quotes)
        self._view.signal_select_all.connect(self._select_all)
        self._view.signal_unselect_all.connect(self._unselect_all)
        self._view.signal_exit.connect(self._close_attempted)
        self._view.signal_search_text_changed.connect(self._filter)

    def _download_quotes(self) -> None:
        logging.info("Downloading quotes...")
        checked_items = self._model.checked_items
        for item in checked_items:
            data = (item, "Fetching...", "Fetching...")
            self._model.load_single_data(data)
            if isinstance(item, ExchangeRate):
                self._download_exchange_rate_quote(item)
            elif isinstance(item, Security):
                self._download_security_quote(item)
        self._update_button_states()
        self._unsaved_quotes = True

    def _download_security_quote(self, security: Security) -> None:
        try:
            date_, price = get_latest_quote(security.symbol)
            price = CashAmount(price, security.currency)
            logging.debug(
                f"Downloaded {security.symbol} quote: "
                f"{price.to_str_normalized()} on {date_}"
            )
        except QuoteUpdateError:
            display_error_message(
                f"Download failed for Security symbol {security.symbol}.\n"
                "Please ensure the symbol is correct and your internet connection is "
                "stable."
            )
            data = (security, "Error!", "Error!")
            self._model.load_single_data(data)
            return
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        data = (
            security,
            date_.strftime(user_settings.settings.general_date_format),
            price.to_str_normalized(),
        )
        self._model.load_single_data(data)
        self._quotes[str(security)] = (date_, price)

    def _download_exchange_rate_quote(self, exchange_rate: ExchangeRate) -> None:
        exchange_rate_ticker = (
            exchange_rate.primary_currency.code
            + exchange_rate.secondary_currency.code
            + "=X"
        )
        try:
            date_, rate = get_latest_quote(exchange_rate_ticker)
            logging.debug(f"Downloaded {exchange_rate} quote: {rate} on {date_}")
        except Exception:  # noqa: BLE001
            try:
                exchange_rate_ticker = (
                    exchange_rate.primary_currency.code
                    + "-"
                    + exchange_rate.secondary_currency.code
                )
                date_, rate = get_latest_quote(exchange_rate_ticker)
            except QuoteUpdateError:
                display_error_message(
                    f"Download failed for Exchange Rate {exchange_rate}.\n"
                    "Please ensure the Currency codes are correct and your internet "
                    "connection is stable."
                )
                data = (exchange_rate, "Error!", "Error!")
                self._model.load_single_data(data)
                return
            except Exception as exception:  # noqa: BLE001
                handle_exception(exception)
                return

        data = (
            exchange_rate,
            date_.strftime(user_settings.settings.general_date_format),
            f"{rate:,}",
        )
        self._model.load_single_data(data)
        self._quotes[str(exchange_rate)] = (date_, rate)

    def _save_quotes(self) -> None:
        checked_items = self._model.checked_items
        text = "The selected quotes have been saved:\n"
        for item in checked_items:
            try:
                date_, value = self._quotes[str(item)]
                if isinstance(item, Security):
                    item.set_price(date_, value)
                    text += (
                        f"- {item.symbol}: {value} on "
                        f"{date_.strftime(user_settings.settings.general_date_format)}\n"
                    )
                else:
                    item.set_rate(date_, value)
                    text += (
                        f"- {item}: {value:,} on "
                        f"{date_.strftime(user_settings.settings.general_date_format)}\n"
                    )
            except KeyError:
                pass
        self._view.set_button_state(download=True, save=False)
        self.event_data_changed()
        logging.info("Downloaded quotes saved")
        self._unsaved_quotes = False
        show_info_box(self._view, text.strip(), "Quotes saved")
        self._view.close()

    def _select_all(self) -> None:
        self._model.load_checked_items(self._model.items)

    def _unselect_all(self) -> None:
        self._model.load_checked_items([])

    def _update_button_states(self) -> None:
        if len(self._model.checked_items) > 0:
            if all(str(item) in self._quotes for item in self._model.checked_items):
                self._view.set_button_state(download=True, save=True)
            else:
                self._view.set_button_state(download=True, save=False)
        else:
            self._view.set_button_state(download=False, save=False)

    def _close_attempted(self) -> None:
        if not self._unsaved_quotes:
            self._view.set_close_allowed(allowed=True)
            return
        if ask_yes_no_question(
            self._view,
            question=(
                "The downloaded quotes have not been saved yet.\n"
                "Do you want to close without saving?"
            ),
            title="Close without saving?",
        ):
            self._view.set_close_allowed(allowed=True)
            return
        self._view.set_close_allowed(allowed=False)

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._proxy.setFilterWildcard(pattern)
