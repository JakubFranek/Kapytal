import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QAbstractButton, QDialogButtonBox, QWidget
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_currency_dialog import Ui_CurrencyDialog


class CurrencyDialog(CustomDialog, Ui_CurrencyDialog):
    signal_ok = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(icons.add_currency)
        self.buttonBox.clicked.connect(self._handle_button_box_click)

    @property
    def currency_code(self) -> str:
        return self.currencyCodeLineEdit.text()

    @property
    def currency_places(self) -> int:
        return self.currencyPlacesSpinBox.value()

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
