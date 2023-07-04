from collections.abc import Collection

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.record_keeper import RecordKeeper
from src.models.statistics.category_stats import (
    calculate_average_per_month_category_stats,
    calculate_category_stats,
    calculate_monthly_category_stats,
    calculate_monthly_totals_and_averages,
)
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.view_models.periodic_category_stats_tree_model import (
    PeriodicCategoryStatsTreeModel,
)
from src.views.main_view import MainView
from src.views.reports.category_periodic_report import CategoryPeriodicReport
from src.views.reports.category_report import CategoryReport


class CategoryReportPresenter:
    def __init__(
        self,
        main_view: MainView,
        transactions_presenter: TransactionsPresenter,
        record_keeper: RecordKeeper,
    ) -> None:
        self._main_view = main_view
        self._transactions_presenter = transactions_presenter
        self._record_keeper = record_keeper
        self._connect_to_view_signals()

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._record_keeper = record_keeper

    def _connect_to_view_signals(self) -> None:
        self._main_view.signal_category_total_report.connect(self._create_total_report)
        self._main_view.signal_category_average_per_month_report.connect(
            self._create_average_per_month_report
        )
        self._main_view.signal_category_monthly_report.connect(
            self._create_monthly_report
        )

    def _create_total_report(self) -> None:
        transactions = self._transactions_presenter.get_visible_transactions()
        transactions = _filter_transactions(transactions)
        base_currency = self._record_keeper.base_currency
        stats = calculate_category_stats(
            transactions, base_currency, self._record_keeper.categories
        )
        self.report = CategoryReport("Total", self._main_view)
        self.report.finalize_setup()
        self.report.load_stats(stats)
        self.report.show_form()

    def _create_average_per_month_report(self) -> None:
        transactions = self._transactions_presenter.get_visible_transactions()
        transactions = _filter_transactions(transactions)
        base_currency = self._record_keeper.base_currency
        stats_per_month = calculate_monthly_category_stats(
            transactions, base_currency, self._record_keeper.categories
        )
        stats = calculate_average_per_month_category_stats(stats_per_month)
        self.report = CategoryReport("Average Per Month", self._main_view)
        self.report.finalize_setup()
        self.report.load_stats(stats)
        self.report.show_form()

    def _create_monthly_report(self) -> None:
        transactions = self._transactions_presenter.get_visible_transactions()
        transactions = _filter_transactions(transactions)
        base_currency = self._record_keeper.base_currency
        stats_per_month = calculate_monthly_category_stats(
            transactions,
            base_currency,
            self._record_keeper.categories,
            period_format="%b %Y",
        )
        income_stats_per_month = {}
        expense_stats_per_month = {}
        for period, stats in stats_per_month.items():
            income_stats = []
            expense_stats = []
            for item in stats:
                if item.balance.value_rounded > 0:
                    income_stats.append(item)
                elif item.balance.value_rounded < 0:
                    expense_stats.append(item)
            income_stats_per_month[period] = income_stats
            expense_stats_per_month[period] = expense_stats

        (
            income_month_totals,
            income_category_averages,
            income_category_totals,
        ) = calculate_monthly_totals_and_averages(income_stats_per_month)
        (
            expense_month_totals,
            expense_category_averages,
            expense_category_totals,
        ) = calculate_monthly_totals_and_averages(expense_stats_per_month)

        self.report = CategoryPeriodicReport(
            "Category Report - Monthly", self._main_view
        )

        self._proxy_income = QSortFilterProxyModel(self.report)
        self._model_income = PeriodicCategoryStatsTreeModel(
            self.report.incomeTreeView, self._proxy_income
        )
        self._model_income.load_periodic_category_stats(
            income_stats_per_month,
            income_month_totals,
            income_category_averages,
            income_category_totals,
        )
        self._proxy_income.setSourceModel(self._model_income)
        self._proxy_income.setSortRole(Qt.ItemDataRole.UserRole)
        self.report.incomeTreeView.setModel(self._proxy_income)
        self.report.incomeTreeView.sortByColumn(
            self._model_income.columnCount() - 2, Qt.SortOrder.DescendingOrder
        )

        self._proxy_expense = QSortFilterProxyModel(self.report)
        self._model_expense = PeriodicCategoryStatsTreeModel(
            self.report.expenseTreeView, self._proxy_expense
        )
        self._model_expense.load_periodic_category_stats(
            expense_stats_per_month,
            expense_month_totals,
            expense_category_averages,
            expense_category_totals,
        )
        self._proxy_expense.setSourceModel(self._model_expense)
        self._proxy_expense.setSortRole(Qt.ItemDataRole.UserRole)
        self.report.expenseTreeView.setModel(self._proxy_expense)
        self.report.expenseTreeView.sortByColumn(
            self._model_expense.columnCount() - 2, Qt.SortOrder.AscendingOrder
        )

        self.report.finalize_setup()
        self.report.show_form()


def _filter_transactions(
    transactions: Collection[Transaction],
) -> tuple[CashTransaction | RefundTransaction]:
    return tuple(
        transaction
        for transaction in transactions
        if isinstance(transaction, CashTransaction | RefundTransaction)
    )
