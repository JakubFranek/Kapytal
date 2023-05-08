import logging

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QCloseEvent
from PyQt6.QtWidgets import QHeaderView, QWidget
from src.views import icons
from src.views.constants import ExchangeRateTableColumn
from src.views.ui_files.forms.Ui_currency_form import Ui_CurrencyForm


# TODO: change visual style from side buttons to tool buttons and context menu
# TODO: add some way to view and edit exchange rate history
class CurrencyForm(QWidget, Ui_CurrencyForm):
    signal_add_currency = pyqtSignal()
    signal_set_base_currency = pyqtSignal()
    signal_remove_currency = pyqtSignal()
    signal_add_exchange_rate = pyqtSignal()
    signal_remove_exchange_rate = pyqtSignal()
    signal_set_exchange_rate = pyqtSignal()
    signal_currency_selection_changed = pyqtSignal()
    signal_exchange_rate_selection_changed = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.currency)

        self.setBaseCurrencyButton.setIcon(icons.base_currency)

        self.addCurrencyButton.clicked.connect(self.signal_add_currency.emit)
        self.setBaseCurrencyButton.clicked.connect(self.signal_set_base_currency.emit)
        self.removeCurrencyButton.clicked.connect(self.signal_remove_currency.emit)
        self.addExchangeRateButton.clicked.connect(self.signal_add_exchange_rate.emit)
        self.removeExchangeRateButton.clicked.connect(
            self.signal_remove_exchange_rate.emit
        )
        self.setExchangeRateButton.clicked.connect(self.signal_set_exchange_rate.emit)

    def show_form(self) -> None:
        logging.debug(f"Showing {self.__class__.__name__}")
        self.show()

    def closeEvent(self, a0: QCloseEvent) -> None:  # noqa: N802
        logging.debug(f"Closing {self.__class__.__name__}")
        return super().closeEvent(a0)

    def set_currency_buttons(self, *, is_currency_selected: bool) -> None:
        self.setBaseCurrencyButton.setEnabled(is_currency_selected)
        self.removeCurrencyButton.setEnabled(is_currency_selected)

    def set_exchange_rate_buttons(self, *, is_exchange_rate_selected: bool) -> None:
        self.setExchangeRateButton.setEnabled(is_exchange_rate_selected)
        self.removeExchangeRateButton.setEnabled(is_exchange_rate_selected)

    def refresh_currency_table(self) -> None:
        self.currencyTable.viewport().update()

    def finalize_setup(self) -> None:
        self.exchangeRateTable.horizontalHeader().setStretchLastSection(False)
        self.exchangeRateTable.horizontalHeader().setSectionResizeMode(
            ExchangeRateTableColumn.CODE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.exchangeRateTable.horizontalHeader().setSectionResizeMode(
            ExchangeRateTableColumn.RATE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.exchangeRateTable.horizontalHeader().setSectionResizeMode(
            ExchangeRateTableColumn.LAST_DATE,
            QHeaderView.ResizeMode.Stretch,
        )

        style = self.style()
        last_section_text = self.exchangeRateTable.model().headerData(
            ExchangeRateTableColumn.LAST_DATE,
            Qt.Orientation.Horizontal,
            Qt.ItemDataRole.DisplayRole,
        )
        self.exchangeRateTable.horizontalHeader().setMinimumSectionSize(
            style.pixelMetric(style.PixelMetric.PM_HeaderMarkSize)
            + style.pixelMetric(style.PixelMetric.PM_HeaderGripMargin) * 2
            + self.fontMetrics().horizontalAdvance(last_section_text)
        )

        self.exchangeRateTable.selectionModel().selectionChanged.connect(
            self.signal_exchange_rate_selection_changed.emit
        )
        self.currencyTable.selectionModel().selectionChanged.connect(
            self.signal_currency_selection_changed.emit
        )
