import logging
import zoneinfo

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import QAbstractButton, QDialogButtonBox, QFileDialog, QWidget

from src.views.ui_files.forms.Ui_settings_form import Ui_SettingsForm


class SettingsForm(QWidget, Ui_SettingsForm):
    signal_OK = pyqtSignal()
    signal_apply = pyqtSignal()

    signal_open_logs = pyqtSignal()

    signal_open_backup_path = pyqtSignal()
    signal_add_backup_path = pyqtSignal()
    signal_remove_backup_path = pyqtSignal()
    signal_backup_path_selection_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(QIcon("icons_16:gear.png"))

        timezones = sorted(zoneinfo.available_timezones())
        for timezone in timezones:
            self.timeZoneComboBox.addItem(timezone)

        self.buttonBox.clicked.connect(self._handle_button_box_click)
        self.addBackupDirectoryButton.clicked.connect(self.signal_add_backup_path)
        self.removeBackupDirectoryButton.clicked.connect(self.signal_remove_backup_path)
        self.openBackupDirectoryButton.clicked.connect(self.signal_open_backup_path)
        self.openLogsDirectoryButton.clicked.connect(self.signal_open_logs)

    @property
    def time_zone(self) -> str:
        return self.timeZoneComboBox.currentText()

    @time_zone.setter
    def time_zone(self, value: str) -> None:
        self.timeZoneComboBox.setCurrentText(value)

    @property
    def backups_max_size_KB(self) -> int:
        return self.backupsSizeLimitSpinBox.value()

    @backups_max_size_KB.setter
    def backups_max_size_KB(self, value: int) -> None:
        self.backupsSizeLimitSpinBox.setValue(value)

    @property
    def logs_max_size_KB(self) -> int:
        return self.logsSizeLimitSpinBox.value()

    @logs_max_size_KB.setter
    def logs_max_size_KB(self, value: int) -> None:
        self.logsSizeLimitSpinBox.setValue(value)

    def show_form(self) -> None:
        logging.debug(f"Showing {self.__class__.__name__}")
        self.show()

    def get_directory_path(self) -> str:
        return QFileDialog.getExistingDirectory(self)

    def set_backup_path_buttons(self, is_backup_path_selected: bool) -> None:
        self.openBackupDirectoryButton.setEnabled(is_backup_path_selected)
        self.removeBackupDirectoryButton.setEnabled(is_backup_path_selected)

    def closeEvent(self, a0: QCloseEvent) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().closeEvent(a0)

    def finalize_setup(self) -> None:
        self.backupsListView.selectionModel().selectionChanged.connect(
            self.signal_backup_path_selection_changed.emit
        )

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_OK.emit()
        elif role == QDialogButtonBox.ButtonRole.ApplyRole:
            self.signal_apply.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.close()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")
