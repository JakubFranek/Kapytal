import logging
from datetime import datetime

from PyQt6.QtWidgets import QApplication
from src.models.custom_exceptions import InvalidOperationError
from src.models.record_keeper import RecordKeeper
from src.models.statistics.cashflow_stats import (
    PeriodType,
    calculate_cash_flow,
    calculate_periodic_cash_flow,
)
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.user_settings import user_settings
from src.presenters.utilities.handle_exception import handle_exception
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.main_view import MainView
from src.views.reports.cashflow_periodic_report import CashFlowPeriodicReport
from src.views.reports.cashflow_total_report import CashFlowTotalReport
from src.views.utilities.handle_exception import display_error_message
from src.views.utilities.message_box_functions import ask_yes_no_question

N_TRANSACTIONS_THRESHOLD = 500


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
            self._create_total_cash_flow_report_with_busy_dialog
        )
        self._main_view.signal_cash_flow_montly_report.connect(
            lambda: self._create_periodic_cash_flow_report_with_busy_dialog(
                PeriodType.MONTH, "Cash Flow Report - Monthly"
            )
        )
        self._main_view.signal_cash_flow_annual_report.connect(
            lambda: self._create_periodic_cash_flow_report_with_busy_dialog(
                PeriodType.YEAR, "Cash Flow Report - Annual"
            )
        )

    def _create_total_cash_flow_report_with_busy_dialog(self) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self._main_view, "Preparing report, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            self._create_total_cash_flow_report()
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
        finally:
            self._busy_dialog.close()

    def _create_periodic_cash_flow_report_with_busy_dialog(
        self, period_type: PeriodType, title: str
    ) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self._main_view, "Preparing report, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            self._create_periodic_cash_flow_report(period_type, title)
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
        finally:
            self._busy_dialog.close()

    def _create_total_cash_flow_report(self) -> None:
        logging.debug("Total Cash Flow Report requested")

        transactions = self._transactions_presenter.get_visible_transactions()

        n_transactions = len(transactions)
        if n_transactions == 0:
            display_error_message(
                "This report cannot be run because there are no Transactions passing "
                "Transaction filter.",
                title="Warning",
            )
            return
        if n_transactions > N_TRANSACTIONS_THRESHOLD and not ask_yes_no_question(
            self._busy_dialog,
            "The report will be generated from a large number of Transactions "
            f"({n_transactions}). This may take a while. "
            "Proceed anyway?",
            "Are you sure?",
        ):
            logging.debug("User cancelled the report creation")
            return

        datetime_filter = (
            self._transactions_presenter.transaction_filter_form_presenter.transaction_filter.datetime_filter
        )
        if datetime_filter.mode == FilterMode.OFF:
            start_date = None
            end_date = datetime.now(tz=user_settings.settings.time_zone).date()
        elif datetime_filter.mode == FilterMode.KEEP:
            start_date = datetime_filter.start.date()
            end_date = datetime_filter.end.date()
        else:
            raise InvalidOperationError(
                f"Datetime Filter mode={datetime_filter.mode.name} "
                "is not supported by this report."
            )

        account_filter = (
            self._transactions_presenter.transaction_filter_form_presenter.transaction_filter.account_filter
        )
        if account_filter.mode == FilterMode.OFF:
            accounts = self._record_keeper.accounts
        elif account_filter.mode == FilterMode.KEEP:
            accounts = account_filter.accounts
        else:
            raise ValueError(
                f"Account Filter mode={datetime_filter.mode.name} "
                "is not supported by this report."
            )

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

        cash_flow_stats = calculate_cash_flow(
            transactions, accounts, base_currency, start_date, end_date
        )
        self.report = CashFlowTotalReport(self._main_view)
        self.report.load_stats(cash_flow_stats)
        self.report.show_form()

    def _create_periodic_cash_flow_report(
        self, period_type: PeriodType, title: str
    ) -> None:
        logging.debug(
            f"Periodic Cash Flow Report requested: period_type={period_type.name}"
        )

        transactions = self._transactions_presenter.get_visible_transactions()

        datetime_filter = (
            self._transactions_presenter.transaction_filter_form_presenter.transaction_filter.datetime_filter
        )
        if datetime_filter.mode == FilterMode.OFF:
            start_date = None
            end_date = datetime.now(tz=user_settings.settings.time_zone).date()
        elif datetime_filter.mode == FilterMode.KEEP:
            start_date = datetime_filter.start.date()
            end_date = datetime_filter.end.date()
        else:
            raise InvalidOperationError(
                f"Datetime Filter mode={datetime_filter.mode.name} "
                "is not supported by this report."
            )

        account_filter = (
            self._transactions_presenter.transaction_filter_form_presenter.transaction_filter.account_filter
        )
        if account_filter.mode == FilterMode.OFF:
            accounts = self._record_keeper.accounts
        elif account_filter.mode == FilterMode.KEEP:
            accounts = account_filter.accounts
        else:
            raise ValueError(
                f"Account Filter mode={datetime_filter.mode.name} "
                "is not supported by this report."
            )

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
            transactions, accounts, base_currency, period_type, start_date, end_date
        )
        self.report = CashFlowPeriodicReport(title, self._main_view)
        self.report.load_stats(cash_flow_stats)
        self.report.show_form()
