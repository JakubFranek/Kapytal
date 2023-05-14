import logging
from collections.abc import Collection

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractButton,
    QCompleter,
    QDialogButtonBox,
    QWidget,
)
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_security_account_dialog import (
    Ui_SecurityAccountDialog,
)


class SecurityAccountDialog(CustomDialog, Ui_SecurityAccountDialog):
    signal_ok = pyqtSignal()

    def __init__(
        self, parent: QWidget, max_position: int, paths: Collection[str], *, edit: bool
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(400, 105)
        self.currentPathLineEdit.setEnabled(False)

        self.pathCompleter = QCompleter(paths)
        self.pathCompleter.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.pathLineEdit.setCompleter(self.pathCompleter)

        if edit:
            self.setWindowTitle("Edit Security Account")
            self.setWindowIcon(icons.edit_security_account)
        else:
            self.setWindowTitle("Add Security Account")
            self.setWindowIcon(icons.add_security_account)
            self.currentPathLabel.setVisible(False)
            self.currentPathLineEdit.setVisible(False)

        self.positionSpinBox.setMaximum(max_position)
        self.buttonBox.clicked.connect(self._handle_button_box_click)

    @property
    def path(self) -> str:
        return self.pathLineEdit.text()

    @path.setter
    def path(self, text: str) -> None:
        self.pathLineEdit.setText(text)

    @property
    def current_path(self) -> str:
        return self.currentPathLineEdit.text()

    @current_path.setter
    def current_path(self, text: str) -> None:
        self.currentPathLineEdit.setText(text)

    @property
    def position(self) -> int:
        return self.positionSpinBox.value()

    @position.setter
    def position(self, value: int) -> None:
        self.positionSpinBox.setValue(value)

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
