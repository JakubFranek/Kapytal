import json
import logging
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.utilities import constants
from src.utilities.general import backup_json_file
from src.views.dialogs.busy_dialog import (
    create_multi_step_busy_indicator,
    create_simple_busy_indicator,
)
from src.views.main_view import MainView


class FilePresenter:
    event_load_record_keeper = Event()

    def __init__(self, view: MainView) -> None:
        self._view = view
        self._initialize_recent_paths()

        # File path initialization
        self._current_file_path: Path | None = None
        self.update_unsaved_changes(unsaved_changes=False)

    # TODO: try to load/save files on separate threads
    def save_to_file(self, record_keeper: RecordKeeper, *, save_as: bool) -> None:
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

            self._busy_indicator_dialog = create_simple_busy_indicator(
                self._view,
                text="Saving data to file, please wait...",
                lower_text=(
                    "This can take up to a minute for "
                    "large number of Transactions (>10,000)"
                ),
            )
            self._busy_indicator_dialog.open()
            QApplication.processEvents()
            try:
                with self._current_file_path.open(mode="w", encoding="UTF-8") as file:
                    data = {
                        "version": constants.VERSION,
                        "datetime_saved": datetime.now(
                            user_settings.settings.time_zone
                        ),
                        "data": record_keeper,
                    }
                    logging.debug(f"Saving to file: {self._current_file_path}")
                    json.dump(data, file, cls=CustomJSONEncoder)

                    self.update_unsaved_changes(unsaved_changes=False)
                    self._view.show_status_message(
                        f"File saved: {self._current_file_path}", 3000
                    )

                    logging.info(f"File saved: {self._current_file_path}")
            except:  # noqa: TRY302
                raise
            finally:
                self._busy_indicator_dialog.close()
            backup_json_file(self._current_file_path)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)

    def load_from_file(self, path: str | Path | None = None) -> None:
        logging.debug("Load from file initiated")
        if self.check_for_unsaved_changes("Load File") is False:
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

    def close_file(self) -> None:
        if self.check_for_unsaved_changes("Close File") is False:
            return
        logging.info("Closing File, resetting to clean state")
        self.event_load_record_keeper(RecordKeeper())
        self._current_file_path = None
        self.update_unsaved_changes(unsaved_changes=False)

    def update_unsaved_changes(self, *, unsaved_changes: bool) -> None:
        self._unsaved_changes = unsaved_changes
        self._view.set_save_status(
            self._current_file_path, unsaved=self._unsaved_changes
        )

    def check_for_unsaved_changes(self, operation: str) -> bool:
        """True: proceed \n False: abort"""

        if not self._unsaved_changes:
            return True

        logging.info(
            f"Operation '{operation}' called with unsaved changes, asking the "
            "user for instructions"
        )
        reply = self._view.ask_save_before_close()
        if reply is True:
            self.save_to_file(save_as=False)
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

    def _open_file(self, path: Path) -> None:
        self._busy_indicator_dialog = create_multi_step_busy_indicator(
            self._view,
            text="Loading data from file...",
            steps=2,
            lower_text="This can take up to a minute for huge files (>10 MB)",
        )
        self._busy_indicator_dialog.open()
        QApplication.processEvents()
        try:
            with path.open(mode="r", encoding="UTF-8") as file:
                backup_json_file(self._current_file_path)

                self._busy_indicator_dialog.set_state("Loading data from file...", 0)
                QApplication.processEvents()
                logging.debug(f"Loading file: {self._current_file_path}")
                logging.disable(logging.INFO)  # suppress logging of object creation
                data = json.load(file, cls=CustomJSONDecoder)
                record_keeper: RecordKeeper = data["data"]
                logging.disable(logging.NOTSET)  # enable logging again

                self._busy_indicator_dialog.set_state("Updating User Interface...", 1)
                QApplication.processEvents()
                self.event_load_record_keeper(record_keeper)

                self._view.show_status_message(
                    f"File loaded: {self._current_file_path}", 3000
                )
                self.update_unsaved_changes(unsaved_changes=False)

                self._add_recent_path(self._current_file_path)

                logging.debug(
                    f"Currencies: {len(record_keeper.currencies):,}, "
                    f"Exchange Rates: {len(record_keeper.exchange_rates):,}, "
                    f"Securities: {len(record_keeper.securities):,},"
                    f"AccountGroups: {len(record_keeper.account_groups):,}, "
                    f"Accounts: {len(record_keeper.accounts):,}, "
                    f"Transactions: {len(record_keeper.transactions):,}, "
                    f"Categories: {len(record_keeper.categories):,}, "
                    f"Tags: {len(record_keeper.tags):,}, "
                    f"Payees: {len(record_keeper.tags):,}"
                )
                logging.info(
                    f"File loaded: {path}, version={data['version']}, "
                    f"datetime_saved={data['datetime_saved']}"
                )
        except Exception:  # noqa: TRY302
            raise
        finally:
            self._busy_indicator_dialog.close()

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

    def clear_recent_paths(self) -> None:
        logging.debug("Clearing Recent Files")
        self._recent_paths = []
        self._save_recent_paths()
        self._update_recent_paths_menu()
