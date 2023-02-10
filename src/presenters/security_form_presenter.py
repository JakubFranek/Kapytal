import logging
from datetime import datetime

from PyQt6.QtCore import QSortFilterProxyModel, Qt

from src.models.constants import tzinfo
from src.models.record_keeper import RecordKeeper
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.presenters.view_models.security_table_model import SecurityTableModel
from src.views.dialogs.security_dialog import SecurityDialog
from src.views.dialogs.set_security_price_dialog import SetSecurityPriceDialog
from src.views.forms.security_form import SecurityForm


class SecurityFormPresenter:
    event_data_changed = Event()

    def __init__(self, view: SecurityForm, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        self._proxy_model = QSortFilterProxyModel(self._view.tableView)
        self._model = SecurityTableModel(self._view.tableView, [], self._proxy_model)
        self.update_model_data()
        self._proxy_model.setSourceModel(self._model)
        self._proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy_model.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy_model.setFilterKeyColumn(-1)
        self._view.tableView.setModel(self._proxy_model)

        self._view.signal_add_security.connect(
            lambda: self.run_security_dialog(edit=False)
        )
        self._view.signal_remove_security.connect(self.remove_security)
        self._view.signal_edit_security.connect(
            lambda: self.run_security_dialog(edit=True)
        )
        self._view.signal_select_security.connect(self.select_security)
        self._view.signal_set_security_price.connect(self.run_set_price_dialog)
        self._view.signal_search_text_changed.connect(self._filter)

        self._view.finalize_setup()
        self._view.signal_selection_changed.connect(self._selection_changed)
        self._selection_changed()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._model.pre_reset_model()
        self._record_keeper = record_keeper
        self.update_model_data()
        self._model.post_reset_model()

    def update_model_data(self) -> None:
        self._model.securities = self._record_keeper.securities

    def show_form(self) -> None:
        self.update_model_data()
        self._view.selectButton.setVisible(False)
        self._view.show_form()

    def run_security_dialog(self, edit: bool) -> None:
        currency_codes = [currency.code for currency in self._record_keeper.currencies]
        self._dialog = SecurityDialog(self._view, currency_codes, edit)
        if edit:
            security = self._model.get_selected_item()
            if security is None:
                raise ValueError("Cannot edit an unselected item.")
            self._dialog.signal_OK.connect(self.edit_security)
            self._dialog.name = security.name
            self._dialog.symbol = security.symbol
            self._dialog.type_ = security.type_
        else:
            self._dialog.signal_OK.connect(self.add_security)
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
        except Exception:
            handle_exception()
            return

        self._model.pre_add()
        self.update_model_data()
        self._model.post_add()
        self._dialog.close()
        self.event_data_changed()

    def edit_security(self) -> None:
        security = self._model.get_selected_item()
        if security is None:
            raise ValueError("Cannot edit an unselected item.")

        uuid = str(security.uuid)
        name = self._dialog.name
        symbol = self._dialog.symbol
        type_ = self._dialog.type_

        logging.info(f"Editing Security '{security.name}'")
        try:
            self._record_keeper.edit_security(
                uuid=uuid, name=name, symbol=symbol, type_=type_
            )
        except Exception:
            handle_exception()
            return

        self.update_model_data()
        self._dialog.close()
        self.event_data_changed()

    def remove_security(self) -> None:
        security = self._model.get_selected_item()
        if security is None:
            return

        uuid = str(security.uuid)

        logging.info(f"Removing {security}")
        try:
            self._record_keeper.remove_security(uuid)
        except Exception:
            handle_exception()
            return

        self._model.pre_remove_item(security)
        self.update_model_data()
        self._model.post_remove_item()
        self.event_data_changed()

    def run_set_price_dialog(self) -> None:
        security = self._model.get_selected_item()
        if security is None:
            raise ValueError("A Security must be selected to set its price.")

        last_value = security.price.value_normalized
        self._dialog = SetSecurityPriceDialog(
            date_today=datetime.now(tzinfo).date(),
            last_value=last_value,
            parent=self._view,
        )
        self._dialog.signal_OK.connect(self.set_price)
        logging.debug("Running SetSecurityPriceDialog")
        self._dialog.exec()

    def set_price(self) -> None:
        security = self._model.get_selected_item()
        if security is None:
            raise ValueError("A Security must be selected to set its price.")

        uuid = str(security.uuid)
        value = self._dialog.value.normalize()
        date_ = self._dialog.date_
        logging.info(f"Setting {security} price: {value} on {date_}")
        try:
            self._record_keeper.set_security_price(uuid, value, date_)
        except Exception:
            handle_exception()
            return

        self.update_model_data()
        self._dialog.close()
        self.event_data_changed()

    def select_security(self) -> None:
        pass

    def _filter(self) -> None:
        pattern = self._view.search_bar_text
        logging.debug(f"Filtering Securities: {pattern=}")
        self._proxy_model.setFilterWildcard(pattern)

    def _selection_changed(self) -> None:
        item = self._model.get_selected_item()
        is_security_selected = item is not None
        self._view.set_buttons(is_security_selected)
