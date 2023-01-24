from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QAbstractButton, QDialog, QDialogButtonBox, QMessageBox

from src.views.ui_files.Ui_account_group_dialog import Ui_AccountGroupDialog


class AccountGroupDialog(QDialog, Ui_AccountGroupDialog):
    signal_OK = pyqtSignal()

    def __init__(self, edit: bool = False) -> None:
        super().__init__()
        self.setupUi(self)
        if not edit:
            self.setWindowTitle("Add Account Group")
            self.setWindowIcon(QIcon("icons_24:plus.png"))
        else:
            self.setWindowTitle("Edit Account Group")
            self.setWindowIcon(QIcon("icons_24:pencil.png"))

        self.resize(500, 100)

        self.buttonBox.clicked.connect(self.handleButtonBoxClick)

    @property
    def path(self) -> str:
        return self.pathLineEdit.text()

    @path.setter
    def path(self, text: str) -> None:
        self.pathLineEdit.setText(text)

    def handleButtonBoxClick(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_OK.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.close()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def display_error(
        self,
        text: str,
        exc_details: str,
        critical: bool = False,
        title: str = "Error!",
    ) -> None:
        message_box = QMessageBox()

        if critical is True:
            message_box.setIcon(QMessageBox.Icon.Critical)
            message_box.setWindowIcon(QIcon("icons_24:cross.png"))
        else:
            message_box.setIcon(QMessageBox.Icon.Warning)
            message_box.setWindowIcon(QIcon("icons_24:exclamation.png"))

        message_box.setWindowTitle(title)
        message_box.setText(text)
        message_box.setDetailedText(exc_details)

        message_box.exec()
