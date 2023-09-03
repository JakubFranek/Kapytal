import logging
from collections.abc import Collection

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication
from src.models.base_classes.transaction import Transaction
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.record_keeper import RecordKeeper
from src.models.statistics.category_stats import (
    CategoryStats,
    calculate_periodic_category_stats,
    calculate_periodic_totals_and_averages,
)
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.view_models.periodic_category_stats_tree_model import (
    PeriodicCategoryStatsTreeModel,
)
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.main_view import MainView
from src.views.reports.category_report import CategoryReport
from src.views.utilities.handle_exception import display_error_message
from src.views.utilities.message_box_functions import ask_yes_no_question

N_TRANSACTIONS_THRESHOLD = 1_000


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
        self._main_view.signal_category_monthly_report.connect(
            lambda: self._create_periodic_report_with_busy_dialog(
                period_format="%b %Y", title="Category Report - Monthly"
            )
        )
        self._main_view.signal_category_annual_report.connect(
            lambda: self._create_periodic_report_with_busy_dialog(
                period_format="%Y", title="Category Report - Annual"
            )
        )

    def _create_periodic_report_with_busy_dialog(
        self, period_format: str, title: str
    ) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self._main_view, "Preparing report, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            self._create_periodic_report(period_format, title)
        except:  # noqa: TRY302
            raise
        finally:
            self._busy_dialog.close()

    def _create_periodic_report(self, period_format: str, title: str) -> None:
        logging.debug(f"Category Report requested: {period_format=}")

        transactions = self._transactions_presenter.get_visible_transactions()
        transactions = _filter_transactions(transactions)
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
            f"({n_transactions:,}). This may take a while. "
            "Proceed anyway?",
            "Are you sure?",
        ):
            logging.debug("User cancelled the report creation")
            return

        base_currency = self._record_keeper.base_currency

        if base_currency is None:
            display_error_message(
                "Set a base Currency before running this report.",
                title="Warning",
            )
            return
        if not transactions:
            display_error_message(
                "This report cannot be run because there are no Transactions passing "
                "Transaction filter.",
                title="Warning",
            )
            return

        periodic_stats = calculate_periodic_category_stats(
            transactions,
            base_currency,
            self._record_keeper.categories,
            period_format=period_format,
        )

        (
            period_totals,
            period_income_totals,
            period_expense_totals,
            category_averages,
            category_totals,
        ) = calculate_periodic_totals_and_averages(periodic_stats, base_currency)

        self._report = CategoryReport(title, base_currency.code, self._main_view)
        self._report.signal_show_transactions.connect(self._show_transactions)
        self._report.signal_recalculate_report.connect(
            lambda: self._recalculate_report(period_format, title)
        )
        self._report.signal_selection_changed.connect(self._selection_changed)

        self._proxy = QSortFilterProxyModel(self._report)
        self._model = PeriodicCategoryStatsTreeModel(self._report.treeView, self._proxy)
        self._model.load_periodic_category_stats(
            periodic_stats,
            period_totals,
            period_income_totals,
            period_expense_totals,
            category_averages,
            category_totals,
        )
        self._proxy.setSourceModel(self._model)
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._report.treeView.setModel(self._proxy)
        self._report.treeView.header().setSortIndicatorClearable(True)  # noqa: FBT003
        self._report.treeView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)

        income_periodic_stats: dict[str, list[CategoryStats]] = {}
        expense_periodic_stats: dict[str, list[CategoryStats]] = {}
        for period, stats in periodic_stats.items():
            income_stats = []
            expense_stats = []
            for item in stats:
                if item.balance.value_rounded > 0:
                    income_stats.append(item)
                elif item.balance.value_rounded < 0:
                    expense_stats.append(item)
            income_periodic_stats[period] = income_stats
            expense_periodic_stats[period] = expense_stats

        income_average_stats = [
            CategoryStats(category, 0, 0, transactions_balance.balance)
            for category, transactions_balance in category_averages.items()
            if transactions_balance.balance.value_rounded > 0
        ]
        expense_average_stats = [
            CategoryStats(category, 0, 0, transactions_balance.balance)
            for category, transactions_balance in category_averages.items()
            if transactions_balance.balance.value_rounded < 0
        ]
        income_periodic_stats["Average / Total"] = income_average_stats
        expense_periodic_stats["Average / Total"] = expense_average_stats

        self._report.load_stats(income_periodic_stats, expense_periodic_stats)
        self._report.finalize_setup()
        self._selection_changed()
        self._report.show_form()

    def _show_transactions(self) -> None:
        transactions, period, path = self._model.get_selected_transactions()
        title = f"Category Report - {path}, {period}"
        transaction_table_form_presenter = (
            self._transactions_presenter.transaction_table_form_presenter
        )
        transaction_table_form_presenter.event_data_changed.append(
            lambda _: self._report.set_recalculate_report_action_state(enabled=True)
        )
        transaction_table_form_presenter.show_data(transactions, title, self._report)

    def _recalculate_report(self, period_format: str, title: str) -> None:
        self._report.close()
        self._create_periodic_report_with_busy_dialog(period_format, title)

    def _selection_changed(
        self,
    ) -> None:
        try:
            transactions, _, _ = self._model.get_selected_transactions()
        except InvalidOperationError:
            enabled = False
        else:
            enabled = len(transactions) > 0
        self._report.set_show_transactions_action_state(enable=enabled)


def _filter_transactions(
    transactions: Collection[Transaction],
) -> tuple[CashTransaction | RefundTransaction]:
    return tuple(
        transaction
        for transaction in transactions
        if isinstance(transaction, CashTransaction | RefundTransaction)
    )
