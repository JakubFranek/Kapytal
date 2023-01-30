from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QAbstractButton, QDialog, QDialogButtonBox

from src.views.ui_files.Ui_security_account_dialog import Ui_SecurityAccountDialog


class SecurityAccountDialog(QDialog, Ui_SecurityAccountDialog):
    signal_OK = pyqtSignal()

    def __init__(self, max_position: int, edit: bool = False) -> None:
        super().__init__()
        self.setupUi(self)
        self.resize(270, 105)
        self.currentPathLineEdit.setEnabled(False)
        if edit:
            self.setWindowTitle("Edit Security Account")
            self.setWindowIcon(QIcon("icons_24:pencil.png"))
        else:
            self.setWindowTitle("Add Security Account")
            self.setWindowIcon(QIcon("icons_custom:bank-plus.png"))
            self.currentPathLabel.setVisible(False)
            self.currentPathLineEdit.setVisible(False)

        self.positionSpinBox.setMaximum(max_position)
        self.buttonBox.clicked.connect(self.handle_button_box_click)

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

    def handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_OK.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.close()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")
