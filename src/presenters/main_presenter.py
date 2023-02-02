import json
import logging

from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.record_keeper import RecordKeeper
from src.presenters.account_tree_presenter import AccountTreePresenter
from src.presenters.currency_form_presenter import CurrencyFormPresenter
from src.utilities.general import get_exception_display_info
from src.views.currency_form import CurrencyForm
from src.views.main_view import MainView
from src.views.utilities.handle_exception import display_error_message


class MainPresenter:
    def __init__(self, view: MainView, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._record_keeper = record_keeper

        # Presenter initialization
        logging.info("Creating AccountTreePresenter")
        self._account_tree_presenter = AccountTreePresenter(
            view.account_tree, record_keeper
        )
        logging.info("Creating CurrencyFormPresenter")
        currency_form = CurrencyForm(parent=view)
        self._currency_form_presenter = CurrencyFormPresenter(
            currency_form, record_keeper
        )

        # Setting up Event observers
        self._account_tree_presenter.event_data_changed.append(
            lambda: self._update_unsaved_changes(True)
        )
        self._currency_form_presenter.event_data_changed.append(
            lambda: self._update_unsaved_changes(True)
        )

        # View pyqtSignal connections
        self._view.signal_open_currency_form.connect(
            self._currency_form_presenter.show_form
        )
        self._view.signal_save.connect(lambda: self._save_to_file(save_as=False))
        self._view.signal_save_as.connect(lambda: self._save_to_file(save_as=True))
        self._view.signal_open.connect(self._load_from_file)

        self.current_file_path: str | None = None
        self._update_unsaved_changes(False)

        logging.info("Showing MainView")
        self._view.show()

    def _save_to_file(self, save_as: bool) -> None:
        logging.info("Saving to JSON file...")
        try:
            if save_as is True or self.current_file_path is None:
                file_path = self._view.get_save_path()
                if file_path != "":
                    self.current_file_path = file_path

            if isinstance(self.current_file_path, str):
                with open(self.current_file_path, mode="w", encoding="UTF-8") as file:
                    json.dump(self._record_keeper, file, cls=CustomJSONEncoder)
                    self._update_unsaved_changes(False)
                    self._view.statusBar().showMessage(
                        f"File saved ({self.current_file_path})", 2000
                    )
                    logging.info(f"File saved to {self.current_file_path}")
            else:
                logging.info("Invalid or no file path received, file saving cancelled")
        except Exception:
            self._handle_exception()

    def _load_from_file(self) -> None:
        logging.info("Loading from JSON file...")
        try:
            file_path = self._view.get_open_path()
            if file_path != "":
                self.current_file_path = file_path
                with open(file_path, mode="r", encoding="UTF-8") as file:
                    record_keeper = json.load(file, cls=CustomJSONDecoder)
                    self._record_keeper = record_keeper
                    self._account_tree_presenter.load_record_keeper(record_keeper)
                    self._currency_form_presenter.load_record_keeper(record_keeper)
                    self._view.statusBar().showMessage(
                        f"File loaded ({self.current_file_path})", 2000
                    )
                    self._update_unsaved_changes(False)
                    logging.info(f"JSON file loaded from {file_path}")
            else:
                logging.info("Invalid or no file path received, file load cancelled")
        except Exception:
            self._handle_exception()

    def _update_unsaved_changes(self, unsaved_changes: bool) -> None:
        self._unsaved_changes = unsaved_changes
        self._view.set_save_status(self.current_file_path, self._unsaved_changes)

    def _handle_exception(self) -> None:
        display_text, display_details = get_exception_display_info()  # type: ignore
        display_error_message(display_text, display_details)
