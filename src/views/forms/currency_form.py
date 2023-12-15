from collections.abc import Collection

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
from src.views.utilities.helper_functions import calculate_table_width
from src.views.widgets.charts.date_line_chart_view import DateLineChartView


class CurrencyForm(CustomWidget, Ui_CurrencyForm):
    signal_add_currency = pyqtSignal()
    signal_set_base_currency = pyqtSignal()
    signal_remove_currency = pyqtSignal()
    signal_add_exchange_rate = pyqtSignal()
    signal_remove_exchange_rate = pyqtSignal()
    signal_add_data = pyqtSignal()
    signal_edit_data = pyqtSignal()
    signal_remove_data = pyqtSignal()
    signal_load_data = pyqtSignal()
    signal_currency_selection_changed = pyqtSignal()
    signal_exchange_rate_selection_changed = pyqtSignal()
    signal_data_point_selection_changed = pyqtSignal()
    signal_data_point_double_clicked = pyqtSignal()
    signal_update_quotes = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowIcon(icons.currency)
        self._initialize_actions()

        self.chart_widget = DateLineChartView(self)
        self.exchangeRateHistoryTableHorizontalLayout.addWidget(self.chart_widget)

        self.currencyTable.horizontalHeader().setSortIndicatorClearable(True)
        self.exchangeRateTable.horizontalHeader().setSortIndicatorClearable(True)
        self.exchangeRateHistoryTable.horizontalHeader().setSortIndicatorClearable(True)
        self.exchangeRateHistoryTable.doubleClicked.connect(
            self.signal_data_point_double_clicked.emit
        )

    def load_chart_data(
        self, x: Collection, y: Collection, title: str, y_decimals: int
    ) -> None:
        self.chart_widget.load_data(x, y, title, y_decimals=y_decimals)
        self.update_history_table_width()

    def set_currency_actions(self, *, is_currency_selected: bool) -> None:
        self.actionSet_Base_Currency.setEnabled(is_currency_selected)
        self.actionRemove_Currency.setEnabled(is_currency_selected)

    def set_exchange_rate_actions(self, *, is_exchange_rate_selected: bool) -> None:
        self.actionRemove_Exchange_Rate.setEnabled(is_exchange_rate_selected)

    def set_data_point_actions(
        self,
        *,
        is_exchange_rate_selected: bool,
        is_data_point_selected: bool,
        is_single_data_point_selected: bool
    ) -> None:
        self.actionAdd_data.setEnabled(is_exchange_rate_selected)
        self.actionEdit_data.setEnabled(
            is_exchange_rate_selected and is_single_data_point_selected
        )
        self.actionRemove_data.setEnabled(
            is_exchange_rate_selected and is_data_point_selected
        )
        self.actionLoad_data.setEnabled(is_exchange_rate_selected)

    def refresh_currency_table(self) -> None:
        self.currencyTable.viewport().update()

    def set_history_group_box_title(self, title: str) -> None:
        self.exchangeRateHistoryGroupBox.setTitle(title)

    def finalize_setup(self) -> None:
        self.currencyTable.horizontalHeader().setStretchLastSection(False)
        for column in CurrencyTableColumn:
            self.currencyTable.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeMode.ResizeToContents
            )

        self.exchangeRateTable.horizontalHeader().setStretchLastSection(False)
        for column in ExchangeRateTableColumn:
            self.exchangeRateTable.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeMode.ResizeToContents
            )

        self.exchangeRateHistoryTable.horizontalHeader().setStretchLastSection(False)
        for column in ValueTableColumn:
            self.exchangeRateHistoryTable.horizontalHeader().setSectionResizeMode(
                column, QHeaderView.ResizeMode.ResizeToContents
            )

        self.exchangeRateTable.selectionModel().selectionChanged.connect(
            self.signal_exchange_rate_selection_changed.emit
        )
        self.currencyTable.selectionModel().selectionChanged.connect(
            self.signal_currency_selection_changed.emit
        )
        self.exchangeRateHistoryTable.selectionModel().selectionChanged.connect(
            self.signal_data_point_selection_changed.emit
        )

        self.currencyTable.sortByColumn(-1, Qt.SortOrder.AscendingOrder)
        self.exchangeRateTable.sortByColumn(-1, Qt.SortOrder.AscendingOrder)
        self.exchangeRateHistoryTable.sortByColumn(0, Qt.SortOrder.DescendingOrder)

    def _initialize_actions(self) -> None:
        self.actionAdd_Currency.setIcon(icons.add)
        self.actionSet_Base_Currency.setIcon(icons.base_currency)
        self.actionRemove_Currency.setIcon(icons.remove)

        self.actionAdd_Exchange_Rate.setIcon(icons.add)
        self.actionRemove_Exchange_Rate.setIcon(icons.remove)
        self.actionUpdate_Quotes.setIcon(icons.refresh)

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
        self.actionUpdate_Quotes.triggered.connect(self.signal_update_quotes.emit)

        self.actionAdd_data.triggered.connect(self.signal_add_data.emit)
        self.actionEdit_data.triggered.connect(self.signal_edit_data.emit)
        self.actionRemove_data.triggered.connect(self.signal_remove_data.emit)
        self.actionLoad_data.triggered.connect(self.signal_load_data.emit)

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
        self.updateQuotesToolButton.setDefaultAction(self.actionUpdate_Quotes)

    def show_form(self) -> None:
        super().show_form()
        self.update_table_widths()

    def update_table_widths(self) -> None:
        self.exchangeRateTable.resizeColumnsToContents()
        self.update_currency_table_width()
        self.update_history_table_width()

    def update_currency_table_width(self) -> None:
        self.currencyTable.resizeColumnsToContents()
        currency_table_width = calculate_table_width(self.currencyTable)
        self.currencyGroupBox.setFixedWidth(currency_table_width + 30)
        self.currencyTable.horizontalHeader().setSectionResizeMode(
            CurrencyTableColumn.PLACES,
            QHeaderView.ResizeMode.Stretch,
        )

    def update_history_table_width(self) -> None:
        self.exchangeRateHistoryTable.resizeColumnsToContents()

        exchange_rate_history_table_width = calculate_table_width(
            self.exchangeRateHistoryTable
        )
        self.exchangeRateHistoryTableWidget.setFixedWidth(
            exchange_rate_history_table_width + 25
        )
        self.exchangeRateHistoryTable.horizontalHeader().setSectionResizeMode(
            ValueTableColumn.VALUE,
            QHeaderView.ResizeMode.Stretch,
        )
