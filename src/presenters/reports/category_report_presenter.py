from collections.abc import Collection

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.record_keeper import RecordKeeper
from src.models.statistics.category_stats import (
    calculate_average_per_month_category_stats,
    calculate_category_stats,
    calculate_monthly_category_stats,
)
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.views.main_view import MainView
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


def _filter_transactions(
    transactions: Collection[Transaction],
) -> tuple[CashTransaction | RefundTransaction]:
    return tuple(
        transaction
        for transaction in transactions
        if isinstance(transaction, CashTransaction | RefundTransaction)
    )
