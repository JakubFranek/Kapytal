from src.models.record_keeper import RecordKeeper
from src.models.statistics.cashflow_stats import (
    calculate_cash_flow,
    calculate_periodic_cash_flow,
)
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.views.main_view import MainView
from src.views.reports.cashflow_periodic_report import CashFlowPeriodicReport
from src.views.reports.cashflow_total_report import CashFlowTotalReport
from src.views.utilities.handle_exception import display_error_message


class CashFlowReportPresenter:
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
        self._main_view.signal_cash_flow_total_report.connect(
            self._create_total_cash_flow_report
        )
        self._main_view.signal_cash_flow_montly_report.connect(
            lambda: self._create_periodic_cash_flow_report(
                "%b %Y", "Cash Flow Report - Monthly"
            )
        )
        self._main_view.signal_cash_flow_annual_report.connect(
            lambda: self._create_periodic_cash_flow_report(
                "%Y", "Cash Flow Report - Annual"
            )
        )

    def _create_total_cash_flow_report(self) -> None:
        transactions = self._transactions_presenter.get_visible_transactions()
        account_filter = (
            self._transactions_presenter.transaction_filter_form_presenter.transaction_filter.account_filter
        )
        if account_filter.mode == FilterMode.OFF:
            accounts = self._record_keeper.accounts
        elif account_filter.mode == FilterMode.KEEP:
            accounts = account_filter.accounts
        else:
            raise ValueError(f"Unexpected filter mode: {account_filter.mode}")
        base_currency = self._record_keeper.base_currency

        if base_currency is None:
            display_error_message(
                "Set a base Currency before running this report.",
                title="Warning",
            )
            return
        if not accounts:
            display_error_message(
                "Select at least one Account before running this report.",
                title="Warning",
            )
            return

        cash_flow_stats = calculate_cash_flow(transactions, accounts, base_currency)
        self.report = CashFlowTotalReport(self._main_view)
        self.report.load_stats(cash_flow_stats)
        self.report.show_form()

    def _create_periodic_cash_flow_report(self, period_format: str, title: str) -> None:
        transactions = self._transactions_presenter.get_visible_transactions()
        account_filter = (
            self._transactions_presenter.transaction_filter_form_presenter.transaction_filter.account_filter
        )
        if account_filter.mode == FilterMode.OFF:
            accounts = self._record_keeper.accounts
        elif account_filter.mode == FilterMode.KEEP:
            accounts = account_filter.accounts
        else:
            raise ValueError(f"Unexpected filter mode: {account_filter.mode}")
        base_currency = self._record_keeper.base_currency

        if base_currency is None:
            display_error_message(
                "Set a base Currency before running this report.",
                title="Warning",
            )
            return
        if not accounts:
            display_error_message(
                "Select at least one Account before running this report.",
                title="Warning",
            )
            return

        cash_flow_stats = calculate_periodic_cash_flow(
            transactions, accounts, base_currency, period_format
        )
        self.report = CashFlowPeriodicReport(title, self._main_view)
        self.report.load_stats(cash_flow_stats)
        self.report.show_form()
