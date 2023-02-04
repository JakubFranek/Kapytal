import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent, QIcon
from PyQt6.QtWidgets import QWidget

from src.views.ui_files.Ui_currency_form import Ui_CurrencyForm


class CurrencyForm(QWidget, Ui_CurrencyForm):
    signal_add_currency = pyqtSignal()
    signal_set_base_currency = pyqtSignal()
    signal_remove_currency = pyqtSignal()
    signal_add_exchange_rate = pyqtSignal()
    signal_remove_exchange_rate = pyqtSignal()
    signal_set_exchange_rate = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(QIcon("icons_16:currency.png"))

        self.setBaseCurrencyButton.setIcon(QIcon("icons_16:star.png"))

        self.addCurrencyButton.clicked.connect(self.signal_add_currency.emit)
        self.setBaseCurrencyButton.clicked.connect(self.signal_set_base_currency.emit)
        self.removeCurrencyButton.clicked.connect(self.signal_remove_currency.emit)
        self.addExchangeRateButton.clicked.connect(self.signal_add_exchange_rate.emit)
        self.removeExchangeRateButton.clicked.connect(
            self.signal_remove_exchange_rate.emit
        )
        self.setExchangeRateButton.clicked.connect(self.signal_set_exchange_rate.emit)

    def show_form(self) -> None:
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:
        logging.info(f"Closing {self.__class__.__name__}")
        return super().closeEvent(a0)
