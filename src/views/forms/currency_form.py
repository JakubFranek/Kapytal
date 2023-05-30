from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QHeaderView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.constants import (
    CurrencyTableColumn,
    ExchangeRateTableColumn,
    ValueTableColumn,
)
from src.views.ui_files.forms.Ui_currency_form import Ui_CurrencyForm


# TODO: change visual style from side buttons to tool buttons and context menu
# TODO: add some way to view and edit exchange rate history
class CurrencyForm(CustomWidget, Ui_CurrencyForm):
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
        self._initialize_actions()

    def set_currency_actions(self, *, is_currency_selected: bool) -> None:
        self.actionSet_Base_Currency.setEnabled(is_currency_selected)
        self.actionRemove_Currency.setEnabled(is_currency_selected)

    def set_exchange_rate_actions(self, *, is_exchange_rate_selected: bool) -> None:
        self.actionRemove_Exchange_Rate.setEnabled(is_exchange_rate_selected)

    def refresh_currency_table(self) -> None:
        self.currencyTable.viewport().update()

    def set_history_group_box_title(self, title: str) -> None:
        self.exchangeRateHistoryGroupBox.setTitle(title)

    def finalize_setup(self) -> None:
        # TODO: review resizetocontents settings, resizing precision etc
        self.currencyTable.horizontalHeader().setStretchLastSection(False)
        self.currencyTable.horizontalHeader().setSectionResizeMode(
            CurrencyTableColumn.CODE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.currencyTable.horizontalHeader().setSectionResizeMode(
            CurrencyTableColumn.PLACES,
            QHeaderView.ResizeMode.Stretch,
        )

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

        self.exchangeRateHistoryTable.horizontalHeader().setStretchLastSection(False)
        self.exchangeRateHistoryTable.horizontalHeader().setSectionResizeMode(
            ValueTableColumn.DATE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.exchangeRateHistoryTable.horizontalHeader().setSectionResizeMode(
            ValueTableColumn.VALUE,
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

    def _initialize_actions(self) -> None:
        self.actionAdd_Currency.setIcon(icons.add)
        self.actionSet_Base_Currency.setIcon(icons.base_currency)
        self.actionRemove_Currency.setIcon(icons.remove)

        self.actionAdd_Exchange_Rate.setIcon(icons.add)
        self.actionRemove_Exchange_Rate.setIcon(icons.remove)

        self.actionAdd_data.setIcon(icons.add)
        self.actionEdit_data.setIcon(icons.edit)
        self.actionRemove_data.setIcon(icons.remove)
        self.actionLoad_data.setIcon(icons.open_file)

        self.actionAdd_Currency.triggered.connect(self.signal_add_currency.emit)
        self.actionSet_Base_Currency.triggered.connect(
            self.signal_set_base_currency.emit
        )
        self.actionRemove_Currency.triggered.connect(self.signal_remove_currency.emit)

        self.actionAdd_Exchange_Rate.triggered.connect(
            self.signal_add_exchange_rate.emit
        )
        self.actionRemove_Exchange_Rate.triggered.connect(
            self.signal_remove_exchange_rate.emit
        )

        self.addCurrencyToolButton.setDefaultAction(self.actionAdd_Currency)
        self.setBaseCurrencyToolButton.setDefaultAction(self.actionSet_Base_Currency)
        self.removeCurrencyToolButton.setDefaultAction(self.actionRemove_Currency)
        self.addExchangeRateToolButton.setDefaultAction(self.actionAdd_Exchange_Rate)
        self.removeExchangeRateToolButton.setDefaultAction(
            self.actionRemove_Exchange_Rate
        )
        self.addRateToolButton.setDefaultAction(self.actionAdd_data)
        self.editRateToolButton.setDefaultAction(self.actionEdit_data)
        self.removeRateToolButton.setDefaultAction(self.actionRemove_data)
        self.loadToolButton.setDefaultAction(self.actionLoad_data)
