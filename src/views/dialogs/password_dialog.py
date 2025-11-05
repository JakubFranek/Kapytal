from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QAbstractButton, QDialogButtonBox, QWidget
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_password_dialog import Ui_PasswordDialog


class PasswordDialog(CustomDialog, Ui_PasswordDialog):
    signal_ok = pyqtSignal()
    signal_cancel = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(270, 80)
        self.setWindowIcon(icons.password)

        self.buttonBox.clicked.connect(self._handle_button_box_click)

    @property
    def password(self) -> str:
        return self.passwordLineEdit.text()

    def set_window_title(self, title: str) -> None:
        self.setWindowTitle(title)

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_ok.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.signal_cancel.emit()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")
