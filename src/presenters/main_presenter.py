import json
import logging
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.record_keeper import RecordKeeper
from src.presenters.form.category_form_presenter import CategoryFormPresenter
from src.presenters.form.currency_form_presenter import CurrencyFormPresenter
from src.presenters.form.payee_form_presenter import PayeeFormPresenter
from src.presenters.form.security_form_presenter import SecurityFormPresenter
from src.presenters.form.settings_form_presenter import SettingsFormPresenter
from src.presenters.form.tag_form_presenter import TagFormPresenter
from src.presenters.utilities.handle_exception import handle_exception
from src.presenters.widget.account_tree_presenter import AccountTreePresenter
from src.presenters.widget.transactions_presenter import (
    TransactionsPresenter,
)
from src.utilities import constants
from src.utilities.general import backup_json_file
from src.views.forms.category_form import CategoryForm
from src.views.forms.currency_form import CurrencyForm
from src.views.forms.payee_form import PayeeForm
from src.views.forms.security_form import SecurityForm
from src.views.forms.settings_form import SettingsForm
from src.views.forms.tag_form import TagForm
from src.views.main_view import MainView


class MainPresenter:
    def __init__(self, view: MainView, app: QApplication) -> None:
        self._view = view
        self._record_keeper = RecordKeeper()
        self._app = app

        self._initialize_presenters()
        self._setup_event_observers()
        self._connect_view_signals()
        self._initialize_recent_paths()

        # File path initialization
        self._current_file_path: Path | None = None
        self._update_unsaved_changes(unsaved_changes=False)

        logging.debug("Showing MainView")
        self._view.show()

    def _save_to_file(self, *, save_as: bool) -> None:
        logging.debug("Save to file initiated")
        try:
            if save_as is True or self._current_file_path is None:
                logging.debug("Asking the user for destination path")
                file_path = self._view.get_save_path()
                if not file_path:
                    logging.info(
                        "Save to file cancelled: invalid or no file path received"
                    )
                    return
                self._current_file_path = Path(file_path)

            with self._current_file_path.open(mode="w", encoding="UTF-8") as file:
                logging.debug(f"Saving to file: {self._current_file_path}")
                json.dump(self._record_keeper, file, cls=CustomJSONEncoder)

                self._update_unsaved_changes(unsaved_changes=False)
                self._view.show_status_message(
                    f"File saved: {self._current_file_path}", 3000
                )

                logging.info(f"File saved: {self._current_file_path}")
            backup_json_file(self._current_file_path)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)

    def _load_from_file(self, path: str | Path | None = None) -> None:
        logging.debug("Load from file initiated")
        if self._check_for_unsaved_changes("Load File") is False:
            return
        try:
            if path is None:
                logging.debug("Asking user for file path")
                path = self._view.get_open_path()
                if not path:
                    logging.info(
                        "Load from file cancelled: invalid or no file path received"
                    )
                    return

            logging.debug(f"File path: {path}")
            self._current_file_path = Path(path)
            self._open_file(self._current_file_path)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)

    def _open_file(self, path: Path) -> None:
        with path.open(mode="r", encoding="UTF-8") as file:
            backup_json_file(self._current_file_path)

            logging.debug(f"Loading file: {self._current_file_path}")
            logging.disable(logging.INFO)  # suppress logging of object creation
            record_keeper: RecordKeeper = json.load(file, cls=CustomJSONDecoder)
            logging.disable(logging.NOTSET)  # enable logging again

            self._load_record_keeper(record_keeper)

            self._view.show_status_message(
                f"File loaded: {self._current_file_path}", 3000
            )
            self._update_unsaved_changes(unsaved_changes=False)

            self._add_recent_path(self._current_file_path)

            logging.debug(f"Currencies: {len(record_keeper.currencies)}")
            logging.debug(f"Exchange Rates: {len(record_keeper.exchange_rates)}")
            logging.debug(f"Securities: {len(record_keeper.securities)}")
            logging.debug(f"AccountGroups: {len(record_keeper.account_groups)}")
            logging.debug(f"Accounts: {len(record_keeper.accounts)}")
            logging.debug(f"Transactions: {len(record_keeper.transactions)}")
            logging.debug(f"Categories: {len(record_keeper.categories)}")
            logging.debug(f"Tags: {len(record_keeper.tags)}")
            logging.debug(f"Payees: {len(record_keeper.tags)}")
            logging.info(f"File loaded: {path}")

    def _close_file(self) -> None:
        if self._check_for_unsaved_changes("Close File") is False:
            return
        logging.info("Closing File, resetting to clean state")
        self._record_keeper = RecordKeeper()
        self._load_record_keeper(self._record_keeper)
        self._current_file_path = None
        self._update_unsaved_changes(unsaved_changes=False)

    def _quit(self) -> None:
        if self._check_for_unsaved_changes("Quit") is False:
            return
        logging.info("Qutting")
        self._app.quit()

    def _check_for_unsaved_changes(self, operation: str) -> bool:
        """True: proceed \n False: abort"""

        if not self._unsaved_changes:
            return True

        logging.info(
            f"Operation '{operation}' called with unsaved changes, asking the "
            "user for instructions"
        )
        reply = self._view.ask_save_before_close()
        if reply is True:
            self._save_to_file(save_as=False)
            if not self._unsaved_changes:
                logging.info(f"Saved, proceeding with '{operation}'")
                return True
            logging.info(f"Save cancelled, aborting operation '{operation}'")
            return False
        if reply is False:
            logging.info(f"Save rejected, proceeding with operation '{operation}'")
            return True
        logging.info(f"Operation '{operation}' cancelled")
        return False

    def _update_unsaved_changes(self, *, unsaved_changes: bool) -> None:
        self._unsaved_changes = unsaved_changes
        self._view.set_save_status(
            self._current_file_path, unsaved=self._unsaved_changes
        )

    def _load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper
        self._transactions_presenter.load_record_keeper(record_keeper)
        self._account_tree_presenter.load_record_keeper(record_keeper)

        self._currency_form_presenter.load_record_keeper(record_keeper)
        self._payee_form_presenter.load_record_keeper(record_keeper)
        self._tag_form_presenter.load_record_keeper(record_keeper)
        self._security_form_presenter.load_record_keeper(record_keeper)
        self._category_form_presenter.load_record_keeper(record_keeper)

    def _initialize_presenters(self) -> None:
        self._account_tree_presenter = AccountTreePresenter(
            self._view.account_tree_widget, self._record_keeper
        )
        self._transactions_presenter = TransactionsPresenter(
            self._view.transaction_table_widget, self._record_keeper
        )
        currency_form = CurrencyForm(parent=self._view)
        self._currency_form_presenter = CurrencyFormPresenter(
            currency_form, self._record_keeper
        )
        security_form = SecurityForm(parent=self._view)
        self._security_form_presenter = SecurityFormPresenter(
            security_form, self._record_keeper
        )
        payee_form = PayeeForm(parent=self._view)
        self._payee_form_presenter = PayeeFormPresenter(payee_form, self._record_keeper)
        tag_form = TagForm(parent=self._view)
        self._tag_form_presenter = TagFormPresenter(tag_form, self._record_keeper)
        category_form = CategoryForm(parent=self._view)
        self._category_form_presenter = CategoryFormPresenter(
            category_form, self._record_keeper
        )
        settings_form = SettingsForm(parent=self._view)
        self._settings_form_presenter = SettingsFormPresenter(settings_form)

    def _setup_event_observers(self) -> None:
        self._account_tree_presenter.event_data_changed.append(self._data_changed)
        self._account_tree_presenter.event_check_state_changed.append(
            self._update_valid_accounts
        )
        self._currency_form_presenter.event_base_currency_changed.append(
            self._base_currency_changed
        )
        self._currency_form_presenter.event_data_changed.append(self._data_changed)
        self._security_form_presenter.event_data_changed.append(self._data_changed)
        self._payee_form_presenter.event_data_changed.append(self._data_changed)
        self._tag_form_presenter.event_data_changed.append(self._data_changed)
        self._category_form_presenter.event_data_changed.append(self._data_changed)
        self._transactions_presenter.event_data_changed.append(self._data_changed)

    def _connect_view_signals(self) -> None:
        self._view.signal_exit.connect(self._quit)
        self._view.signal_open_currency_form.connect(
            self._currency_form_presenter.show_form
        )
        self._view.signal_open_security_form.connect(
            self._security_form_presenter.show_form
        )
        self._view.signal_open_payee_form.connect(self._payee_form_presenter.show_form)
        self._view.signal_open_tag_form.connect(self._tag_form_presenter.show_form)
        self._view.signal_open_category_form.connect(
            self._category_form_presenter.show_form
        )
        self._view.signal_open_settings_form.connect(
            self._settings_form_presenter.show_form
        )

        self._view.signal_save_file.connect(lambda: self._save_to_file(save_as=False))
        self._view.signal_save_file_as.connect(lambda: self._save_to_file(save_as=True))
        self._view.signal_open_file.connect(self._load_from_file)
        self._view.signal_open_recent_file.connect(
            lambda path: self._load_from_file(path)
        )
        self._view.signal_clear_recent_files.connect(self._clear_recent_paths)
        self._view.signal_close_file.connect(self._close_file)

        self._view.signal_show_account_tree.connect(
            lambda checked: self._account_tree_presenter.set_widget_visibility(
                visible=checked
            )
        )

    def _initialize_recent_paths(self) -> None:
        if not constants.recent_files_path.exists():
            logging.debug("Recent Files not found, initializing to empty list")
            self._recent_paths: list[Path] = []
        else:
            with constants.recent_files_path.open(encoding="UTF-8") as file:
                logging.debug(f"Loading Recent Files: {constants.recent_files_path}")
                paths_as_str: list[str] = json.load(file, cls=CustomJSONDecoder)
                self._recent_paths = [Path(path) for path in paths_as_str]

        self._update_recent_paths_menu()

    def _save_recent_paths(self) -> None:
        paths_as_str = [str(path) for path in self._recent_paths]
        with constants.recent_files_path.open(mode="w", encoding="UTF-8") as file:
            logging.debug(f"Saving Recent Files: {constants.recent_files_path}")
            json.dump(paths_as_str, file, cls=CustomJSONEncoder)

    def _add_recent_path(self, path: Path) -> None:
        logging.debug(f"Adding a Recent File: {path}")
        if path in self._recent_paths:
            self._recent_paths.remove(path)
        self._recent_paths.insert(0, path)

        self._save_recent_paths()
        self._update_recent_paths_menu()

    def _update_recent_paths_menu(self) -> None:
        recent_paths = [str(path) for path in self._recent_paths]
        self._view.set_recent_files_menu(recent_paths)

    def _clear_recent_paths(self) -> None:
        logging.debug("Clearing Recent Files")
        self._recent_paths = []
        self._save_recent_paths()
        self._update_recent_paths_menu()

    def _update_valid_accounts(self) -> None:
        self._transactions_presenter.account_tree_shown_accounts = (
            self._account_tree_presenter.valid_accounts
        )

    def _data_changed(self) -> None:
        self._transactions_presenter.update_filter_models()
        self._transactions_presenter.refresh_view()
        self._transactions_presenter.reapply_sort()
        self._account_tree_presenter.refresh_view()
        self._account_tree_presenter.update_total_balance()
        self._account_tree_presenter.update_geometries()
        self._update_unsaved_changes(unsaved_changes=True)

    def _base_currency_changed(self) -> None:
        self._account_tree_presenter.update_model_data()
        self._transactions_presenter.update_base_currency()
        self._transactions_presenter.resize_table_to_contents()
        self._data_changed()
