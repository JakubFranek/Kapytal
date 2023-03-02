import logging
import os
from pathlib import Path

import src.models.user_settings.user_settings as user_settings
from src.presenters.utilities.handle_exception import handle_exception
from src.presenters.view_models.backup_paths_list_model import BackupPathsListModel
from src.views.forms.settings_form import SettingsForm


class SettingsFormPresenter:
    def __init__(self, view: SettingsForm, app_root_path: Path) -> None:
        self._view = view
        self._logs_path = app_root_path / "logs"

        self._backup_paths = list(user_settings.settings.backup_paths)

        self._backup_paths_list_model = BackupPathsListModel(
            self._view.backupsListView, user_settings.settings.backup_paths
        )
        self._view.backupsListView.setModel(self._backup_paths_list_model)

        self._view.signal_OK.connect(lambda: self.save(close=True))
        self._view.signal_apply.connect(lambda: self.save(close=False))
        self._view.signal_backup_path_selection_changed.connect(
            self._backup_path_selection_changed
        )
        self._view.signal_data_changed.connect(lambda: self._set_unsaved_changes(True))

        self._view.signal_add_backup_path.connect(self.add_backup_path)
        self._view.signal_remove_backup_path.connect(self.remove_backup_path)
        self._view.signal_open_backup_path.connect(self.open_backup_path)
        self._view.signal_open_logs.connect(self.open_logs_path)

        self._set_unsaved_changes(False)

        self._view.finalize_setup()
        self._backup_path_selection_changed()

    def show_form(self) -> None:
        self._backup_paths = list(user_settings.settings.backup_paths)
        self._view.backups_max_size_KB = (
            user_settings.settings.backups_max_size_bytes // 1000
        )
        self._view.logs_max_size_KB = user_settings.settings.logs_max_size_bytes // 1000
        self._backup_paths = list(user_settings.settings.backup_paths)
        self._backup_paths_list_model.pre_reset_model()
        self.update_model_data()
        self._backup_paths_list_model.post_reset_model()
        self._view.show_form()

    def update_model_data(self) -> None:
        self._backup_paths_list_model.paths = self._backup_paths

    def add_backup_path(self) -> None:
        logging.debug("Backup path addition initiated: asking user for directory")
        path_string = self._view.get_directory_path()

        if not path_string:
            logging.debug("Backup path addition cancelled")
            return

        logging.debug(f"Adding backup path to staging list: {path_string}")
        self._backup_paths.append(Path(path_string))
        self._backup_paths_list_model.pre_add()
        self.update_model_data()
        self._backup_paths_list_model.post_add()

        self._set_unsaved_changes(True)

    def remove_backup_path(self) -> None:
        path = self._backup_paths_list_model.get_selected_item()
        if path is None:
            return

        logging.debug(f"Removing backup path from staging list: {path}")
        try:
            self._backup_paths.remove(path)
        except Exception:
            handle_exception()
            return

        self._backup_paths_list_model.pre_remove_item(path)
        self.update_model_data()
        self._backup_paths_list_model.post_remove_item()

        self._set_unsaved_changes(True)

    def save(self, close: bool) -> None:
        if not self._unsaved_changes:
            logging.debug("UserSettings save initiated: no unsaved changes, skipping")
            if close:
                self._view.close()
            return

        logging.debug("UserSettings save initiated")
        backup_size_limit_bytes = self._view.backups_max_size_KB * 1000
        logs_size_limit_bytes = self._view.logs_max_size_KB * 1000

        user_settings.settings.backups_max_size_bytes = backup_size_limit_bytes
        user_settings.settings.logs_max_size_bytes = logs_size_limit_bytes
        user_settings.settings.backup_paths = self._backup_paths

        user_settings.save()
        self._set_unsaved_changes(False)

        if close:
            self._view.close()

    def open_backup_path(self) -> None:
        path = self._backup_paths_list_model.get_selected_item()
        if path is None:
            raise ValueError("Cannot open an unselected path.")

        logging.debug(f"Opening backup path in File Explorer: {path}")
        os.startfile(path)  # noqa: S606

    def open_logs_path(self) -> None:
        logging.debug(f"Opening logs path in File Explorer: {self._logs_path}")
        os.startfile(self._logs_path)  # noqa: S606

    def _backup_path_selection_changed(self) -> None:
        item = self._backup_paths_list_model.get_selected_item()
        is_currency_selected = item is not None
        self._view.set_backup_path_buttons(is_currency_selected)

    def _set_unsaved_changes(self, unsaved_changes: bool) -> None:
        self._unsaved_changes = unsaved_changes
