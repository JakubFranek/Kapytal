import logging
from datetime import date
from decimal import Decimal

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QAbstractButton, QDialogButtonBox, QWidget
from src.views import icons
from src.views.base_classes.custom_dialog import CustomDialog
from src.views.ui_files.dialogs.Ui_set_security_price_dialog import (
    Ui_SetSecurityPriceDialog,
)


class SetSecurityPriceDialog(CustomDialog, Ui_SetSecurityPriceDialog):
    signal_ok = pyqtSignal()

    def __init__(
        self,
        date_today: date,
        last_value: Decimal,
        currency_code: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(icons.set_security_price)
        self.priceDoubleSpinBox.setMaximum(1_000_000_000_000)
        self.priceDoubleSpinBox.setValue(last_value)
        self.priceDoubleSpinBox.setDecimals(9)
        self.priceDoubleSpinBox.setSuffix(" " + currency_code)
        self.dateEdit.setDate(date_today)
        self.dateEdit.setMaximumDate(date_today)

        self.buttonBox.clicked.connect(self._handle_button_box_click)

    @property
    def value(self) -> Decimal:
        return Decimal(self.priceDoubleSpinBox.cleanText().replace(",", ""))

    @property
    def date_(self) -> date:
        return self.dateEdit.date().toPyDate()

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