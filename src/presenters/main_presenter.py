import json
import logging

from PyQt6.QtWidgets import QApplication

from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.record_keeper import RecordKeeper
from src.presenters.account_tree_presenter import AccountTreePresenter
from src.presenters.currency_form_presenter import CurrencyFormPresenter
from src.presenters.payee_form_presenter import PayeeFormPresenter
from src.presenters.security_form_presenter import SecurityFormPresenter
from src.presenters.tag_form_presenter import TagFormPresenter
from src.utilities.general import backup_json_file, get_exception_display_info
from src.views.forms.currency_form import CurrencyForm
from src.views.forms.payee_form import PayeeForm
from src.views.forms.security_form import SecurityForm
from src.views.forms.tag_form import TagForm
from src.views.main_view import MainView
from src.views.utilities.handle_exception import display_error_message


class MainPresenter:
    def __init__(
        self,
        view: MainView,
        record_keeper: RecordKeeper,
        app: QApplication,
        app_root_directory: str,
    ) -> None:
        self._view = view
        self._record_keeper = record_keeper
        self._app = app

        # Presenter initialization
        logging.debug("Creating AccountTreePresenter")
        self._account_tree_presenter = AccountTreePresenter(
            view.account_tree, record_keeper
        )
        logging.debug("Creating Currency Form and CurrencyFormPresenter")
        currency_form = CurrencyForm(parent=view)
        self._currency_form_presenter = CurrencyFormPresenter(
            currency_form, record_keeper
        )
        logging.debug("Creating PayeeForm and PayeeFormPresenter")
        payee_form = PayeeForm(parent=view)
        self._payee_form_presenter = PayeeFormPresenter(payee_form, record_keeper)
        logging.debug("Creating TagForm and TagFormPresenter")
        tag_form = TagForm(parent=view)
        self._tag_form_presenter = TagFormPresenter(tag_form, record_keeper)
        logging.debug("Creating SecurityForm and SecurityFormPresenter")
        security_form = SecurityForm(parent=view)
        self._security_form_presenter = SecurityFormPresenter(
            security_form, record_keeper
        )

        # Setting up Event observers
        self._account_tree_presenter.event_data_changed.append(
            lambda: self._update_unsaved_changes(True)
        )
        self._currency_form_presenter.event_base_currency_changed.append(
            self._account_tree_presenter.update_model_data
        )
        self._currency_form_presenter.event_data_changed.append(
            lambda: self._update_unsaved_changes(True)
        )
        self._payee_form_presenter.event_data_changed.append(
            lambda: self._update_unsaved_changes(True)
        )
        self._tag_form_presenter.event_data_changed.append(
            lambda: self._update_unsaved_changes(True)
        )
        self._security_form_presenter.event_data_changed.append(
            lambda: self._update_unsaved_changes(True)
        )

        # MainView pyqtSignal connections
        self._view.signal_exit.connect(self._quit)
        self._view.signal_open_currency_form.connect(
            self._currency_form_presenter.show_form
        )
        self._view.signal_open_payee_form.connect(self._payee_form_presenter.show_form)
        self._view.signal_open_tag_form.connect(self._tag_form_presenter.show_form)
        self._view.signal_open_security_form.connect(
            self._security_form_presenter.show_form
        )
        self._view.signal_save.connect(lambda: self._save_to_file(save_as=False))
        self._view.signal_save_as.connect(lambda: self._save_to_file(save_as=True))
        self._view.signal_open.connect(self._load_from_file)

        # File path initialization
        self.current_file_path: str | None = None
        self.backup_directories: list[str] = [
            app_root_directory + "/saved_data/backups/"
        ]
        self._update_unsaved_changes(False)

        logging.debug("Showing MainView")
        self._view.show()

    def _save_to_file(self, save_as: bool) -> None:
        logging.info("Save to file initiated")
        try:
            if save_as is True or self.current_file_path is None:
                logging.debug("Asking the user for destination path")
                file_path = self._view.get_save_path()
                if file_path != "":
                    self.current_file_path = file_path

            if not isinstance(self.current_file_path, str):
                logging.info("Invalid or no file path received, file save cancelled")
                return

            with open(self.current_file_path, mode="w", encoding="UTF-8") as file:
                logging.debug(f"Saving to file: {self.current_file_path}")
                json.dump(self._record_keeper, file, cls=CustomJSONEncoder)
                self._update_unsaved_changes(False)
                self._view.statusBar().showMessage(
                    f"File saved: {self.current_file_path}", 3000
                )
                logging.info(f"File saved: {self.current_file_path}")
        except Exception:
            self._handle_exception()

    def _load_from_file(self) -> None:
        logging.info("Load from file initiated")
        try:
            file_path = self._view.get_open_path()
            if file_path == "":
                logging.info("Invalid or no file path received, file load cancelled")
                return

            self.current_file_path = file_path
            with open(file_path, mode="r", encoding="UTF-8") as file:
                logging.debug(f"File path received: {file_path}")
                backup_json_file(file_path, self.backup_directories)
                logging.debug(f"Loading file: {file_path}")
                logging.disable(logging.INFO)
                record_keeper: RecordKeeper = json.load(file, cls=CustomJSONDecoder)
                logging.disable(logging.NOTSET)
                self._record_keeper = record_keeper
                self._account_tree_presenter.load_record_keeper(record_keeper)
                self._currency_form_presenter.load_record_keeper(record_keeper)
                self._payee_form_presenter.load_record_keeper(record_keeper)
                self._tag_form_presenter.load_record_keeper(record_keeper)
                self._security_form_presenter.load_record_keeper(record_keeper)
                self._view.statusBar().showMessage(
                    f"File loaded: {self.current_file_path}", 3000
                )
                self._update_unsaved_changes(False)
                logging.debug(f"Currencies: {len(record_keeper.currencies)}")
                logging.debug(f"Exchange Rates: {len(record_keeper.exchange_rates)}")
                logging.debug(f"Securities: {len(record_keeper.securities)}")
                logging.debug(f"AccountGroups: {len(record_keeper.account_groups)}")
                logging.debug(f"Accounts: {len(record_keeper.accounts)}")
                logging.debug(f"Transactions: {len(record_keeper.transactions)}")
                logging.debug(f"Categories: {len(record_keeper.categories)}")
                logging.debug(f"Tags: {len(record_keeper.tags)}")
                logging.debug(f"Payees: {len(record_keeper.tags)}")
                logging.info(f"File loaded: {file_path}")
        except Exception:
            self._handle_exception()

    def _quit(self) -> None:
        if self._unsaved_changes is True:
            logging.info(
                "Quit called with unsaved changes, asking the user for instructions"
            )
            reply = self._view.ask_save_before_quit()
            if reply is True:
                self._save_to_file(save_as=False)
                if self._unsaved_changes is False:
                    logging.info("Quitting after saving")
                    self._app.quit()
                else:
                    logging.info("Quit cancelled")
                    return
            elif reply is False:
                logging.info("Quit without saving")
                self._app.quit()
            else:
                logging.info("Quit cancelled")
                return
        else:
            logging.info("Quitting")
            self._app.quit()

    def _update_unsaved_changes(self, unsaved_changes: bool) -> None:
        self._unsaved_changes = unsaved_changes
        self._view.set_save_status(self.current_file_path, self._unsaved_changes)

    def _handle_exception(self) -> None:
        display_text, display_details = get_exception_display_info()  # type: ignore
        display_error_message(display_text, display_details)
