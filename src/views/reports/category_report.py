from collections.abc import Collection, Sequence
from enum import Enum, auto

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor
from PyQt6.QtWidgets import (
    QApplication,
    QHeaderView,
    QMenu,
    QWidget,
)
from src.models.statistics.category_stats import CategoryStats
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.ui_files.reports.Ui_category_report import Ui_CategoryReport
from src.views.widgets.charts.sunburst_chart_view import (
    SunburstChartView,
    SunburstNode,
)


class StatsType(Enum):
    INCOME = auto()
    EXPENSE = auto()


class CategoryReport(CustomWidget, Ui_CategoryReport):
    signal_show_transactions = pyqtSignal()
    signal_recalculate_report = pyqtSignal()
    signal_selection_changed = pyqtSignal()
    signal_sunburst_slice_clicked = pyqtSignal(str)

    def __init__(
        self,
        title: str,
        currency_code: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle(title)
        self.setWindowIcon(icons.category)
        self.currencyNoteLabel.setText(f"All values in {currency_code}")

        self.chart_view = SunburstChartView(self, clickable_slices=True)
        self.chartVerticalLayout.addWidget(self.chart_view)

        self.actionExpand_All.setIcon(icons.expand)
        self.actionCollapse_All.setIcon(icons.collapse)
        self.actionShow_Hide_Period_Columns.setIcon(icons.calendar)
        self.actionShow_Transactions.setIcon(icons.table)
        self.actionRecalculate_Report.setIcon(icons.refresh)

        self.actionExpand_All.triggered.connect(self.treeView.expandAll)
        self.actionCollapse_All.triggered.connect(self.treeView.collapseAll)
        self.actionShow_Hide_Period_Columns.triggered.connect(self._show_hide_periods)
        self.actionShow_Transactions.triggered.connect(
            self.signal_show_transactions.emit
        )
        self.actionRecalculate_Report.triggered.connect(self.signal_recalculate_report)

        self.actionShow_Hide_Period_Columns.setCheckable(True)
        self.actionShow_Hide_Period_Columns.setChecked(True)
        self.actionRecalculate_Report.setEnabled(False)

        self.expandAllToolButton.setDefaultAction(self.actionExpand_All)
        self.collapseAllToolButton.setDefaultAction(self.actionCollapse_All)
        self.hidePeriodsToolButton.setDefaultAction(self.actionShow_Hide_Period_Columns)
        self.recalculateReportToolButton.setDefaultAction(self.actionRecalculate_Report)
        self.showTransactionsToolButton.setDefaultAction(self.actionShow_Transactions)

        self.typeComboBox.addItem("Income")
        self.typeComboBox.addItem("Expense")
        self.typeComboBox.setCurrentText("Income")
        self.typeComboBox.currentTextChanged.connect(self._combobox_text_changed)

        self.periodComboBox.currentTextChanged.connect(self._combobox_text_changed)

        self.treeView.contextMenuEvent = self._create_context_menu
        self.treeView.doubleClicked.connect(self._tree_view_double_clicked)

        self.chart_view.signal_slice_clicked.connect(self.signal_sunburst_slice_clicked)

    @property
    def stats_type(self) -> StatsType:
        if self.typeComboBox.currentText() == "Income":
            return StatsType.INCOME
        return StatsType.EXPENSE

    @property
    def period(self) -> str:
        return self.periodComboBox.currentText()

    def finalize_setup(self) -> None:
        for column in range(self.treeView.model().columnCount()):
            self.treeView.header().setSectionResizeMode(
                column, QHeaderView.ResizeMode.ResizeToContents
            )
        self.treeView.selectionModel().selectionChanged.connect(
            self.signal_selection_changed
        )

    def show_form(self) -> None:
        super().show_form()
        width = self.splitter.size().width()
        self.splitter.setSizes([width // 2, width // 2])

    def load_stats(
        self,
        income_periodic_stats: dict[str, Sequence[CategoryStats]],
        expense_periodic_stats: dict[str, Sequence[CategoryStats]],
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
        data = (
            self._income_periodic_stats
            if type_ == "Income"
            else self._expense_periodic_stats
        )
        selected_period = self.periodComboBox.currentText()
        sunburst_data = _convert_category_stats_to_sunburst_data(data[selected_period])
        self.chart_view.load_data(sunburst_data)

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
                for column in range(1, self.treeView.model().columnCount() - 2):
                    self.treeView.showColumn(column)
            else:
                for column in range(1, self.treeView.model().columnCount() - 2):
                    self.treeView.hideColumn(column)
        except:  # noqa: TRY302
            raise
        finally:
            self._busy_dialog.close()

    def _create_context_menu(self, event: QContextMenuEvent) -> None:  # noqa: ARG002
        self.menu = QMenu(self)
        self.menu.addAction(self.actionShow_Transactions)
        self.menu.popup(QCursor.pos())

    def _tree_view_double_clicked(self) -> None:
        if self.actionShow_Transactions.isEnabled():
            self.signal_show_transactions.emit()


def _convert_category_stats_to_sunburst_data(
    stats: Sequence[CategoryStats],
) -> tuple[SunburstNode]:
    balance = 0.0
    level = 1

    try:
        currency = stats[0].balance.currency
        currency_code = currency.code
        currency_places = currency.places
    except IndexError:
        currency_code = ""
        currency_places = 0

    children: list[SunburstNode] = []
    root_node = SunburstNode(
        "Total", "Total", 0, currency_code, currency_places, [], None
    )
    for item in stats:
        if item.category.parent is not None:
            continue
        node = _create_node(item, stats, level + 1, root_node)
        balance += node.value
        children.append(node)
    children.sort(key=lambda x: abs(x.value), reverse=True)
    root_node.children = children
    root_node.value = balance
    return (root_node,)


def _create_node(
    stats: CategoryStats,
    all_stats: Collection[CategoryStats],
    level: int,
    parent: SunburstNode,
) -> SunburstNode:
    node = SunburstNode(
        stats.category.name,
        stats.category.path,
        abs(float(stats.balance.value_rounded)),
        parent.unit,
        parent.decimals,
        [],
        parent,
    )

    for item in all_stats:
        if item.category in stats.category.children:
            child_node = _create_node(item, all_stats, level + 1, node)
            node.children.append(child_node)
    child_value_sum = sum(child.value for child in node.children)
    if child_value_sum > node.value:
        node.value = child_value_sum
    node.children.sort(key=lambda x: abs(x.value), reverse=True)
    return node
