import json
import logging
from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QObject, QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication
from src.models.json.custom_json_decoder import CustomJSONDecoder
from src.models.json.custom_json_encoder import CustomJSONEncoder
from src.models.record_keeper import RecordKeeper
from src.models.user_settings import user_settings
from src.presenters.utilities.event import Event
from src.presenters.utilities.handle_exception import handle_exception
from src.utilities import constants
from src.utilities.general import backup_json_file
from src.views.dialogs.busy_dialog import create_multi_step_busy_indicator
from src.views.main_view import MainView


class LoadFileWorker(QObject):
    finished = pyqtSignal()
    failed = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.path: Path

    def run(self) -> None:
        try:
            with self.path.open(mode="r", encoding="UTF-8") as file:
                logging.disable(logging.INFO)  # suppress logging of object creation
                self.data = json.load(file, cls=CustomJSONDecoder)
                self.record_keeper = RecordKeeper.deserialize(
                    self.data["data"],
                    progress_callable=self._progress,
                )
                logging.disable(logging.NOTSET)
                self.finished.emit()
        except Exception as exc:  # noqa: BLE001
            self.exception = exc
            self.failed.emit()

    def _progress(self, progress: int) -> None:
        self.progress.emit(progress)


class SaveFileWorker(QObject):
    finished = pyqtSignal()
    failed = pyqtSignal()
    progress = pyqtSignal(int)
    status_text = pyqtSignal(str)
    progress_unknown = pyqtSignal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.path: Path
        self.record_keeper: RecordKeeper

    def run(self) -> None:
        try:
            with self.path.open(mode="w", encoding="UTF-8") as file:
                self.status_text.emit("Serializing data...")
                data = {
                    "version": constants.VERSION,
                    "datetime_saved": datetime.now(user_settings.settings.time_zone),
                    "data": self.record_keeper.serialize(self._progress),
                }
                self.progress_unknown.emit()
                self.status_text.emit("Writing to file...")
                json.dump(data, file, cls=CustomJSONEncoder, ensure_ascii=False)
                self.finished.emit()
        except Exception as exc:  # noqa: BLE001
            self.exception = exc
            self.failed.emit()

    def _progress(self, progress: int) -> None:
        self.progress.emit(progress)


class FilePresenter:
    event_load_record_keeper = Event()

    def __init__(self, view: MainView, record_keeper: RecordKeeper) -> None:
        self._view = view
        self._initialize_recent_paths()
        self.load_record_keeper(record_keeper)

        # File path initialization
        self._current_file_path: Path | None = None
        self.update_unsaved_changes(unsaved_changes=False)

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

    def save_to_file(self, record_keeper: RecordKeeper, *, save_as: bool) -> None:
        logging.debug("Save to file initiated")
        if save_as is True or self._current_file_path is None:
            logging.debug("Asking the user for destination path")
            file_path = self._view.get_save_path()
            if not file_path:
                logging.info("Save to file cancelled: invalid or no file path received")
                return
            self._current_file_path = Path(file_path)

        logging.debug(f"Saving to file: {self._current_file_path}")
        self._save_to_file(record_keeper, self._current_file_path)

    def load_from_file(self, path: str | Path | None = None) -> None:
        logging.debug("Load from file initiated")
        if self.check_for_unsaved_changes("Load File") is False:
            return
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
            self.save_to_file(self._record_keeper, save_as=False)
            # FIXME: due to multithreaded saving, the next line is always False and the program does not Quit
            # solution: pass operation function as argument and perform it once thread is done
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
        self._busy_indicator = create_multi_step_busy_indicator(
            self._view, "Loading data, please wait...", 100, "Deserializing data..."
        )

        backup_json_file(self._current_file_path)
        self._thread = QThread()
        self._worker = LoadFileWorker()
        self._worker.moveToThread(self._thread)
        self._worker.path = path
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._file_load_completed)
        self._worker.failed.connect(self._worker_operation_failed)
        self._worker.progress.connect(self._update_load_progress)
        self._view.set_item_view_update_state(enabled=False)
        self._thread.start()
        self._busy_indicator.open()

    def _update_load_progress(self, progress: int) -> None:
        self._busy_indicator.set_value(progress)

    def _file_load_completed(self) -> None:
        self._busy_indicator.set_progress_bar_range(0, 0)
        self._busy_indicator.set_lower_text("Updating User Interface...")
        self._view.set_item_view_update_state(enabled=True)
        QApplication.processEvents()

        data = self._worker.data
        record_keeper = self._worker.record_keeper
        self._worker.thread().quit()
        self._worker.deleteLater()
        self._thread.deleteLater()

        self.event_load_record_keeper(record_keeper)

        self._view.show_status_message(f"File loaded: {self._current_file_path}", 3000)
        self.update_unsaved_changes(unsaved_changes=False)

        self._add_recent_path(self._current_file_path)

        logging.info(
            f"File loaded: {self._current_file_path}, version={data['version']}, "
            f"datetime_saved={data['datetime_saved']}, "
            f"Currencies: {len(record_keeper.currencies)}, "
            f"Exchange Rates: {len(record_keeper.exchange_rates)}, "
            f"Securities: {len(record_keeper.securities)}, "
            f"AccountGroups: {len(record_keeper.account_groups)}, "
            f"Accounts: {len(record_keeper.accounts)}, "
            f"Transactions: {len(record_keeper.transactions)}, "
            f"Categories: {len(record_keeper.categories)}, "
            f"Tags: {len(record_keeper.tags)}, "
            f"Payees: {len(record_keeper.tags)}"
        )
        self._busy_indicator.close()

    def _worker_operation_failed(self) -> None:
        exception = self._worker.exception
        self._worker.thread().quit()
        self._worker.deleteLater()
        self._thread.deleteLater()
        self._busy_indicator.close()
        handle_exception(exception)

    def _save_to_file(self, record_keeper: RecordKeeper, path: Path) -> None:
        self._busy_indicator = create_multi_step_busy_indicator(
            self._view,
            "Saving data, please wait...",
            100,
            "Starting separate thread...",
        )

        self._thread = QThread()
        self._worker = SaveFileWorker()
        self._worker.moveToThread(self._thread)
        self._worker.path = path
        self._worker.record_keeper = record_keeper
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._file_save_completed)
        self._worker.failed.connect(self._worker_operation_failed)
        self._worker.progress.connect(self._update_file_save_progress)
        self._worker.status_text.connect(self._update_file_save_status_text)
        self._worker.progress_unknown.connect(self._update_file_save_progress_bar_range)
        self._view.set_item_view_update_state(enabled=False)
        self._thread.start()
        self._busy_indicator.open()

    def _update_file_save_progress(self, progress: int) -> None:
        self._busy_indicator.set_value(progress)

    def _update_file_save_status_text(self, text: str) -> None:
        self._busy_indicator.set_lower_text(text)

    def _update_file_save_progress_bar_range(self) -> None:
        self._busy_indicator.set_progress_bar_range(0, 0)

    def _file_save_completed(self) -> None:
        self._busy_indicator.close()
        self._view.set_item_view_update_state(enabled=True)

        self._worker.thread().quit()
        self._worker.deleteLater()
        self._thread.deleteLater()

        self.update_unsaved_changes(unsaved_changes=False)
        self._view.show_status_message(f"File saved: {self._current_file_path}", 3000)

        logging.info(f"File saved: {self._current_file_path}")
        backup_json_file(self._current_file_path)

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
