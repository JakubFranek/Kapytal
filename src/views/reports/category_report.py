from collections import defaultdict
from collections.abc import Collection, Sequence
from enum import Enum, auto

from PyQt6.QtCore import QSignalBlocker, Qt, pyqtSignal
from PyQt6.QtGui import QContextMenuEvent, QCursor
from PyQt6.QtWidgets import (
    QApplication,
    QHeaderView,
    QLineEdit,
    QMenu,
    QWidget,
)
from src.models.model_objects.currency_objects import CashAmount, Currency
from src.models.statistics.category_stats import CategoryStats
from src.views import colors, icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.ui_files.reports.Ui_category_report import Ui_CategoryReport
from src.views.widgets.charts.stacked_bar_chart_view import (
    DataSeries,
    StackedBarChartView,
)
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
    signal_search_text_changed = pyqtSignal(str)

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

        background = colors.get_tab_widget_background()

        self.sunburst_chart_view = SunburstChartView(
            self, clickable_slices=True, background_color=background
        )
        self.sunburstChartTab.layout().addWidget(self.sunburst_chart_view)

        self.bar_chart_view = StackedBarChartView(self, background_color=background)
        self.barChartTab.layout().addWidget(self.bar_chart_view)

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

        self.sunburstTypeComboBox.addItem("Income")
        self.sunburstTypeComboBox.addItem("Expense")
        self.sunburstTypeComboBox.setCurrentText("Income")
        self.sunburstTypeComboBox.currentTextChanged.connect(
            self._sunburst_combobox_text_changed
        )

        self.barTypeComboBox.addItem("Income")
        self.barTypeComboBox.addItem("Expense")
        self.barTypeComboBox.setCurrentText("Income")
        self.barTypeComboBox.currentTextChanged.connect(self._bar_combobox_text_changed)

        self.periodComboBox.currentTextChanged.connect(
            self._sunburst_combobox_text_changed
        )

        self.treeView.contextMenuEvent = self._create_context_menu
        self.treeView.doubleClicked.connect(self._tree_view_double_clicked)

        self.sunburst_chart_view.signal_slice_clicked.connect(
            self.signal_sunburst_slice_clicked
        )

        self.searchLineEdit.textChanged.connect(self.signal_search_text_changed)
        self.searchLineEdit.addAction(
            icons.magnifier, QLineEdit.ActionPosition.LeadingPosition
        )

    @property
    def stats_type(self) -> StatsType:
        if self.sunburstTypeComboBox.currentText() == "Income":
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
        base_currency: Currency,
    ) -> None:
        self._income_periodic_stats = income_periodic_stats
        self._expense_periodic_stats = expense_periodic_stats
        self._base_currency = base_currency

        periods = tuple(income_periodic_stats.keys())
        self._setup_sunburst_combobox(periods)

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

    def _setup_sunburst_combobox(self, periods: Collection[str]) -> None:
        with QSignalBlocker(self.periodComboBox):
            for period in periods:
                self.periodComboBox.addItem(period)
        self.periodComboBox.setCurrentText(periods[-1])

    def _sunburst_combobox_text_changed(self) -> None:
        type_ = self.sunburstTypeComboBox.currentText()
        data = (
            self._income_periodic_stats
            if type_ == "Income"
            else self._expense_periodic_stats
        )
        selected_period = self.periodComboBox.currentText()
        sunburst_data = _convert_category_stats_to_sunburst_data(
            data[selected_period], self._base_currency
        )
        self.sunburst_chart_view.load_data(sunburst_data)

    def _bar_combobox_text_changed(self) -> None:
        type_ = self.barTypeComboBox.currentText()
        data = (
            self._income_periodic_stats
            if type_ == "Income"
            else self._expense_periodic_stats
        )
        bar_data = _convert_category_stats_to_bar_data(data)
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
                for column in range(1, self.treeView.model().columnCount() - 2):
                    self.treeView.showColumn(column)
            else:
                for column in range(1, self.treeView.model().columnCount() - 2):
                    self.treeView.hideColumn(column)
        except:  # noqa: TRY203
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
    stats: Sequence[CategoryStats], currency: Currency
) -> tuple[SunburstNode]:
    balance = 0.0
    level = 1

    children: list[SunburstNode] = []
    root_node = SunburstNode(
        "Total", "Total", 0, currency.code, currency.decimals, [], None
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


def _convert_category_stats_to_bar_data(
    stats: dict[str, Sequence[CategoryStats]],
) -> tuple[DataSeries]:
    period_names = tuple(key for key in stats if key not in {"Total", "Average"})
    if not period_names:
        return ()
    currency = stats[period_names[0]][0].balance.currency

    periodic_category_order: dict[str, list[str]] = {}

    for period, stats_sequence in stats.items():
        stats_list = list(stats_sequence)
        if period not in period_names:
            continue
        stats_list.sort(key=lambda x: abs(x.balance.value_normalized), reverse=True)
        sorted_category_names = [
            t.category.name for t in stats_list if t.category.parent is None
        ]
        periodic_category_order[period] = sorted_category_names

    category_names: set[str] = set()
    for _category_names in periodic_category_order.values():
        for category_name in _category_names:
            category_names.add(category_name)

    category_order_sum: defaultdict[str, int] = defaultdict(int)
    for category_name in category_names:
        for _category_names in periodic_category_order.values():
            try:
                category_order_sum[category_name] += _category_names.index(
                    category_name
                )
            except ValueError:
                category_order_sum[category_name] += len(_category_names)

    sorted_category_names = [
        t[0] for t in sorted(category_order_sum.items(), key=lambda x: x[1])
    ]

    data_series: list[DataSeries] = []
    for category_name in sorted_category_names:
        data_series_item = DataSeries(category_name, [])
        for period, stats_sequence in stats.items():
            value_added = False
            if period not in period_names:
                continue
            for stats_item in stats_sequence:
                if stats_item.category.name == category_name:
                    data_series_item.values.append(stats_item.balance)
                    value_added = True
                    break
            if value_added:
                continue
            data_series_item.values.append(CashAmount(0, currency=currency))
        data_series.append(data_series_item)

    return tuple(data_series)


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

    # this is needed because CategoryStats can report a different number than
    # the sum of children (due to refunds), as children are pre-separated by whether
    # they are positive or negative but CategoryStats sum all balances together
    node.value = max(node.value, child_value_sum)
    node.children.sort(key=lambda x: abs(x.value), reverse=True)
    return node
