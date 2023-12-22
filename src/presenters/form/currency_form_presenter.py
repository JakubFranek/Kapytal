import csv
import logging
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from dateutil.relativedelta import relativedelta
from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.currency_objects import ExchangeRate
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.currency_table_model import CurrencyTableModel
from src.view_models.exchange_rate_table_model import ExchangeRateTableModel
from src.view_models.value_table_model import ValueTableModel, ValueType
from src.views.dialogs.add_exchange_rate_dialog import AddExchangeRateDialog
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.dialogs.currency_dialog import CurrencyDialog
from src.views.dialogs.load_data_dialog import ConflictResolutionMode, LoadDataDialog
from src.views.dialogs.set_exchange_rate_dialog import SetExchangeRateDialog
from src.views.forms.currency_form import CurrencyForm
from src.views.utilities.handle_exception import display_error_message
from src.views.utilities.message_box_functions import ask_yes_no_question


class CurrencyFormPresenter:
    event_data_changed = Event()
    event_base_currency_changed = Event()
    event_update_quotes = Event()

    def __init__(self, view: CurrencyForm, record_keeper: RecordKeeper) -> None:
        self.view = view
        self._record_keeper = record_keeper

        self._initialize_models()

        self.view.signal_add_currency.connect(self._run_add_currency_dialog)
        self.view.signal_set_base_currency.connect(self._set_base_currency)
        self.view.signal_remove_currency.connect(self._remove_currency)
        self.view.signal_add_exchange_rate.connect(self._run_add_exchange_rate_dialog)
        self.view.signal_remove_exchange_rate.connect(self._remove_exchange_rate)
        self.view.signal_add_data.connect(self._run_add_data_point_dialog)
        self.view.signal_edit_data.connect(self._run_edit_data_point_dialog)
        self.view.signal_remove_data.connect(self._remove_data_points)
        self.view.signal_load_data.connect(self._run_load_data_dialog)

        self.view.finalize_setup()

        self.view.signal_exchange_rate_selection_changed.connect(
            self._exchange_rate_selection_changed
        )
        self.view.signal_currency_selection_changed.connect(
            self._currency_selection_changed
        )
        self.view.signal_data_point_selection_changed.connect(
            self._data_point_selection_changed
        )
        self.view.signal_data_point_double_clicked.connect(
            self._run_edit_data_point_dialog
        )
        self.view.signal_update_quotes.connect(self.event_update_quotes)

        self._exchange_rate_selection_changed()
        self._currency_selection_changed()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

        self._currency_table_model.pre_reset_model()
        self._currency_table_model.load_data(
            record_keeper.currencies, record_keeper.base_currency
        )
        self._currency_table_model.post_reset_model()

        self.reset_and_update_exchange_rate_table()

        self._exchange_rate_history_model.pre_reset_model()
        self._exchange_rate_history_model.load_data(())
        self._exchange_rate_history_model.post_reset_model()

        self._exchange_rate_selection_changed()
        self._update_chart(None)

    def data_changed(self) -> None:
        self.reset_and_update_exchange_rate_table()

    def reset_and_update_exchange_rate_table(self) -> None:
        selected_index = self.view.exchangeRateTable.currentIndex()

        self._exchange_rate_table_model.pre_reset_model()
        self.update_exchange_rate_table_data()
        self._exchange_rate_table_model.post_reset_model()

        if selected_index.isValid():
            self.view.exchangeRateTable.selectRow(selected_index.row())

    def update_exchange_rate_table_data(self) -> None:
        stats = self._calculate_exchange_rate_stats(self._record_keeper.exchange_rates)
        self._exchange_rate_table_model.load_data(
            self._record_keeper.exchange_rates, stats
        )
        self._set_exchange_rate_table_column_visibility()

    def show_form(self) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self.view, "Preparing Currencies and Exchange Rates form, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()

        if self._exchange_rate_table_model.get_selected_item() is None:
            self.view.exchangeRateTable.selectRow(0)
        self.view.show_form()
        self._busy_dialog.close()

    def _run_add_currency_dialog(self) -> None:
        self._dialog = CurrencyDialog(self.view)
        self._dialog.signal_ok.connect(self._add_currency)
        logging.debug("Running CurrencyDialog")
        self._dialog.exec()

    def _add_currency(self) -> None:
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
        self._currency_table_model.load_data(
            self._record_keeper.currencies, self._record_keeper.base_currency
        )
        self._currency_table_model.post_add()
        self._dialog.close()
        self.event_data_changed()
        if self._record_keeper.base_currency != previous_base_currency:
            self.event_base_currency_changed()

    def _set_base_currency(self) -> None:
        currency = self._currency_table_model.get_selected_item()
        if currency is None:
            raise InvalidOperationError("Cannot set an unselected Currency as base.")

        logging.info(f"Setting {currency.code} as base currency")
        try:
            self._record_keeper.set_base_currency(currency.code)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._currency_table_model.load_data(
            self._record_keeper.currencies, self._record_keeper.base_currency
        )
        self.event_base_currency_changed()
        self.event_data_changed()
        self.view.refresh_currency_table()

    def _remove_currency(self) -> None:
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
        self._currency_table_model.load_data(
            self._record_keeper.currencies, self._record_keeper.base_currency
        )
        self._currency_table_model.post_remove_item()
        self.event_data_changed()
        if self._record_keeper.base_currency != previous_base_currency:
            self.event_base_currency_changed()

    def _run_add_exchange_rate_dialog(self) -> None:
        codes = [currency.code for currency in self._record_keeper.currencies]
        if len(codes) < 2:
            display_error_message(
                "Create at least 2 Currencies before adding an Exchange Rate."
            )
            return

        self._dialog = AddExchangeRateDialog(currency_codes=codes, parent=self.view)
        self._dialog.signal_ok.connect(self._add_exchange_rate)
        logging.debug("Running AddExchangeRateDialog")
        self._dialog.exec()

    def _add_exchange_rate(self) -> None:
        primary_code = self._dialog.primary_currency_code
        secondary_code = self._dialog.secondary_currency_code

        logging.info(f"Adding ExchangeRate: {primary_code}/{secondary_code}")
        try:
            self._record_keeper.add_exchange_rate(primary_code, secondary_code)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._exchange_rate_table_model.pre_add()
        self.update_exchange_rate_table_data()
        self._exchange_rate_table_model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def _remove_exchange_rate(self) -> None:
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        if exchange_rate is None:
            raise InvalidOperationError("Cannot remove an unselected ExchangeRate.")

        logging.debug(
            "ExchangeRate deletion requested, asking the user for confirmation"
        )
        if not ask_yes_no_question(
            self.view,
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
        self.update_exchange_rate_table_data()
        self._exchange_rate_table_model.post_remove_item()
        self.event_data_changed()

    def _run_add_data_point_dialog(self) -> None:
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        if exchange_rate is None:
            raise ValueError("An ExchangeRate must be selected to set its value.")
        exchange_rate_code = str(exchange_rate)
        last_value = (
            exchange_rate.latest_rate
            if exchange_rate.latest_rate.is_finite()
            else Decimal(1)
        )

        today = datetime.now(user_settings.settings.time_zone).date()
        self._dialog = SetExchangeRateDialog(
            date_=today,
            max_date=today,
            exchange_rate=exchange_rate_code,
            value=last_value,
            parent=self.view,
            edit=False,
        )
        self._dialog.signal_ok.connect(self._set_exchange_rate)
        logging.debug("Running SetExchangeRateDialog (add data point)")
        self._dialog.exec()

    def _run_edit_data_point_dialog(self) -> None:
        selected_data_points = self._exchange_rate_history_model.get_selected_values()
        if len(selected_data_points) != 1:
            raise ValueError("Exactly one data point must be selected to edit it.")
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        if exchange_rate is None:
            raise ValueError("An ExchangeRate must be selected to edit its data point.")
        exchange_rate_code = str(exchange_rate)

        date_, value = selected_data_points[0]
        self._dialog = SetExchangeRateDialog(
            date_=date_,
            max_date=datetime.now(user_settings.settings.time_zone).date(),
            exchange_rate=exchange_rate_code,
            value=value,
            parent=self.view,
            edit=True,
        )
        self._dialog.signal_ok.connect(self._set_exchange_rate)
        logging.debug("Running SetExchangeRateDialog (edit data point)")
        self._dialog.exec()

    def _set_exchange_rate(self) -> None:
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        if exchange_rate is None:
            raise ValueError("An ExchangeRate must be selected to edit its data point.")

        value = self._dialog.value.normalize()
        date_ = self._dialog.date_
        exchange_rate_code = self._dialog.exchange_rate_code
        if self._dialog.edit:
            date_edited = self._dialog.original_date != date_
        else:
            date_edited = False

        logging.info(f"Setting ExchangeRate {exchange_rate_code}: {value!s} on {date_}")
        try:
            exchange_rate.set_rate(date_, value)
            if date_edited:
                exchange_rate.delete_rate(self._dialog.original_date)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        previous_data_points = self._exchange_rate_history_model.data_points
        new_data_points = exchange_rate.rate_history_pairs
        if date_edited:  # REFACTOR: not optimal - model reset is a dirty fix
            self._exchange_rate_history_model.pre_reset_model()
            self._exchange_rate_history_model.load_data(
                new_data_points, exchange_rate.rate_decimals
            )
            self._exchange_rate_history_model.post_reset_model()
        elif len(previous_data_points) != len(new_data_points):
            for _index, _data in enumerate(new_data_points):
                if date_ == _data[0]:
                    index = _index
                    break
            else:
                raise ValueError("No data point found for the given date.")
            self._exchange_rate_history_model.pre_add(index)
            self._exchange_rate_history_model.load_data(
                new_data_points, exchange_rate.rate_decimals
            )
            self._exchange_rate_history_model.post_add()
        else:
            self._exchange_rate_history_model.load_data(
                new_data_points, exchange_rate.rate_decimals
            )

        self._dialog.close()
        self._update_chart(exchange_rate)
        self.event_data_changed()

    def _remove_data_points(self) -> None:
        selected_data_points = self._exchange_rate_history_model.get_selected_values()
        if len(selected_data_points) == 0:
            raise InvalidOperationError(
                "At least one Exchange Range data point must be selected for removal."
            )
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        if exchange_rate is None:
            raise InvalidOperationError(
                "An ExchangeRate must be selected to edit its data point."
            )

        logging.debug(
            f"{exchange_rate!s} Exchange Rate data point deletion requested, "
            "asking the user for confirmation"
        )
        if not ask_yes_no_question(
            self.view,
            question=(
                f"Do you want to delete {len(selected_data_points):,} data point(s) "
                f"for {exchange_rate!s} exchange rate?"
            ),
            title="Are you sure?",
        ):
            logging.debug("User cancelled the data point deletion")
            return

        try:
            any_deleted = False
            for date_, _ in selected_data_points:
                exchange_rate.delete_rate(date_)
                any_deleted = True
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        if any_deleted:
            self._reset_model_and_update_chart(exchange_rate)
            self._data_point_selection_changed()
            self.event_data_changed()

    def _run_load_data_dialog(self) -> None:
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        if exchange_rate is None:
            raise InvalidOperationError(
                "An ExchangeRate must be selected to load data points."
            )
        self._dialog = LoadDataDialog(self.view, str(exchange_rate))
        self._dialog.signal_ok.connect(self._load_data)
        logging.info(f"Running LoadDataDialog: {exchange_rate!s}")
        self._dialog.exec()

    def _load_data(self) -> None:
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        if exchange_rate is None:
            raise InvalidOperationError(
                "An ExchangeRate must be selected to load data points."
            )

        _path = self._dialog.path
        conflict_resolution_mode = self._dialog.conflict_resolution_mode
        path = Path(_path)

        logging.debug(f"Loading {exchange_rate!s} data from {path!s}")
        data: list[tuple[date, Decimal]] = []
        try:
            with path.open("r") as file:
                reader = csv.reader(file)
                for _date, _value in reader:
                    date_ = datetime.strptime(_date, "%Y-%m-%d").date()  # noqa: DTZ007
                    value = Decimal(_value)
                    data.append((date_, value))
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        logging.debug(f"Loaded {len(data):,} data points for {exchange_rate!s}")

        if conflict_resolution_mode == ConflictResolutionMode.OVERWRITE:
            filtered_data = data
        else:
            filtered_data = [
                (date_, value)
                for date_, value in data
                if date_ not in exchange_rate.rate_history
            ]

        try:
            exchange_rate.set_rates(filtered_data)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        logging.debug(
            f"Set {len(filtered_data):,} data points to {exchange_rate!s} "
            f"(conflict_resolution_mode={conflict_resolution_mode.name})"
        )

        self._reset_model_and_update_chart(exchange_rate)
        self._dialog.close()
        self.event_data_changed()

    def _exchange_rate_selection_changed(self) -> None:
        item = self._exchange_rate_table_model.get_selected_item()
        is_exchange_rate_selected = item is not None
        self.view.set_exchange_rate_actions(
            is_exchange_rate_selected=is_exchange_rate_selected
        )

        if item is not None and self._exchange_rate_selection != item:
            self.view.set_history_group_box_title(str(item) + " history")
            self._reset_model_and_update_chart(item)

        self._exchange_rate_selection = item
        self._data_point_selection_changed()

    def _currency_selection_changed(self) -> None:
        item = self._currency_table_model.get_selected_item()
        is_currency_selected = item is not None
        self.view.set_currency_actions(is_currency_selected=is_currency_selected)

    def _data_point_selection_changed(self) -> None:
        exchange_rate = self._exchange_rate_table_model.get_selected_item()
        is_exchange_rate_selected = exchange_rate is not None
        data_points = self._exchange_rate_history_model.get_selected_values()
        is_data_point_selected = len(data_points) > 0
        is_single_data_point_selected = len(data_points) == 1
        self.view.set_data_point_actions(
            is_exchange_rate_selected=is_exchange_rate_selected,
            is_data_point_selected=is_data_point_selected,
            is_single_data_point_selected=is_single_data_point_selected,
        )

    def _reset_model_and_update_chart(self, exchange_rate: ExchangeRate) -> None:
        if not self._busy_dialog.isVisible():
            self._busy_chart_dialog = create_simple_busy_indicator(
                self.view, "Updating Exchange Rate chart, please wait..."
            )
            self._busy_chart_dialog.open()
            QApplication.processEvents()

        self._exchange_rate_history_model.pre_reset_model()
        self._exchange_rate_history_model.load_data(
            exchange_rate.rate_history_pairs, exchange_rate.rate_decimals
        )
        self._exchange_rate_history_model.post_reset_model()
        self._update_chart(exchange_rate)

        if not self._busy_dialog.isVisible():
            self._busy_chart_dialog.close()

    def _update_chart(self, exchange_rate: ExchangeRate | None) -> None:
        if exchange_rate is None or len(exchange_rate.rate_history_pairs) == 0:
            self.view.load_chart_data((), (), "", 0)
            return
        dates, rates = zip(*exchange_rate.rate_history_pairs, strict=True)
        self.view.load_chart_data(
            dates, rates, str(exchange_rate), exchange_rate.rate_decimals
        )

    def _initialize_models(self) -> None:
        self._currency_table_proxy = QSortFilterProxyModel(self.view)
        self._currency_table_model = CurrencyTableModel(
            self.view.currencyTable,
            self._currency_table_proxy,
        )
        self._currency_table_proxy.setSourceModel(self._currency_table_model)
        self.view.currencyTable.setModel(self._currency_table_proxy)

        self._exchange_rate_table_proxy = QSortFilterProxyModel(self.view)
        self._exchange_rate_table_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._exchange_rate_table_model = ExchangeRateTableModel(
            self.view.exchangeRateTable,
            self._exchange_rate_table_proxy,
        )
        self._exchange_rate_table_proxy.setSourceModel(self._exchange_rate_table_model)
        self.view.exchangeRateTable.setModel(self._exchange_rate_table_proxy)

        self._exchange_rate_history_proxy = QSortFilterProxyModel(self.view)
        self._exchange_rate_history_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._exchange_rate_history_model = ValueTableModel(
            self.view.exchangeRateHistoryTable,
            self._exchange_rate_history_proxy,
            ValueType.EXCHANGE_RATE,
        )
        self._exchange_rate_history_proxy.setSourceModel(
            self._exchange_rate_history_model
        )
        self.view.exchangeRateHistoryTable.setModel(self._exchange_rate_history_proxy)

    def _set_exchange_rate_table_column_visibility(self) -> None:
        for column in range(self._exchange_rate_table_model.columnCount()):
            column_empty = (
                self._exchange_rate_table_model.is_column_empty(column)
                and len(self._record_keeper.exchange_rates) != 0  # show all when empty
            )
            self.view.exchangeRateTable.setColumnHidden(column, column_empty)

    def _calculate_exchange_rate_stats(
        self, exchange_rates: list[ExchangeRate]
    ) -> dict[ExchangeRate, dict[str, Decimal]]:
        today = datetime.now(user_settings.settings.time_zone).date()
        periods = {
            "1D": (today - relativedelta(days=1), today),
            "7D": (today - relativedelta(days=7), today),
            "1M": (today - relativedelta(months=1), today),
            "3M": (today - relativedelta(months=3), today),
            "6M": (today - relativedelta(months=6), today),
            "1Y": (today - relativedelta(years=1), today),
            "2Y": (today - relativedelta(years=2), today),
            "3Y": (today - relativedelta(years=3), today),
            "5Y": (today - relativedelta(years=5), today),
            "7Y": (today - relativedelta(years=7), today),
            "10Y": (today - relativedelta(years=10), today),
            "YTD": (today.replace(month=1, day=1), today),
            "Total": (None, today),
        }

        returns = {
            exchange_rate: {
                period: exchange_rate.calculate_return(start, end)
                for period, (start, end) in periods.items()
            }
            for exchange_rate in exchange_rates
        }

        # add annualized Total period to returns
        for exchange_rate in exchange_rates:
            try:
                return_total = returns[exchange_rate]["Total"] / 100
                days = (exchange_rate.latest_date - exchange_rate.earliest_date).days
                if days == 0:
                    returns[exchange_rate]["Total p.a."] = Decimal(0)
                    continue
                exponent = Decimal(365) / Decimal(days)
                returns[exchange_rate]["Total p.a."] = 100 * (
                    ((1 + return_total) ** exponent) - 1
                )
            except TypeError:
                returns[exchange_rate]["Total p.a."] = Decimal("NaN")

        return returns
