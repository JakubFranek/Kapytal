from collections.abc import Collection
from typing import Literal

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QHeaderView, QWidget
from src.models.model_objects.attributes import Category
from src.models.statistics.category_stats import CategoryStats
from src.view_models.category_tree_model import CategoryTreeModel
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.constants import CategoryTreeColumn
from src.views.ui_files.reports.Ui_category_report import Ui_CategoryReport
from src.views.widgets.charts.pie_chart_widget import PieChartWidget


class CategoryReport(CustomWidget, Ui_CategoryReport):
    def __init__(
        self,
        type_: Literal["Total", "Average Per Month"],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        # BUG: figure out why this is needed at all
        font = self.font()
        font_size = font.pointSize()
        tree_font = self.incomeTreeView.font()
        tree_font.setPointSize(font_size)
        self.incomeTreeView.setFont(tree_font)
        self.expenseTreeView.setFont(tree_font)

        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle(f"Category Report - {type_}")
        self.setWindowIcon(icons.bar_chart)

        self.income_chart_widget = PieChartWidget(self)
        self.expense_chart_widget = PieChartWidget(self)
        self.incomeTabHorizontalLayout.addWidget(self.income_chart_widget)
        self.expenseTabHorizontalLayout.addWidget(self.expense_chart_widget)
        self.incomeTabHorizontalLayout.setStretch(0, 0)
        self.incomeTabHorizontalLayout.setStretch(1, 1)
        self.expenseTabHorizontalLayout.setStretch(0, 0)
        self.expenseTabHorizontalLayout.setStretch(1, 1)

        self._income_proxy = QSortFilterProxyModel(self)
        self._income_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._income_proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._income_model = CategoryTreeModel(self.incomeTreeView, self._income_proxy)
        self._income_proxy.setSourceModel(self._income_model)
        self.incomeTreeView.setModel(self._income_proxy)
        self.incomeTreeView.header().setSortIndicatorClearable(True)

        self._expense_proxy = QSortFilterProxyModel(self)
        self._expense_proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._expense_proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._expense_model = CategoryTreeModel(
            self._expense_proxy, self._expense_proxy
        )
        self._expense_proxy.setSourceModel(self._expense_model)
        self.expenseTreeView.setModel(self._expense_proxy)
        self.expenseTreeView.header().setSortIndicatorClearable(True)

    def load_stats(
        self,
        stats: dict[Category, CategoryStats],
    ) -> None:
        income_stats = {
            category: stats
            for category, stats in stats.items()
            if stats.balance.is_positive()
        }
        flat_income_categories = [category for category, _ in income_stats.items()]
        expense_stats = {
            category: stats
            for category, stats in stats.items()
            if stats.balance.is_negative()
        }
        flat_expense_categories = [category for category, _ in expense_stats.items()]

        self._income_model.pre_reset_model()
        self._income_model.load_data(flat_income_categories, income_stats)
        self._income_model.post_reset_model()
        self._expense_model.pre_reset_model()
        self._expense_model.load_data(flat_expense_categories, expense_stats)
        self._expense_model.post_reset_model()
        self.incomeTreeView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)
        self.expenseTreeView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)

    def finalize_setup(self) -> None:
        self.incomeTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.incomeTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.TRANSACTIONS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.incomeTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.BALANCE,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.expenseTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.NAME,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.expenseTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.TRANSACTIONS,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.expenseTreeView.header().setSectionResizeMode(
            CategoryTreeColumn.BALANCE,
            QHeaderView.ResizeMode.ResizeToContents,
        )
