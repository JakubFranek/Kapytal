from datetime import date
from decimal import Decimal

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QAbstractButton, QDialog, QDialogButtonBox, QWidget

from src.views.ui_files.Ui_set_exchange_rate_dialog import Ui_SetExchangeRateDialog


class SetExchangeRateDialog(QDialog, Ui_SetExchangeRateDialog):
    signal_OK = pyqtSignal()

    def __init__(
        self,
        date_today: date,
        exchange_rate: str,
        last_value: Decimal,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon("icons_custom:currency-arrow.png"))
        self.exchangeRateLabel.setText(exchange_rate)
        self.exchangeRateDoubleSpinBox.setValue(last_value)
        self.dateEdit.setDate(date_today)
        self.dateEdit.setMaximumDate(date_today)

        self.buttonBox.clicked.connect(self._handle_button_box_click)

    @property
    def value(self) -> Decimal:
        return Decimal(self.exchangeRateDoubleSpinBox.text())

    @property
    def date_(self) -> date:
        return self.dateEdit.date().toPyDate()

    @property
    def exchange_rate_code(self) -> str:
        return self.exchangeRateLabel.text()

    def _handle_button_box_click(self, button: QAbstractButton) -> None:
        role = self.buttonBox.buttonRole(button)
        if role == QDialogButtonBox.ButtonRole.AcceptRole:
            self.signal_OK.emit()
        elif role == QDialogButtonBox.ButtonRole.RejectRole:
            self.close()
        else:
            raise ValueError("Unknown role of the clicked button in the ButtonBox")
