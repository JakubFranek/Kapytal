from collections.abc import Collection
from typing import Literal

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QHeaderView, QWidget
from src.models.statistics.attribute_stats import AttributeStats
from src.view_models.attribute_table_model import AttributeTableModel
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.constants import AttributeTableColumn
from src.views.ui_files.reports.Ui_attribute_report import Ui_AttributeReport
from src.views.widgets.charts.pie_chart_widget import PieChartWidget


class AttributeReport(CustomWidget, Ui_AttributeReport):
    def __init__(
        self,
        type_: Literal["Total", "Average Per Month"],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle(f"Tag Report - {type_}")
        self.setWindowIcon(icons.bar_chart)

        self.income_chart_widget = PieChartWidget(self)
        self.expense_chart_widget = PieChartWidget(self)
        self.incomeTabVerticalLayout.addWidget(self.income_chart_widget)
        self.expenseTabVerticalLayout.addWidget(self.expense_chart_widget)

        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy_model.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._table_model = AttributeTableModel(self.tableView, self._proxy_model)
        self._proxy_model.setSourceModel(self._table_model)
        self.tableView.setModel(self._proxy_model)

    def load_stats(self, stats: Collection[AttributeStats]) -> None:
        self._table_model.pre_reset_model()
        self._table_model.load_attribute_stats(stats)
        self._table_model.post_reset_model()
        self.tableView.resizeColumnsToContents()
        self.tableView.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        income_stats = [stats for stats in stats if stats.balance.is_positive()]
        expense_stats = [stats for stats in stats if stats.balance.is_negative()]

        income_sizes = [stats.balance.value_rounded for stats in income_stats]
        income_labels = [stats.attribute.name for stats in income_stats]
        expense_sizes = [-stats.balance.value_rounded for stats in expense_stats]
        expense_labels = [stats.attribute.name for stats in expense_stats]

        self.income_chart_widget.load_data(income_sizes, income_labels)
        self.expense_chart_widget.load_data(expense_sizes, expense_labels)

    def finalize_setup(self) -> None:
        self.tableView.horizontalHeader().setSectionResizeMode(
            AttributeTableColumn.NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            AttributeTableColumn.TRANSACTIONS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            AttributeTableColumn.BALANCE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
