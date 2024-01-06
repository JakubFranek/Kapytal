import copy
import logging
import os
from pathlib import Path

from src.models.user_settings import user_settings
from src.presenters.utilities.handle_exception import handle_exception
from src.utilities import constants
from src.view_models.backup_paths_list_model import BackupPathsListModel
from src.views.forms.settings_form import SettingsForm


class SettingsFormPresenter:
    def __init__(self, view: SettingsForm) -> None:
        self._view = view

        self._backup_paths = list(user_settings.settings.backup_paths)

        self._backup_paths_list_model = BackupPathsListModel(self._view.backupsListView)
        self._view.backupsListView.setModel(self._backup_paths_list_model)

        self._view.signal_ok.connect(lambda: self.save(close=True))
        self._view.signal_apply.connect(lambda: self.save(close=False))
        self._view.signal_backup_path_selection_changed.connect(
            self._backup_path_selection_changed
        )
        self._view.signal_data_changed.connect(
            lambda: self._set_unsaved_changes(unsaved=True)
        )

        self._view.signal_add_backup_path.connect(self.add_backup_path)
        self._view.signal_remove_backup_path.connect(self.remove_backup_path)
        self._view.signal_open_backup_path.connect(self.open_backup_path)
        self._view.signal_open_logs.connect(self.open_logs_path)

        self._set_unsaved_changes(unsaved=False)

        self._view.finalize_setup()
        self._backup_path_selection_changed()

    def show_form(self) -> None:
        self._view.backups_max_size_kb = (
            user_settings.settings.backups_max_size_bytes // 1000
        )
        self._view.logs_max_size_kb = user_settings.settings.logs_max_size_bytes // 1000
        self._view.general_date_format = user_settings.settings.general_date_format
        self._view.transaction_date_format = (
            user_settings.settings.transaction_date_format
        )
        self._view.exchange_rate_decimals = (
            user_settings.settings.exchange_rate_decimals
        )
        self._view.price_per_share_decimals = (
            user_settings.settings.price_per_share_decimals
        )
        self._view.check_for_updates_on_startup = (
            user_settings.settings.check_for_updates_on_startup
        )
        self._backup_paths = list(user_settings.settings.backup_paths)
        self._backup_paths_list_model.pre_reset_model()
        self.update_model_data()
        self._backup_paths_list_model.post_reset_model()
        self._view.show_form()

    def update_model_data(self) -> None:
        self._backup_paths_list_model.load_paths(self._backup_paths)

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

        self._set_unsaved_changes(unsaved=True)

    def remove_backup_path(self) -> None:
        path = self._backup_paths_list_model.get_selected_item()
        if path is None:
            return

        logging.debug(f"Removing backup path from staging list: {path}")
        try:
            self._backup_paths.remove(path)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            return

        self._backup_paths_list_model.pre_remove_item(path)
        self.update_model_data()
        self._backup_paths_list_model.post_remove_item()

        self._set_unsaved_changes(unsaved=True)

    def save(self, *, close: bool) -> None:
        if not self._unsaved_changes:
            logging.debug("UserSettings save initiated: no unsaved changes, skipping")
            if close:
                self._view.close()
            return

        logging.debug("UserSettings save initiated")
        backup_size_limit_bytes = self._view.backups_max_size_kb * 1000
        logs_size_limit_bytes = self._view.logs_max_size_kb * 1000

        settings_copy = copy.copy(user_settings.settings)
        try:
            user_settings.settings.backups_max_size_bytes = backup_size_limit_bytes
            user_settings.settings.logs_max_size_bytes = logs_size_limit_bytes
            user_settings.settings.backup_paths = self._backup_paths
            user_settings.settings.general_date_format = self._view.general_date_format
            user_settings.settings.transaction_date_format = (
                self._view.transaction_date_format
            )
            user_settings.settings.exchange_rate_decimals = (
                self._view.exchange_rate_decimals
            )
            user_settings.settings.price_per_share_decimals = (
                self._view.price_per_share_decimals
            )
            user_settings.settings.check_for_updates_on_startup = (
                self._view.check_for_updates_on_startup
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
            user_settings.settings = settings_copy
            return

        user_settings.save()
        self._set_unsaved_changes(unsaved=False)

        if close:
            self._view.close()

    def open_backup_path(self) -> None:
        path = self._backup_paths_list_model.get_selected_item()
        if path is None:
            raise ValueError("Cannot open an unselected path.")

        logging.debug(f"Opening backup path in File Explorer: {path}")
        os.startfile(path)

    def open_logs_path(self) -> None:
        logging.debug(
            f"Opening logs path in File Explorer: {constants.logs_folder_path}"
        )
        os.startfile(constants.logs_folder_path)

    def _backup_path_selection_changed(self) -> None:
        item = self._backup_paths_list_model.get_selected_item()
        is_backup_path_selected = item is not None
        self._view.set_backup_path_buttons(
            is_backup_path_selected=is_backup_path_selected
        )

    def _set_unsaved_changes(self, *, unsaved: bool) -> None:
        self._unsaved_changes = unsaved
