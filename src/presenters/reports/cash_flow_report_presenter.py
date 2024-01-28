import logging
from datetime import datetime
from typing import Any

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
from src.views.reports.cashflow_total_report import (
    CashFlowTotalReport,
    TransactionGroup,
)
from src.views.utilities.handle_exception import display_error_message
from src.views.utilities.message_box_functions import ask_yes_no_question

N_TRANSACTIONS_THRESHOLD_TOTAL = 50_000
N_TRANSACTIONS_THRESHOLD_PERIODIC = 5_000


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
        if n_transactions > N_TRANSACTIONS_THRESHOLD_TOTAL and not ask_yes_no_question(
            self._busy_dialog,
            "The report will be generated from a large number of Transactions "
            f"({n_transactions:n}). This may take a while. "
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
        self._total_stats = cash_flow_stats

        self._report = CashFlowTotalReport(self._main_view)
        self._report.event_show_transactions.append(self._show_total_transactions)
        self._report.signal_recalculate_report.connect(self._recalculate_total_report)
        self._report.load_stats(cash_flow_stats)
        self._report.show_form()

    def _create_periodic_cash_flow_report(
        self, period_type: PeriodType, title: str
    ) -> None:
        logging.debug(
            f"Periodic Cash Flow Report requested: period_type={period_type.name}"
        )

        transactions = self._transactions_presenter.get_visible_transactions()
        n_transactions = len(transactions)
        if n_transactions == 0:
            display_error_message(
                "This report cannot be run because there are no Transactions passing "
                "Transaction filter.",
                title="Warning",
            )
            return
        if (
            n_transactions > N_TRANSACTIONS_THRESHOLD_PERIODIC
            and not ask_yes_no_question(
                self._busy_dialog,
                "The report will be generated from a large number of Transactions "
                f"({n_transactions:n}). This may take a while. "
                "Proceed anyway?",
                "Are you sure?",
            )
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

        cash_flow_stats = calculate_periodic_cash_flow(
            transactions, accounts, base_currency, period_type, start_date, end_date
        )
        self._report = CashFlowPeriodicReport(
            title, base_currency.code, self._main_view
        )
        self._report.signal_show_transactions.connect(self._show_transactions)
        self._report.signal_recalculate_report.connect(
            lambda: self._recalculate_periodic_report(period_type, title)
        )
        self._report.signal_selection_changed.connect(self._selection_changed)
        self._report.load_stats(cash_flow_stats)
        self._selection_changed()
        self._report.show_form()

    def _show_transactions(self) -> None:
        (
            transactions,
            period,
            path,
        ) = self._report.get_selected_transactions()
        title = f"Cash Flow Report - {path}, {period}"

        transaction_table_form_presenter = (
            self._transactions_presenter.transaction_table_form_presenter
        )
        transaction_table_form_presenter.event_data_changed.append(
            self._activate_recalculate_action
        )
        transaction_table_form_presenter.event_form_closed.append(
            self._on_transaction_table_form_close
        )

        transaction_table_form_presenter.show_data(transactions, title, self._report)

    def _show_total_transactions(self, group: TransactionGroup) -> None:
        match group:
            case TransactionGroup.INCOME:
                transactions = self._total_stats.incomes.transactions
                path = "Income"
            case TransactionGroup.INWARD_TRANSFER:
                transactions = self._total_stats.inward_transfers.transactions
                path = "Inward Transfers"
            case TransactionGroup.REFUND:
                transactions = self._total_stats.refunds.transactions
                path = "Refunds"
            case TransactionGroup.INFLOWS:
                transactions = self._total_stats.inflows.transactions
                path = "Inflows"
            case TransactionGroup.OUTWARD_TRANSFER:
                transactions = self._total_stats.outward_transfers.transactions
                path = "Outward Transfers"
            case TransactionGroup.EXPENSE:
                transactions = self._total_stats.expenses.transactions
                path = "Expenses"
            case TransactionGroup.OUTFLOWS:
                transactions = self._total_stats.outflows.transactions
                path = "Outflows"
            case TransactionGroup.CASHFLOW:
                transactions = self._total_stats.delta_neutral.transactions
                path = "Cash Flow"
            case _:
                raise ValueError(f"Unsupported TransactionGroup: {group}")

        title = f"Cash Flow Report - {path}"
        transaction_table_form_presenter = (
            self._transactions_presenter.transaction_table_form_presenter
        )
        transaction_table_form_presenter.event_data_changed.append(
            self._activate_recalculate_action
        )
        transaction_table_form_presenter.event_form_closed.append(
            self._on_transaction_table_form_close
        )
        transaction_table_form_presenter.show_data(transactions, title, self._report)

    def _recalculate_periodic_report(self, period_type: PeriodType, title: str) -> None:
        self._report.close()
        self._create_periodic_cash_flow_report_with_busy_dialog(period_type, title)

    def _recalculate_total_report(self) -> None:
        self._report.close()
        self._create_total_cash_flow_report_with_busy_dialog()

    def _selection_changed(
        self,
    ) -> None:
        try:
            transactions, _, _ = self._report.get_selected_transactions()
        except InvalidOperationError:
            enabled = False
        else:
            enabled = len(transactions) > 0
        self._report.set_show_transactions_action_state(enable=enabled)

    def _activate_recalculate_action(
        self,
        *_: Any,  # noqa: ANN401
    ) -> None:
        # *_ due to event_data_changed being called with argument UUIDs
        self._report.set_recalculate_report_action_state(enabled=True)

    def _on_transaction_table_form_close(self) -> None:
        # cleanup method
        transaction_table_form_presenter = (
            self._transactions_presenter.transaction_table_form_presenter
        )
        if (
            self._activate_recalculate_action
            in transaction_table_form_presenter.event_data_changed
        ):
            transaction_table_form_presenter.event_data_changed.remove(
                self._activate_recalculate_action
            )
