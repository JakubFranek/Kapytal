import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QAbstractButton, QDialogButtonBox, QWidget
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_tag_dialog import Ui_TagDialog


class TagDialog(CustomDialog, Ui_TagDialog):
    signal_ok = pyqtSignal()

    def __init__(self, parent: QWidget, *, edit: bool = False) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.resize(270, 80)
        if edit:
            self.setWindowTitle("Rename Tag")
            self.setWindowIcon(icons.edit_tag)
        else:
            self.setWindowTitle("Add Tag")
            self.setWindowIcon(icons.add_tag)

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
            self.signal_ok.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.reject()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")

    def reject(self) -> None:
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().reject()
