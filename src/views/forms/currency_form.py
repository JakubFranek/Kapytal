from collections.abc import Collection

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QHeaderView, QTableView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.constants import (
    CurrencyTableColumn,
    ExchangeRateTableColumn,
    ValueTableColumn,
)
from src.views.ui_files.forms.Ui_currency_form import Ui_CurrencyForm


class Canvas(FigureCanvasQTAgg):
    def __init__(self) -> None:
        fig = Figure(figsize=(10, 10), dpi=100)
        self.axes = fig.add_subplot(111)
        super().__init__(fig)


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

        self._chart = Canvas()

        self._chart_toolbar = NavigationToolbar2QT(self._chart, None)
        self.actionHome = QAction(icons.home, "Reset Chart", self)
        self.actionBack = QAction(icons.arrow_left, "Back", self)
        self.actionForward = QAction(icons.arrow_right, "Forward", self)
        self.actionPan = QAction(icons.arrow_move, "Pan", self)
        self.actionZoom = QAction(icons.magnifier, "Zoom", self)
        self.actionSubplots = QAction(icons.slider, "Subplots", self)
        self.actionCustomize = QAction(icons.settings, "Customize", self)
        self.actionSave = QAction(icons.disk, "Save", self)
        self.actionHome.triggered.connect(self._chart_toolbar.home)
        self.actionBack.triggered.connect(self._chart_toolbar.back)
        self.actionForward.triggered.connect(self._chart_toolbar.forward)
        self.actionPan.triggered.connect(self._chart_toolbar.pan)
        self.actionZoom.triggered.connect(self._chart_toolbar.zoom)
        self.actionSubplots.triggered.connect(self._chart_toolbar.configure_subplots)
        self.actionCustomize.triggered.connect(self._chart_toolbar.edit_parameters)
        self.actionSave.triggered.connect(self._chart_toolbar.save_figure)
        self.actionPan.setCheckable(True)
        self.actionZoom.setCheckable(True)
        self.homeToolButton.setDefaultAction(self.actionHome)
        self.backToolButton.setDefaultAction(self.actionBack)
        self.forwardToolButton.setDefaultAction(self.actionForward)
        self.panToolButton.setDefaultAction(self.actionPan)
        self.zoomToolButton.setDefaultAction(self.actionZoom)
        self.subplotsToolButton.setDefaultAction(self.actionSubplots)
        self.customizeToolButton.setDefaultAction(self.actionCustomize)
        self.saveToolButton.setDefaultAction(self.actionSave)
        self.exchangeRateHistoryChartVerticalLayout.addWidget(self._chart)

    def load_chart_data(self, x: Collection, y: Collection) -> None:
        self._chart.axes.clear()
        self._chart.axes.plot(x, y)
        self._chart.axes.grid(visible=True)
        self._chart.axes.figure.autofmt_xdate()
        self._chart.draw()
        self._chart_toolbar.update()
        self.update_history_table_width()

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

    def show_form(self) -> None:
        super().show_form()
        self.update_table_widths()

    def update_table_widths(self) -> None:
        self.currencyTable.resizeColumnsToContents()
        self.exchangeRateTable.resizeColumnsToContents()

        currency_table_width = self._calculate_table_width(self.currencyTable)
        exchange_rate_table_width = self._calculate_table_width(self.exchangeRateTable)
        larger_width = max(currency_table_width, exchange_rate_table_width)

        self.currencyGroupBox.setFixedWidth(larger_width + 30)
        self.exchangeRateGroupBox.setFixedWidth(larger_width + 30)

        self.currencyTable.horizontalHeader().setSectionResizeMode(
            CurrencyTableColumn.PLACES,
            QHeaderView.ResizeMode.Stretch,
        )
        self.exchangeRateTable.horizontalHeader().setSectionResizeMode(
            ExchangeRateTableColumn.LAST_DATE,
            QHeaderView.ResizeMode.Stretch,
        )

        self.update_history_table_width()

    def update_history_table_width(self) -> None:
        self.exchangeRateHistoryTable.resizeColumnsToContents()
        exchange_rate_history_table_width = self._calculate_table_width(
            self.exchangeRateHistoryTable
        )
        self.exchangeRateHistoryTable.setFixedWidth(
            exchange_rate_history_table_width + 10
        )

    @staticmethod
    def _calculate_table_width(table: QTableView) -> int:
        return table.horizontalHeader().length() + table.verticalHeader().width()
