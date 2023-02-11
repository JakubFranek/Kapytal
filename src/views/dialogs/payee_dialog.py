import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QAbstractButton, QDialog, QDialogButtonBox, QWidget

from src.views.ui_files.Ui_payee_dialog import Ui_PayeeDialog


class PayeeDialog(QDialog, Ui_PayeeDialog):
    signal_OK = pyqtSignal()

    def __init__(self, parent: QWidget, edit: bool = False) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(270, 80)
        if edit:
            self.setWindowTitle("Rename Payee")
            self.setWindowIcon(QIcon("icons_custom:user-silhouette-pencil.png"))
        else:
            self.setWindowTitle("Add Payee")
            self.setWindowIcon(QIcon("icons_custom:user-silhouette-plus.png"))

        self.buttonBox.clicked.connect(self._handle_button_box_click)

    @property
    def name(self) -> str:
        return self.nameLineEdit.text()

    @name.setter
    def name(self, text: str) -> None:
        self.nameLineEdit.setText(text)

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_OK.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def reject(self) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().reject()
