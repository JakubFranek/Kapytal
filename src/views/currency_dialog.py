from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QAbstractButton, QDialog, QDialogButtonBox, QWidget

from src.views.ui_files.Ui_currency_dialog import Ui_CurrencyDialog


class CurrencyDialog(QDialog, Ui_CurrencyDialog):
    signal_OK = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon("icons_custom:currency-plus.png"))
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
            self.signal_OK.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.close()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")
