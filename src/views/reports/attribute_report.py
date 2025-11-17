from collections import defaultdict
from collections.abc import Collection, Sequence
from enum import Enum, auto
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor
from PyQt6.QtWidgets import QApplication, QHeaderView, QLineEdit, QMenu, QWidget
from src.models.model_objects.attributes import AttributeType
from src.models.model_objects.currency_objects import CashAmount
from src.models.statistics.attribute_stats import AttributeStats
from src.views import colors, icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.ui_files.reports.Ui_attribute_report import (
    Ui_AttributeReport,
)
from src.views.widgets.charts.pie_chart_view import PieChartView
from src.views.widgets.charts.stacked_bar_chart_view import (
    DataSeries,
    StackedBarChartView,
)

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
    signal_bar_clicked = pyqtSignal(str, str)
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

        background = colors.get_tab_widget_background()

        self.pie_chart_view = PieChartView(
            self, clickable_slices=True, background_color=background
        )
        self.pieTab.layout().addWidget(self.pie_chart_view)

        self.bar_chart_view = StackedBarChartView(self, background_color=background)
        self.barTab.layout().addWidget(self.bar_chart_view)

        self.pieTypeComboBox.addItem("Income")
        self.pieTypeComboBox.addItem("Expense")
        self.pieTypeComboBox.setCurrentText("Income")
        self.pieTypeComboBox.currentTextChanged.connect(self._pie_combobox_text_changed)

        self.piePeriodComboBox.currentTextChanged.connect(
            self._pie_combobox_text_changed
        )

        self.barTypeComboBox.addItem("Income")
        self.barTypeComboBox.addItem("Expense")
        self.barTypeComboBox.setCurrentText("Income")
        self.barTypeComboBox.currentTextChanged.connect(self._bar_combobox_text_changed)

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

        self.pie_chart_view.signal_slice_clicked.connect(
            self.signal_pie_slice_clicked.emit
        )

        self.bar_chart_view.signal_bar_clicked.connect(self.signal_bar_clicked.emit)

        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed)
        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )

    @property
    def pie_stats_type(self) -> StatsType:
        if self.pieTypeComboBox.currentText() == "Income":
            return StatsType.INCOME
        return StatsType.EXPENSE

    @property
    def pie_period(self) -> str:
        return self.piePeriodComboBox.currentText()

    @property
    def bar_stats_type(self) -> StatsType:
        if self.barTypeComboBox.currentText() == "Income":
            return StatsType.INCOME
        return StatsType.EXPENSE

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
        self._setup_pie_comboboxes(periods)
        # Updates bar chart without user needing to update combobox manually
        self._bar_combobox_text_changed()

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

    def _setup_pie_comboboxes(self, periods: Collection[str]) -> None:
        with QSignalBlocker(self.piePeriodComboBox):
            for period in periods:
                self.piePeriodComboBox.addItem(period)
        self.piePeriodComboBox.setCurrentText(periods[-1])

    def _pie_combobox_text_changed(self) -> None:
        type_ = self.pieTypeComboBox.currentText()
        selected_period = self.piePeriodComboBox.currentText()
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

        self.pie_chart_view.load_data(data, decimals, currency_code, color)

    def _bar_combobox_text_changed(self) -> None:
        type_ = self.barTypeComboBox.currentText()
        data = (
            self._income_periodic_stats
            if type_ == "Income"
            else self._expense_periodic_stats
        )
        bar_data = _convert_attribute_stats_to_bar_data(data)
        period_names = (key for key in data if key not in {"Total", "Average"})
        self.bar_chart_view.load_data(bar_data, period_names=period_names)

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


def _convert_attribute_stats_to_bar_data(
    stats: dict[str, Sequence[AttributeStats]],
) -> tuple[DataSeries]:
    period_names = tuple(key for key in stats if key not in {"Total", "Average"})
    if not period_names:
        return ()
    try:
        currency = stats[period_names[0]][0].balance.currency
    except IndexError:
        return ()

    periodic_attribute_order: dict[str, list[str]] = {}

    for period, stats_sequence in stats.items():
        stats_list = list(stats_sequence)
        if period not in period_names:
            continue
        stats_list.sort(key=lambda x: abs(x.balance.value_normalized), reverse=True)
        periodic_attribute_order[period] = [
            attribute_stats.attribute.name for attribute_stats in stats_list
        ]

    attribute_names: set[str] = set()
    for _attribute_names in periodic_attribute_order.values():
        for attribute_name in _attribute_names:
            attribute_names.add(attribute_name)

    attribute_order_sum: defaultdict[str, int] = defaultdict(int)
    for attribute_name in attribute_names:
        for _attribute_names in periodic_attribute_order.values():
            try:
                attribute_order_sum[attribute_name] += _attribute_names.index(
                    attribute_name
                )
            except ValueError:
                attribute_order_sum[attribute_name] += len(_attribute_names)

    sorted_attribute_names = [
        t[0] for t in sorted(attribute_order_sum.items(), key=lambda x: x[1])
    ]

    data_series: list[DataSeries] = []
    for attribute_name in sorted_attribute_names:
        data_series_item = DataSeries(attribute_name, [])
        for period, stats_sequence in stats.items():
            value_added = False
            if period not in period_names:
                continue
            for stats_item in stats_sequence:
                if stats_item.attribute.name == attribute_name:
                    data_series_item.values.append(abs(stats_item.balance))
                    value_added = True
                    break
            if value_added:
                continue
            data_series_item.values.append(CashAmount(0, currency=currency))
        data_series.append(data_series_item)

    return tuple(data_series)
