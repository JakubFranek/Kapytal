import csv
import logging
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from dateutil.relativedelta import relativedelta
from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.currency_objects import CashAmount
from src.models.model_objects.security_objects import Security, SecurityAccount
from src.models.record_keeper import RecordKeeper
from src.models.statistics.security_stats import calculate_irr
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.owned_securities_tree_model import OwnedSecuritiesTreeModel
from src.view_models.security_table_model import SecurityTableModel
from src.view_models.value_table_model import ValueTableModel, ValueType
from src.views.constants import OwnedSecuritiesTreeColumn
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.dialogs.load_data_dialog import ConflictResolutionMode, LoadDataDialog
from src.views.dialogs.security_dialog import SecurityDialog
from src.views.dialogs.set_security_price_dialog import SetSecurityPriceDialog
from src.views.forms.security_form import SecurityForm
from src.views.utilities.message_box_functions import ask_yes_no_question


class SecurityFormPresenter:
    event_data_changed = Event()
    event_update_quotes = Event()

    def __init__(self, view: SecurityForm, record_keeper: RecordKeeper) -> None:
        self.view = view
        self._record_keeper = record_keeper

        self.reset_self = True  # if True, models can be reset via data_changed

        self.view.signal_update_quotes.connect(self.event_update_quotes)

        self._initialize_table_models()
        self._initialize_tree_models()

        self._connect_to_signals()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self.reset_models()
        self._security_selection_changed()

    def reset_models(self) -> None:
        self._security_table_model.pre_reset_model()
        self.update_security_model_data()
        self._security_table_model.post_reset_model()

        self.reset_overview_model_data()

        self._price_table_model.pre_reset_model()
        self.update_price_model_data()
        self._price_table_model.post_reset_model()

        self._update_chart(None)

    def update_security_model_data(self) -> None:
        returns = self._calculate_security_returns(self._record_keeper.securities)
        self._security_table_model.load_securities(
            self._record_keeper.securities, returns
        )
        self._set_security_table_column_visibility()

    def reset_overview_model_data(self) -> None:
        # REFACTOR: resetting model for every update is necessary because the model
        # cannot synchronize id's during model updates
        self._overview_tree_model.pre_reset_model()
        self.update_overview_model_data()
        self._overview_tree_model.post_reset_model()

    def update_overview_model_data(self) -> None:
        irrs = self._calculate_irrs()
        self._overview_tree_model.load_data(
            self._record_keeper.security_accounts,
            irrs,
            self._record_keeper.base_currency,
        )
        hide_native_column = all(
            security.currency == self._record_keeper.base_currency
            for security in self._record_keeper.securities
        )
        self.view.treeView.setColumnHidden(
            OwnedSecuritiesTreeColumn.AMOUNT_NATIVE, hide_native_column
        )
        self.view.treeView.setColumnHidden(
            OwnedSecuritiesTreeColumn.GAIN_NATIVE, hide_native_column
        )

    def update_price_model_data(self) -> None:
        self._price_table_model.load_data(())

    def data_changed(self) -> None:
        # skip this if data_changed is triggered by self via event chain
        if not self.reset_self:
            return

        self.view.securityTableView.viewport().update()  # forces redraw
        self.update_security_model_data()

        self._overview_tree_model.pre_reset_model()
        self.update_overview_model_data()
        self._overview_tree_model.post_reset_model()

        security = self._security_table_model.get_selected_item()
        if security is None:
            return
        self._price_table_model.pre_reset_model()
        self._price_table_model.load_data(
            security.decimal_price_history_pairs, security.price_decimals
        )
        self._price_table_model.set_unit(security.currency.code)
        self._price_table_model.post_reset_model()
        self._update_chart(security)

    def show_form(self) -> None:
        self._busy_form_dialog = create_simple_busy_indicator(
            self.view, "Preparing Securities form, please wait..."
        )
        self._busy_form_dialog.open()
        QApplication.processEvents()

        if (
            self._security_table_model.get_selected_item() is None
            and self._security_table_model.rowCount() > 0
        ):
            self.view.securityTableView.selectRow(0)

        self.view.refresh_tree_view()
        self.view.treeView.sortByColumn(
            OwnedSecuritiesTreeColumn.AMOUNT_BASE, Qt.SortOrder.DescendingOrder
        )
        self.view.show_form()
        self._busy_form_dialog.close()

    def _run_security_dialog(self, *, edit: bool) -> None:
        security_types = {security.type_ for security in self._record_keeper.securities}
        currency_codes = [currency.code for currency in self._record_keeper.currencies]
        self._dialog = SecurityDialog(
            parent=self.view,
            security_types=security_types,
            currency_codes=currency_codes,
            edit=edit,
        )
        if edit:
            security = self._security_table_model.get_selected_item()
            if security is None:
                raise ValueError("Cannot edit an unselected item.")
            self._dialog.signal_ok.connect(self._edit_security)
            self._dialog.name = security.name
            self._dialog.symbol = security.symbol
            self._dialog.type_ = security.type_
            self._dialog.currency_code = security.currency.code
            self._dialog.decimals = security.shares_decimals
        else:
            self._dialog.signal_ok.connect(self._add_security)
        logging.debug(f"Running SecurityDialog ({edit=})")
        self._dialog.exec()

    def _add_security(self) -> None:
        name = self._dialog.name
        symbol = self._dialog.symbol
        type_ = self._dialog.type_
        currency_code = self._dialog.currency_code
        shares_decimals = self._dialog.decimals

        logging.info(
            f"Adding Security: {name=}, {symbol=}, type={type_}, "
            f"currency={currency_code}, shares_decimals={shares_decimals!s}"
        )
        try:
            self._record_keeper.add_security(
                name=name,
                symbol=symbol,
                type_=type_,
                currency_code=currency_code,
                shares_decimals=shares_decimals,
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._security_table_model.pre_add()
        self.update_security_model_data()
        self._security_table_model.post_add()
        self._security_selection_changed()
        self._dialog.close()
        self.reset_self = False
        self.event_data_changed()
        self.reset_self = True

    def _edit_security(self) -> None:
        security = self._security_table_model.get_selected_item()
        if security is None:
            raise ValueError("Cannot edit an unselected item.")

        uuid = security.uuid
        name = self._dialog.name
        symbol = self._dialog.symbol
        type_ = self._dialog.type_

        logging.info(
            f"Editing Security name='{security.name}', symbol='{security.symbol}', "
            f"type='{security.type_}': new {name=}, new {symbol=}, new type={type_}"
        )
        try:
            self._record_keeper.edit_security(
                uuid_=uuid, name=name, symbol=symbol, type_=type_
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self.update_security_model_data()
        self._dialog.close()
        self.reset_self = False
        self.event_data_changed()
        self.reset_self = True

    def _remove_security(self) -> None:
        security = self._security_table_model.get_selected_item()
        if security is None:
            return

        uuid = security.uuid

        logging.debug("Security deletion requested, asking the user for confirmation")
        if not ask_yes_no_question(
            self.view,
            f"Do you want to remove {security.name}?",
            "Are you sure?",
        ):
            logging.debug("User cancelled the Security deletion")
            return

        logging.info(f"Removing {security}")
        try:
            self._record_keeper.remove_security(uuid)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._security_table_model.pre_remove_item(security)
        self.update_security_model_data()
        self._security_table_model.post_remove_item()
        self.reset_self = False
        self.event_data_changed()
        self.reset_self = True

    def _run_add_price_dialog(self) -> None:
        security = self._security_table_model.get_selected_item()
        if security is None:
            raise ValueError("A Security must be selected to set its price.")

        last_value = security.price.value_normalized
        if last_value.is_nan():
            last_value = Decimal(0)
        today = datetime.now(user_settings.settings.time_zone).date()

        self._dialog = SetSecurityPriceDialog(
            date_=today,
            max_date=today,
            value=last_value,
            security_name=security.name,
            parent=self.view,
            currency_code=security.currency.code,
            edit=False,
        )
        self._dialog.signal_ok.connect(self._set_price)
        logging.debug("Running SetSecurityPriceDialog (add data point)")
        self._dialog.exec()

    def _run_edit_price_dialog(self) -> None:
        selected_data_points = self._price_table_model.get_selected_values()
        if len(selected_data_points) != 1:
            raise ValueError("Exactly one data point must be selected to edit it.")
        security = self._security_table_model.get_selected_item()
        if security is None:
            raise ValueError("A Security must be selected to set its price.")

        date_, value = selected_data_points[0]

        self._dialog = SetSecurityPriceDialog(
            date_=date_,
            max_date=datetime.now(user_settings.settings.time_zone).date(),
            value=value,
            security_name=security.name,
            parent=self.view,
            currency_code=security.currency.code,
            edit=True,
        )
        self._dialog.signal_ok.connect(self._set_price)
        logging.debug("Running SetSecurityPriceDialog (add data point)")
        self._dialog.exec()

    def _set_price(self) -> None:
        security = self._security_table_model.get_selected_item()
        if security is None:
            raise ValueError("A Security must be selected to set its price.")

        value = self._dialog.value.normalize()
        date_ = self._dialog.date_
        if self._dialog.edit:
            date_edited = self._dialog.original_date != date_
        else:
            date_edited = False

        logging.info(
            f"Setting {security} price: {value} on {date_.strftime('%Y-%m-%d')}"
        )
        try:
            security.set_price(date_, CashAmount(value, security.currency))
            if date_edited:
                security.delete_price(self._dialog.original_date)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        previous_data_points = self._price_table_model.data_points
        new_data_points = security.decimal_price_history_pairs
        if date_edited:  # REFACTOR: not optimal - model reset is a dirty fix
            self._price_table_model.pre_reset_model()
            self._price_table_model.load_data(new_data_points, security.price_decimals)
            self._price_table_model.set_unit(security.currency.code)
            self._price_table_model.post_reset_model()
        elif len(previous_data_points) != len(new_data_points):
            for _index, _data in enumerate(new_data_points):
                if date_ == _data[0]:
                    index = _index
                    break
            else:
                raise ValueError("No data point found for the given date.")
            self._price_table_model.pre_add(index)
            self._price_table_model.load_data(new_data_points, security.price_decimals)
            self._price_table_model.set_unit(security.currency.code)
            self._price_table_model.post_add()
        else:
            self._price_table_model.load_data(new_data_points, security.price_decimals)

        self._dialog.close()
        self._update_chart(security)
        self.update_security_model_data()
        self.reset_overview_model_data()
        self.reset_self = False
        self.event_data_changed()
        self.reset_self = True

    def _remove_prices(self) -> None:
        selected_data_points = self._price_table_model.get_selected_values()
        if len(selected_data_points) == 0:
            raise InvalidOperationError(
                "At least one data point must be selected for removal."
            )
        security = self._security_table_model.get_selected_item()
        if security is None:
            raise InvalidOperationError(
                "An ExchangeRate must be selected to edit its data point."
            )

        logging.debug(
            f"{security!s} price deletion requested, asking the user for confirmation"
        )
        if not ask_yes_no_question(
            self.view,
            question=(
                f"Do you want to delete {len(selected_data_points):,} data point(s) "
                f"of {security.name}?"
            ),
            title="Are you sure?",
        ):
            logging.debug("User cancelled the data point deletion")
            return

        try:
            any_deleted = False
            for date_, _ in selected_data_points:
                security.delete_price(date_)
                any_deleted = True
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        if any_deleted:
            self._update_price_table_and_chart(security)
            self._price_selection_changed()
            self.update_security_model_data()
            self.reset_overview_model_data()
            self.reset_self = False
            self.event_data_changed()
            self.reset_self = True

    def _run_load_data_dialog(self) -> None:
        security = self._security_table_model.get_selected_item()
        if security is None:
            raise InvalidOperationError(
                "A Security must be selected to load data points."
            )
        self._dialog = LoadDataDialog(self.view, security.name)
        self._dialog.signal_ok.connect(self._load_data)
        logging.info(f"Running LoadDataDialog: {security.name}")
        self._dialog.exec()

    def _load_data(self) -> None:
        security = self._security_table_model.get_selected_item()
        if security is None:
            raise InvalidOperationError(
                "A Security must be selected to load data points."
            )

        _path = self._dialog.path
        conflict_resolution_mode = self._dialog.conflict_resolution_mode
        path = Path(_path)

        logging.debug(f"Loading {security!s} data from {path!s}")
        data: list[tuple[date, CashAmount]] = []
        try:
            with path.open("r") as file:
                reader = csv.reader(file)
                for _date, _value in reader:
                    date_ = datetime.strptime(_date, "%Y-%m-%d").date()  # noqa: DTZ007
                    value = CashAmount(_value, security.currency)
                    data.append((date_, value))
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        logging.debug(f"Loaded {len(data):,} data points for {security!s}")

        if conflict_resolution_mode == ConflictResolutionMode.OVERWRITE:
            filtered_data = data
        else:
            filtered_data = [
                (date_, value)
                for date_, value in data
                if date_ not in security.price_history
            ]

        try:
            security.set_prices(filtered_data)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        logging.debug(
            f"Set {len(filtered_data):,} data points to {security.name} "
            f"(conflict_resolution_mode={conflict_resolution_mode.name})"
        )

        self._update_price_table_and_chart(security)
        self.update_security_model_data()
        self.reset_overview_model_data()
        self._dialog.close()
        self.reset_self = False
        self.event_data_changed()
        self.reset_self = True

    def _initialize_table_models(self) -> None:
        self._security_table_proxy = QSortFilterProxyModel(self.view.securityTableView)
        self._security_table_model = SecurityTableModel(
            self.view.securityTableView,
            self._security_table_proxy,
        )
        self._security_table_proxy.setSourceModel(self._security_table_model)
        self._security_table_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._security_table_proxy.setSortCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        self._security_table_proxy.setFilterCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive
        )
        self._security_table_proxy.setFilterKeyColumn(-1)
        self.view.securityTableView.setModel(self._security_table_proxy)

        self._price_table_proxy = QSortFilterProxyModel(
            self.view.securityPriceTableView
        )
        self._price_table_model = ValueTableModel(
            self.view.securityPriceTableView,
            self._price_table_proxy,
            ValueType.SECURITY_PRICE,
        )
        self._price_table_proxy.setSourceModel(self._price_table_model)
        self._price_table_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self.view.securityPriceTableView.setModel(self._price_table_proxy)

    def _initialize_tree_models(self) -> None:
        self._tree_proxy = QSortFilterProxyModel(self.view.treeView)
        self._overview_tree_model = OwnedSecuritiesTreeModel(
            self.view.treeView,
            self._tree_proxy,
        )
        self._tree_proxy.setSourceModel(self._overview_tree_model)
        self._tree_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._tree_proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._tree_proxy.setRecursiveFilteringEnabled(True)  # noqa: FBT003
        self._tree_proxy.sort(
            OwnedSecuritiesTreeColumn.AMOUNT_BASE, Qt.SortOrder.DescendingOrder
        )
        self._tree_proxy.setFilterKeyColumn(-1)
        self._tree_proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.view.treeView.setModel(self._tree_proxy)

    def _connect_to_signals(self) -> None:
        self.view.signal_add_security.connect(
            lambda: self._run_security_dialog(edit=False)
        )
        self.view.signal_remove_security.connect(self._remove_security)
        self.view.signal_edit_security.connect(
            lambda: self._run_security_dialog(edit=True)
        )
        self.view.signal_add_price.connect(self._run_add_price_dialog)
        self.view.signal_edit_price.connect(self._run_edit_price_dialog)
        self.view.signal_remove_prices.connect(self._remove_prices)
        self.view.signal_load_price_data.connect(self._run_load_data_dialog)

        self.view.signal_manage_search_text_changed.connect(self._filter_table)
        self.view.signal_overview_search_text_changed.connect(self._filter_tree)

        self.view.finalize_setup()
        self.view.signal_security_selection_changed.connect(
            self._security_selection_changed
        )
        self.view.signal_price_selection_changed.connect(self._price_selection_changed)
        self._security_selection_changed()
        self.view.signal_security_table_double_clicked.connect(
            lambda: self._run_security_dialog(edit=True)
        )
        self.view.signal_price_table_double_clicked.connect(self._run_edit_price_dialog)

    def _filter_table(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._security_table_proxy.setFilterWildcard(pattern)

    def _filter_tree(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._tree_proxy.setFilterWildcard(pattern)
        self.view.treeView.expandAll()

    def _security_selection_changed(self) -> None:
        security = self._security_table_model.get_selected_item()
        is_security_selected = security is not None
        self.view.enable_security_table_actions(
            is_security_selected=is_security_selected
        )

        if security is not None and self._security_selection != security:
            self._update_price_table_and_chart(security)

        self._security_selection = security
        self._price_selection_changed()

    def _price_selection_changed(self) -> None:
        security = self._security_table_model.get_selected_item()
        is_security_selected = security is not None
        data_points = self._price_table_model.get_selected_values()
        is_price_selected = len(data_points) > 0
        is_single_price_selected = len(data_points) == 1
        self.view.set_price_actions(
            is_security_selected=is_security_selected,
            is_price_selected=is_price_selected,
            is_single_price_selected=is_single_price_selected,
        )

    def _update_price_table_and_chart(self, security: Security) -> None:
        if not self._busy_form_dialog.isVisible():
            self._busy_chart_dialog = create_simple_busy_indicator(
                self.view, "Updating Security price chart, please wait..."
            )
            self._busy_chart_dialog.open()
            QApplication.processEvents()

        self._price_table_model.pre_reset_model()
        self._price_table_model.load_data(
            security.decimal_price_history_pairs, security.price_decimals
        )
        self._price_table_model.set_unit(security.currency.code)
        self._price_table_model.post_reset_model()
        self._update_chart(security)

        if not self._busy_form_dialog.isVisible():
            self._busy_chart_dialog.close()

    def _update_chart(self, security: Security | None) -> None:
        if security is None or len(security.decimal_price_history_pairs) == 0:
            self.view.load_chart_data((), (), "", "", "", 0)
            return
        dates, rates = zip(*security.decimal_price_history_pairs, strict=True)
        self.view.load_chart_data(
            dates,
            rates,
            security.name,
            f"Price [{security.currency.code}]",
            security.currency.code,
            security.price_decimals,
        )

    def _calculate_security_returns(
        self, securities: list[Security]
    ) -> dict[Security, dict[str, Decimal]]:
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
            "Total": (None, today),
        }

        returns = {
            security: {
                period: security.calculate_return(start, end)
                for period, (start, end) in periods.items()
            }
            for security in securities
        }

        # add annualized Total period to returns
        for security in securities:
            return_total = returns[security]["Total"] / 100
            days = (security.latest_date - security.earliest_date).days
            if days == 0:
                returns[security]["Total p.a."] = Decimal(0)
                continue
            exponent = Decimal(365) / Decimal(days)
            returns[security]["Total p.a."] = 100 * (
                ((1 + return_total) ** exponent) - 1
            )

        return returns

    def _set_security_table_column_visibility(self) -> None:
        for column in range(self._security_table_model.columnCount()):
            column_empty = self._security_table_model.is_column_empty(column)
            self.view.securityTableView.setColumnHidden(column, column_empty)

    def _calculate_irrs(self) -> dict[Security, dict[SecurityAccount | None, Decimal]]:
        irrs: dict[Security, dict[SecurityAccount | None, Decimal]] = {}
        for security in self._record_keeper.securities:
            accounts = [
                account
                for account in self._record_keeper.security_accounts
                if account.is_security_related(security)
            ]
            irrs[security] = {None: calculate_irr(security, accounts)}
            for account in accounts:
                irrs[security][account] = calculate_irr(security, [account])

        return irrs
