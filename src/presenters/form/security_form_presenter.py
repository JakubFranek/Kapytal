import logging
from datetime import datetime

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.owned_securities_tree_model import OwnedSecuritiesTreeModel
from src.view_models.security_table_model import SecurityTableModel
from src.views.constants import OwnedSecuritiesTreeColumn
from src.views.dialogs.security_dialog import SecurityDialog
from src.views.dialogs.set_security_price_dialog import SetSecurityPriceDialog
from src.views.forms.security_form import SecurityForm
from src.views.utilities.message_box_functions import ask_yes_no_question

# BUG: occasional silent crash on security price set (with large precision)


class SecurityFormPresenter:
    event_data_changed = Event()

    def __init__(self, view: SecurityForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._initialize_table_models()
        self._initialize_tree_models()

        self._view.signal_add_security.connect(
            lambda: self.run_security_dialog(edit=False)
        )
        self._view.signal_remove_security.connect(self.remove_security)
        self._view.signal_edit_security.connect(
            lambda: self.run_security_dialog(edit=True)
        )
        self._view.signal_set_security_price.connect(self.run_set_price_dialog)
        self._view.signal_search_text_changed.connect(self._filter)

        self._view.finalize_setup()
        self._view.signal_selection_changed.connect(self._selection_changed)
        self._selection_changed()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self.reset_models()

    def reset_models(self) -> None:
        self._table_model.pre_reset_model()
        self._tree_model.pre_reset_model()
        self.update_model_data()
        self._table_model.post_reset_model()
        self._tree_model.post_reset_model()

    def update_model_data(self) -> None:
        self._table_model.securities = self._record_keeper.securities
        self._tree_model.load_security_accounts(
            self._record_keeper.security_accounts,
            self._record_keeper.base_currency,
        )

    def show_form(self) -> None:
        self.reset_models()
        self._view.refresh_tree_view()
        self._view.treeView.sortByColumn(
            OwnedSecuritiesTreeColumn.AMOUNT_BASE, Qt.SortOrder.DescendingOrder
        )
        self._view.show_form()

    def run_security_dialog(self, *, edit: bool) -> None:
        security_types = {security.type_ for security in self._record_keeper.securities}
        currency_codes = [currency.code for currency in self._record_keeper.currencies]
        self._dialog = SecurityDialog(
            parent=self._view,
            security_types=security_types,
            currency_codes=currency_codes,
            edit=edit,
        )
        if edit:
            security = self._table_model.get_selected_item()
            if security is None:
                raise ValueError("Cannot edit an unselected item.")
            self._dialog.signal_ok.connect(self.edit_security)
            self._dialog.name = security.name
            self._dialog.symbol = security.symbol
            self._dialog.type_ = security.type_
        else:
            self._dialog.signal_ok.connect(self.add_security)
        logging.debug(f"Running SecurityDialog ({edit=})")
        self._dialog.exec()

    def add_security(self) -> None:
        name = self._dialog.name
        symbol = self._dialog.symbol
        type_ = self._dialog.type_
        currency_code = self._dialog.currency_code
        unit = self._dialog.unit

        logging.info("Adding Security")
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

        self._table_model.pre_add()
        self.update_model_data()
        self._table_model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def edit_security(self) -> None:
        security = self._table_model.get_selected_item()
        if security is None:
            raise ValueError("Cannot edit an unselected item.")

        uuid = security.uuid
        name = self._dialog.name
        symbol = self._dialog.symbol
        type_ = self._dialog.type_

        logging.info(f"Editing Security '{security.name}'")
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

    def remove_security(self) -> None:
        security = self._table_model.get_selected_item()
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

        self._table_model.pre_remove_item(security)
        self.update_model_data()
        self._table_model.post_remove_item()
        self.event_data_changed()

    def run_set_price_dialog(self) -> None:
        security = self._table_model.get_selected_item()
        if security is None:
            raise ValueError("A Security must be selected to set its price.")

        last_value = security.price.value_normalized
        self._dialog = SetSecurityPriceDialog(
            date_today=datetime.now(user_settings.settings.time_zone).date(),
            last_value=last_value,
            parent=self._view,
            currency_code=security.currency.code,
        )
        self._dialog.signal_ok.connect(self.set_price)
        logging.debug("Running SetSecurityPriceDialog")
        self._dialog.exec()

    def set_price(self) -> None:
        security = self._table_model.get_selected_item()
        if security is None:
            raise ValueError("A Security must be selected to set its price.")

        uuid = security.uuid
        value = self._dialog.value.normalize()
        date_ = self._dialog.date_
        logging.info(f"Setting {security} price: {value} on {date_}")
        try:
            self._record_keeper.set_security_price(uuid, value, date_)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self.update_model_data()
        self._dialog.close()
        self.event_data_changed()

    def _initialize_table_models(self) -> None:
        self._table_proxy = QSortFilterProxyModel(self._view.tableView)
        self._table_model = SecurityTableModel(
            self._view.tableView, self._record_keeper.securities, self._table_proxy
        )
        self._table_proxy.setSourceModel(self._table_model)
        self._table_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._table_proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._table_proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._table_proxy.setFilterKeyColumn(-1)
        self._view.tableView.setModel(self._table_proxy)

    def _initialize_tree_models(self) -> None:
        self._tree_proxy = QSortFilterProxyModel(self._view.treeView)
        self._tree_model = OwnedSecuritiesTreeModel(
            self._view.treeView,
            self._record_keeper.security_accounts,
            self._record_keeper.base_currency,
            self._tree_proxy,
        )
        self._tree_proxy.setSourceModel(self._tree_model)
        self._tree_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._tree_proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._tree_proxy.setRecursiveFilteringEnabled(True)  # noqa: FBT003
        self._tree_proxy.sort(
            OwnedSecuritiesTreeColumn.AMOUNT_BASE, Qt.SortOrder.DescendingOrder
        )
        self._view.treeView.setModel(self._tree_proxy)

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        logging.debug(f"Filtering Securities: {pattern=}")
        self._table_proxy.setFilterWildcard(pattern)

    def _selection_changed(self) -> None:
        item = self._table_model.get_selected_item()
        is_security_selected = item is not None
        self._view.enable_actions(is_security_selected=is_security_selected)