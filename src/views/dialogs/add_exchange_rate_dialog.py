import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QAbstractButton, QDialog, QDialogButtonBox, QWidget
from src.views.ui_files.dialogs.Ui_add_exchange_rate_dialog import (
    Ui_AddExchangeRateDialog,
)


class AddExchangeRateDialog(QDialog, Ui_AddExchangeRateDialog):
    signal_ok = pyqtSignal()

    def __init__(
        self,
        currency_codes: list[str],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon("icons_custom:currency-arrow.png"))
        self.setWindowTitle("Add Exchange Rate")

        for code in currency_codes:
            self.primaryCurrencyComboBox.addItem(code)
            self.secondaryCurrencyComboBox.addItem(code)
        self.primaryCurrencyComboBox.setCurrentIndex(0)
        self.secondaryCurrencyComboBox.setCurrentIndex(1)

        self.buttonBox.clicked.connect(self._handle_button_box_click)

    @property
    def primary_currency_code(self) -> str:
        return self.primaryCurrencyComboBox.currentText()

    @property
    def secondary_currency_code(self) -> str:
        return self.secondaryCurrencyComboBox.currentText()

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
