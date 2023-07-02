from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.record_keeper import RecordKeeper
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.utilities.calculation import (
    calculate_average_per_month_tag_stats,
    calculate_tag_stats,
)
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.views.main_view import MainView
from src.views.reports.tag_report import TagReport


class TagReportPresenter:
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
        self._main_view.signal_tag_total_report.connect(self._create_tag_total_report)
        self._main_view.signal_tag_average_per_month_report.connect(
            self._create_tag_average_per_month_report
        )

    def _create_tag_total_report(self) -> None:
        transactions = self._transactions_presenter.get_visible_transactions()
        transactions = [
            transaction
            for transaction in transactions
            if isinstance(transaction, CashTransaction | RefundTransaction)
        ]
        base_currency = self._record_keeper.base_currency
        tag_stats = calculate_tag_stats(
            transactions, base_currency, self._record_keeper.tags
        )
        self.report = TagReport("Total", self._main_view)
        self.report.finalize_setup()
        self.report.load_stats(tag_stats.values())
        self.report.show_form()

    def _create_tag_average_per_month_report(self) -> None:
        transactions = self._transactions_presenter.get_visible_transactions()
        transactions = [
            transaction
            for transaction in transactions
            if isinstance(transaction, CashTransaction | RefundTransaction)
        ]
        base_currency = self._record_keeper.base_currency
        tag_stats = calculate_average_per_month_tag_stats(
            transactions, base_currency, self._record_keeper.tags
        )
        self.report = TagReport("Average Per Month", self._main_view)
        self.report.finalize_setup()
        self.report.load_stats(tag_stats)
        self.report.show_form()
