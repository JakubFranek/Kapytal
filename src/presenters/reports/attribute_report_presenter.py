from collections.abc import Collection

from src.models.base_classes.transaction import Transaction
from src.models.model_objects.attributes import AttributeType
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.record_keeper import RecordKeeper
from src.models.statistics.attribute_stats import (
    calculate_attribute_stats,
    calculate_average_per_month_attribute_stats,
)
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.views.main_view import MainView
from src.views.reports.attribute_report import AttributeReport


class AttributeReportPresenter:
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
        self._main_view.signal_tag_total_report.connect(
            lambda: self._create_total_report(AttributeType.TAG)
        )
        self._main_view.signal_tag_average_per_month_report.connect(
            lambda: self._create_average_per_month_report(AttributeType.TAG)
        )
        self._main_view.signal_payee_total_report.connect(
            lambda: self._create_total_report(AttributeType.PAYEE)
        )
        self._main_view.signal_payee_average_per_month_report.connect(
            lambda: self._create_average_per_month_report(AttributeType.PAYEE)
        )

    def _create_total_report(self, attribute_type: AttributeType) -> None:
        transactions = self._transactions_presenter.get_visible_transactions()
        transactions = _filter_transactions(transactions)
        base_currency = self._record_keeper.base_currency
        attributes = (
            self._record_keeper.tags
            if attribute_type == AttributeType.TAG
            else self._record_keeper.payees
        )
        title = (
            "Tag Report - Total"
            if attribute_type == AttributeType.TAG
            else "Payee Report - Total"
        )
        stats = calculate_attribute_stats(transactions, base_currency, attributes)
        self.report = AttributeReport(title, self._main_view)
        self.report.finalize_setup()
        self.report.load_stats(stats.values())
        self.report.show_form()

    def _create_average_per_month_report(self, attribute_type: AttributeType) -> None:
        transactions = self._transactions_presenter.get_visible_transactions()
        transactions = _filter_transactions(transactions)
        base_currency = self._record_keeper.base_currency
        attributes = (
            self._record_keeper.tags
            if attribute_type == AttributeType.TAG
            else self._record_keeper.payees
        )
        title = (
            "Tag Report - Average Per Month"
            if attribute_type == AttributeType.TAG
            else "Payee Report - Average Per Month"
        )
        stats = calculate_average_per_month_attribute_stats(
            transactions, base_currency, attributes
        )
        self.report = AttributeReport(title, self._main_view)
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
