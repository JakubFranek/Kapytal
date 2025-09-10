from collections.abc import Collection
from enum import Enum, auto
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor
from PyQt6.QtWidgets import QApplication, QHeaderView, QLineEdit, QMenu, QWidget
from src.models.model_objects.attributes import AttributeType
from src.models.statistics.attribute_stats import AttributeStats
from src.views import colors, icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.ui_files.reports.Ui_attribute_report import (
    Ui_AttributeReport,
)
from src.views.widgets.charts.pie_chart_view import PieChartView

if TYPE_CHECKING:
    from src.models.model_objects.currency_objects import Currency


class StatsType(Enum):
    INCOME = auto()
    EXPENSE = auto()


class AttributeReport(CustomWidget, Ui_AttributeReport):
    signal_selection_changed = pyqtSignal()
    signal_show_transactions = pyqtSignal()
    signal_recalculate_report = pyqtSignal()
    signal_pie_slice_clicked = pyqtSignal(str)
    signal_search_text_changed = pyqtSignal(str)

    def __init__(
        self,
        title: str,
        currency_code: str,
        attribute_type: AttributeType,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle(title)
        if attribute_type == AttributeType.TAG:
            self.setWindowIcon(icons.tag)
        else:
            self.setWindowIcon(icons.payee)
        self.currencyNoteLabel.setText(f"All values in {currency_code}")

        self.chart_view = PieChartView(self, clickable_slices=True)
        self.chartVerticalLayout.addWidget(self.chart_view)

        self.typeComboBox.addItem("Income")
        self.typeComboBox.addItem("Expense")
        self.typeComboBox.setCurrentText("Income")
        self.typeComboBox.currentTextChanged.connect(self._combobox_text_changed)

        self.periodComboBox.currentTextChanged.connect(self._combobox_text_changed)

        self.actionShow_Hide_Period_Columns.setIcon(icons.calendar)
        self.actionShow_Hide_Period_Columns.triggered.connect(self._show_hide_periods)
        self.actionShow_Hide_Period_Columns.setCheckable(True)
        self.actionShow_Hide_Period_Columns.setChecked(True)
        self.showHidePeriodColumnsToolButton.setDefaultAction(
            self.actionShow_Hide_Period_Columns
        )

        self.actionShow_Transactions.setIcon(icons.table)
        self.actionShow_Transactions.triggered.connect(
            self.signal_show_transactions.emit
        )
        self.showTransactionsToolButton.setDefaultAction(self.actionShow_Transactions)

        self.actionRecalculate_Report.setIcon(icons.refresh)
        self.actionRecalculate_Report.setEnabled(False)
        self.actionRecalculate_Report.triggered.connect(self.signal_recalculate_report)

        self.recalculateReportToolButton.setDefaultAction(self.actionRecalculate_Report)

        self.tableView.contextMenuEvent = self._create_context_menu
        self.tableView.doubleClicked.connect(self._table_view_double_clicked)

        self.chart_view.signal_slice_clicked.connect(self.signal_pie_slice_clicked.emit)

        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed)
        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )

    @property
    def stats_type(self) -> StatsType:
        if self.typeComboBox.currentText() == "Income":
            return StatsType.INCOME
        return StatsType.EXPENSE

    @property
    def period(self) -> str:
        return self.periodComboBox.currentText()

    def finalize_setup(self) -> None:
        for column in range(self.tableView.model().columnCount()):
            self.tableView.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )
        self.tableView.selectionModel().selectionChanged.connect(
            self.signal_selection_changed
        )

    def show_form(self) -> None:
        super().show_form()
        width = self.splitter.size().width()
        self.splitter.setSizes([width // 2, width // 2])

    def load_stats(
        self,
        income_periodic_stats: dict[str, Collection[AttributeStats]],
        expense_periodic_stats: dict[str, Collection[AttributeStats]],
    ) -> None:
        self._income_periodic_stats = income_periodic_stats
        self._expense_periodic_stats = expense_periodic_stats

        periods = list(income_periodic_stats.keys())
        self._setup_comboboxes(periods)

    def set_recalculate_report_action_state(self, *, enabled: bool) -> None:
        self.actionRecalculate_Report.setEnabled(enabled)
        if enabled:
            self.recalculateReportToolButton.setToolButtonStyle(
                Qt.ToolButtonStyle.ToolButtonTextBesideIcon
            )
        else:
            self.actionRecalculate_Report.setIcon(Qt.ToolButtonStyle.ToolButtonIconOnly)

    def set_show_transactions_action_state(self, *, enable: bool) -> None:
        self.actionShow_Transactions.setEnabled(enable)

    def _setup_comboboxes(self, periods: Collection[str]) -> None:
        with QSignalBlocker(self.periodComboBox):
            for period in periods:
                self.periodComboBox.addItem(period)
        self.periodComboBox.setCurrentText(periods[-1])

    def _combobox_text_changed(self) -> None:
        type_ = self.typeComboBox.currentText()
        selected_period = self.periodComboBox.currentText()
        _periodic_stats = (
            self._income_periodic_stats
            if type_ == "Income"
            else self._expense_periodic_stats
        )

        data = [
            (abs(item.balance.value_rounded), item.attribute.name)
            for item in _periodic_stats[selected_period]
        ]
        try:
            currency: Currency = _periodic_stats[selected_period][0].balance.currency
            decimals = currency.decimals
            currency_code = currency.code
        except IndexError:
            decimals = 0
            currency_code = ""

        color = (
            colors.ColorRanges.GREEN if type_ == "Income" else colors.ColorRanges.RED
        )

        self.chart_view.load_data(data, decimals, currency_code, color)

    def _show_hide_periods(self) -> None:
        state = self.actionShow_Hide_Period_Columns.isChecked()
        message = "Showing " if state else "Hiding "
        self._busy_dialog = create_simple_busy_indicator(
            self, message + "columns, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            if state:
                for column in range(self.tableView.model().columnCount() - 2):
                    self.tableView.showColumn(column)
            else:
                for column in range(self.tableView.model().columnCount() - 2):
                    self.tableView.hideColumn(column)
        except:  # noqa: TRY203
            raise
        finally:
            self._busy_dialog.close()

    def _create_context_menu(self, event: QContextMenuEvent) -> None:  # noqa: ARG002
        self.menu = QMenu(self)
        self.menu.addAction(self.actionShow_Transactions)
        self.menu.popup(QCursor.pos())

    def _table_view_double_clicked(self) -> None:
        if self.actionShow_Transactions.isEnabled():
            self.signal_show_transactions.emit()
