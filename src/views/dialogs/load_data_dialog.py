import logging
from enum import Enum, auto

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QAbstractButton, QDialogButtonBox, QFileDialog, QWidget
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_load_data_dialog import Ui_LoadDataDialog


class ConflictResolutionMode(Enum):
    KEEP = auto()
    OVERWRITE = auto()


class LoadDataDialog(CustomDialog, Ui_LoadDataDialog):
    signal_ok = pyqtSignal()

    def __init__(self, parent: QWidget, data_name: str) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(320, 80)
        self.setWindowTitle(f"Load {data_name} Data")
        self.setWindowIcon(icons.open_file)

        self.actionSelect_File.setIcon(icons.open_file)
        self.actionSelect_File.triggered.connect(self._select_file)
        self.pathToolButton.setDefaultAction(self.actionSelect_File)
        self.buttonBox.clicked.connect(self._handle_button_box_click)

    def _select_file(self) -> str:
        path = QFileDialog.getOpenFileName(self, filter="CSV file (*.csv)")[0]
        self.pathLineEdit.setText(path)

    @property
    def path(self) -> str:
        return self.pathLineEdit.text()

    @property
    def conflict_resolution_mode(self) -> ConflictResolutionMode:
        if self.keepRadioButton.isChecked():
            return ConflictResolutionMode.KEEP
        if self.overwriteRadioButton.isChecked():
            return ConflictResolutionMode.OVERWRITE
        raise ValueError("Unknown conflict resolution mode")

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_ok.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def reject(self) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().reject()
