import csv
import logging
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.currency_objects import CashAmount
from src.models.model_objects.security_objects import Security
from src.models.record_keeper import RecordKeeper
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

    def __init__(self, view: SecurityForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._initialize_table_models()
        self._initialize_tree_models()

        self._view.signal_add_security.connect(
            lambda: self._run_security_dialog(edit=False)
        )
        self._view.signal_remove_security.connect(self._remove_security)
        self._view.signal_edit_security.connect(
            lambda: self._run_security_dialog(edit=True)
        )
        self._view.signal_add_price.connect(self._run_add_price_dialog)
        self._view.signal_edit_price.connect(self._run_edit_price_dialog)
        self._view.signal_remove_prices.connect(self._remove_prices)
        self._view.signal_load_price_data.connect(self._run_load_data_dialog)

        self._view.signal_manage_search_text_changed.connect(self._filter_table)
        self._view.signal_overview_search_text_changed.connect(self._filter_tree)

        self._view.finalize_setup()
        self._view.signal_security_selection_changed.connect(
            self._security_selection_changed
        )
        self._view.signal_price_selection_changed.connect(self._price_selection_changed)
        self._security_selection_changed()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self.reset_models()

    def reset_models(self) -> None:
        self._security_table_model.pre_reset_model()
        self._tree_model.pre_reset_model()
        self._price_table_model.pre_reset_model()
        self.update_model_data()
        self._security_table_model.post_reset_model()
        self._tree_model.post_reset_model()
        self._price_table_model.post_reset_model()

        self._update_chart(None)

    def update_model_data(self) -> None:
        self._security_table_model.load_securities(self._record_keeper.securities)
        self._tree_model.load_data(
            self._record_keeper.security_accounts,
            self._record_keeper.base_currency,
        )
        self._price_table_model.load_data(())

    def show_form(self) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self._view, "Preparing Securities form, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()

        if self._security_table_model.get_selected_item() is None:
            self._view.securityTableView.selectRow(0)
        self._view.refresh_tree_view()
        self._view.treeView.sortByColumn(
            OwnedSecuritiesTreeColumn.AMOUNT_BASE, Qt.SortOrder.DescendingOrder
        )
        self._view.show_form()
        self._busy_dialog.close()

    def _run_security_dialog(self, *, edit: bool) -> None:
        security_types = {security.type_ for security in self._record_keeper.securities}
        currency_codes = [currency.code for currency in self._record_keeper.currencies]
        self._dialog = SecurityDialog(
            parent=self._view,
            security_types=security_types,
            currency_codes=currency_codes,
            edit=edit,
        )
        self._dialog.unit = Decimal(1)
        if edit:
            security = self._security_table_model.get_selected_item()
            if security is None:
                raise ValueError("Cannot edit an unselected item.")
            self._dialog.signal_ok.connect(self._edit_security)
            self._dialog.name = security.name
            self._dialog.symbol = security.symbol
            self._dialog.type_ = security.type_
        else:
            self._dialog.signal_ok.connect(self._add_security)
        logging.debug(f"Running SecurityDialog ({edit=})")
        self._dialog.exec()

    def _add_security(self) -> None:
        name = self._dialog.name
        symbol = self._dialog.symbol
        type_ = self._dialog.type_
        currency_code = self._dialog.currency_code
        unit = self._dialog.unit

        logging.info(
            f"Adding Security: {name=}, {symbol=}, type={type_}, "
            f"currency={currency_code}, unit={unit!s}"
        )
        try:
            self._record_keeper.add_security(
                name=name,
                symbol=symbol,
                type_=type_,
                currency_code=currency_code,
                unit=unit,
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._security_table_model.pre_add()
        self.update_model_data()
        self._security_table_model.post_add()
        self._dialog.close()
        self.event_data_changed()

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

        self.update_model_data()
        self._dialog.close()
        self.event_data_changed()

    def _remove_security(self) -> None:
        security = self._security_table_model.get_selected_item()
        if security is None:
            return

        uuid = security.uuid

        logging.debug("Security deletion requested, asking the user for confirmation")
        if not ask_yes_no_question(
            self._view,
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
        self.update_model_data()
        self._security_table_model.post_remove_item()
        self.event_data_changed()

    def _run_add_price_dialog(self) -> None:
        security = self._security_table_model.get_selected_item()
        if security is None:
            raise ValueError("A Security must be selected to set its price.")

        last_value = security.price.value_normalized
        self._dialog = SetSecurityPriceDialog(
            date_=datetime.now(user_settings.settings.time_zone).date(),
            value=last_value,
            security_name=security.name,
            parent=self._view,
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
            value=value,
            security_name=security.name,
            parent=self._view,
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
        logging.info(
            f"Setting {security} price: {value} on {date_.strftime('%Y-%m-%d')}"
        )
        try:
            security.set_price(date_, CashAmount(value, security.currency))
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        previous_data_points = self._price_table_model.data_points
        new_data_points = security.decimal_price_history_pairs
        if len(previous_data_points) != len(new_data_points):
            for _index, _data in enumerate(new_data_points):
                if date_ == _data[0]:
                    index = _index
                    break
            else:
                raise ValueError("No data point found for the given date.")
            add = True
        else:
            add = False
            index = None

        if add:
            self._price_table_model.pre_add(index)
            self._price_table_model.load_data(new_data_points)
            self._price_table_model.post_add()
        else:
            self._price_table_model.load_data(new_data_points)

        self._dialog.close()
        self._update_chart(security)
        self.event_data_changed()

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
            self._view,
            question=(
                f"Do you want to delete {len(selected_data_points):,} data point(s) "
                f"of {security.name}?"
            ),
            title="Are you sure?",
        ):
            logging.debug("User cancelled the data point deletion")
            return

        any_deleted = False
        for date_, _ in selected_data_points:
            try:
                security.delete_price(date_)
                any_deleted = True
            except Exception as exception:  # noqa: BLE001
                handle_exception(exception)
                return

        if any_deleted:
            self._reset_model_and_update_chart(security)
            self.event_data_changed()

    def _run_load_data_dialog(self) -> None:
        security = self._security_table_model.get_selected_item()
        if security is None:
            raise InvalidOperationError(
                "A Security must be selected to load data points."
            )
        self._dialog = LoadDataDialog(self._view, security.name)
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

        self._reset_model_and_update_chart(security)
        self._dialog.close()
        self.event_data_changed()

    def _initialize_table_models(self) -> None:
        self._security_table_proxy = QSortFilterProxyModel(self._view.securityTableView)
        self._security_table_model = SecurityTableModel(
            self._view.securityTableView,
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
        self._view.securityTableView.setModel(self._security_table_proxy)

        self._price_table_proxy = QSortFilterProxyModel(
            self._view.securityPriceTableView
        )
        self._price_table_model = ValueTableModel(
            self._view.securityPriceTableView,
            self._price_table_proxy,
            ValueType.SECURITY_PRICE,
        )
        self._price_table_proxy.setSourceModel(self._price_table_model)
        self._price_table_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._view.securityPriceTableView.setModel(self._price_table_proxy)

    def _initialize_tree_models(self) -> None:
        self._tree_proxy = QSortFilterProxyModel(self._view.treeView)
        self._tree_model = OwnedSecuritiesTreeModel(
            self._view.treeView,
            self._tree_proxy,
        )
        self._tree_proxy.setSourceModel(self._tree_model)
        self._tree_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._tree_proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._tree_proxy.setRecursiveFilteringEnabled(True)  # noqa: FBT003
        self._tree_proxy.sort(
            OwnedSecuritiesTreeColumn.AMOUNT_BASE, Qt.SortOrder.DescendingOrder
        )
        self._tree_proxy.setFilterKeyColumn(-1)
        self._tree_proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._view.treeView.setModel(self._tree_proxy)

    def _filter_table(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._security_table_proxy.setFilterWildcard(pattern)

    def _filter_tree(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._tree_proxy.setFilterWildcard(pattern)
        self._view.treeView.expandAll()

    def _security_selection_changed(self) -> None:
        security = self._security_table_model.get_selected_item()
        is_security_selected = security is not None
        self._view.enable_security_table_actions(
            is_security_selected=is_security_selected
        )

        if security is not None and self._security_selection != security:
            self._reset_model_and_update_chart(security)

        self._security_selection = security
        self._price_selection_changed()

    def _price_selection_changed(self) -> None:
        security = self._security_table_model.get_selected_item()
        is_security_selected = security is not None
        data_points = self._price_table_model.get_selected_values()
        is_price_selected = len(data_points) > 0
        is_single_price_selected = len(data_points) == 1
        self._view.set_price_actions(
            is_security_selected=is_security_selected,
            is_price_selected=is_price_selected,
            is_single_price_selected=is_single_price_selected,
        )

    def _reset_model_and_update_chart(self, security: Security) -> None:
        if not self._busy_dialog.isVisible():
            self._busy_chart_dialog = create_simple_busy_indicator(
                self._view, "Updating Security price chart, please wait..."
            )
            self._busy_chart_dialog.open()
            QApplication.processEvents()

        self._price_table_model.pre_reset_model()
        self._price_table_model.load_data(security.decimal_price_history_pairs)
        self._price_table_model.post_reset_model()
        self._update_chart(security)

        if not self._busy_dialog.isVisible():
            self._busy_chart_dialog.close()

    def _update_chart(self, security: Security | None) -> None:
        if security is None or len(security.decimal_price_history_pairs) == 0:
            self._view.load_chart_data((), (), "", "")
            return
        dates, rates = zip(*security.decimal_price_history_pairs, strict=True)
        self._view.load_chart_data(
            dates, rates, security.name, f"Price ({security.currency.code})"
        )
