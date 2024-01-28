import logging
from collections.abc import Collection

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication
from src.models.base_classes.transaction import Transaction
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.attributes import Category
from src.models.model_objects.cash_objects import (
    CashTransaction,
    CashTransactionType,
    RefundTransaction,
)
from src.models.model_objects.currency_objects import Currency
from src.models.record_keeper import RecordKeeper
from src.models.statistics.category_stats import (
    CategoryStats,
    calculate_periodic_category_stats,
    calculate_periodic_totals_and_averages,
)
from src.models.statistics.common_classes import TransactionBalance
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.view_models.periodic_category_stats_tree_model import (
    PeriodicCategoryStatsTreeModel,
)
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.main_view import MainView
from src.views.reports.category_report import CategoryReport, StatsType
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
            f"({n_transactions:n}). This may take a while. "
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
        self._report.signal_show_transactions.connect(self._show_selected_transactions)
        self._report.signal_recalculate_report.connect(
            lambda: self._recalculate_report(period_format, title)
        )
        self._report.signal_selection_changed.connect(self._selection_changed)
        self._report.signal_sunburst_slice_clicked.connect(self._sunburst_slice_clicked)
        self._report.signal_search_text_changed.connect(self._filter)

        self._proxy = QSortFilterProxyModel(self._report)
        self._model = PeriodicCategoryStatsTreeModel(self._report.treeView, self._proxy)
        self._model.load_periodic_category_stats(
            periodic_stats,
            period_totals,
            period_income_totals,
            period_expense_totals,
            category_averages,
            category_totals,
            base_currency,
        )
        self._proxy.setSourceModel(self._model)
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setRecursiveFilteringEnabled(True)
        self._proxy.setFilterRole(Qt.ItemDataRole.UserRole + 1)
        self._report.treeView.setModel(self._proxy)
        self._report.treeView.header().setSortIndicatorClearable(True)
        self._report.treeView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)

        income_periodic_stats: dict[str, list[CategoryStats]] = {}
        expense_periodic_stats: dict[str, list[CategoryStats]] = {}
        for period, stats in periodic_stats.items():
            income_stats, expense_stats = separate_income_and_expense_stats(
                stats, base_currency
            )
            income_periodic_stats[period] = income_stats
            expense_periodic_stats[period] = expense_stats

        income_averages, expense_averages = separate_income_and_expense_stats(
            category_averages, base_currency, divisor=len(periodic_stats)
        )
        income_periodic_stats["Average"] = income_averages
        expense_periodic_stats["Average"] = expense_averages

        income_totals, expense_totals = separate_income_and_expense_stats(
            category_totals, base_currency
        )
        income_periodic_stats["Total"] = income_totals
        expense_periodic_stats["Total"] = expense_totals

        add_missing_parent_category_stats(income_periodic_stats)
        add_missing_parent_category_stats(expense_periodic_stats)

        # saved to retrieve data when slice is clicked
        self._income_stats = income_periodic_stats
        self._expense_stats = expense_periodic_stats

        self._report.load_stats(
            income_periodic_stats, expense_periodic_stats, base_currency
        )
        self._report.finalize_setup()
        self._selection_changed()
        self._report.show_form()

    def _show_selected_transactions(self) -> None:
        transactions, period, path = self._model.get_selected_transactions()
        title = f"Category Report - {path}, {period}"
        self._show_transaction_table(transactions, title)

    def _sunburst_slice_clicked(self, path: str) -> None:
        stats_type = self._report.stats_type
        period = self._report.period
        title = f"Category Report - {path}, {period}"

        data = (
            self._income_stats[period]
            if stats_type == StatsType.INCOME
            else self._expense_stats[period]
        )

        transactions = None
        if path == "Total":
            transactions: set[CashTransaction | RefundTransaction] = set()
            for category_stats in data:
                if category_stats.category.parent is not None:
                    continue
                transactions = transactions.union(category_stats.transactions)
        for category_stats in data:
            if category_stats.category.path == path:
                transactions = category_stats.transactions
                break
        if transactions is None:
            return

        self._show_transaction_table(transactions, title)

    def _show_transaction_table(
        self, transactions: Collection[Transaction], title: str
    ) -> None:
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
            self._model.update_selected_row_objects()
            transactions, _, _ = self._model.get_selected_transactions()
        except InvalidOperationError:
            enabled = False
        else:
            enabled = len(transactions) > 0
        self._report.set_show_transactions_action_state(enable=enabled)

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return

        # needed to prevent crash when filtering when any cell is selected
        self._report.treeView.selectionModel().clearSelection()

        self._proxy.setFilterWildcard(pattern)

        # needed to prevent selecting cells when filtering unpredictably
        self._report.treeView.selectionModel().clearSelection()

        self._report.treeView.expandAll()


def _filter_transactions(
    transactions: Collection[Transaction],
) -> tuple[CashTransaction | RefundTransaction]:
    return tuple(
        transaction
        for transaction in transactions
        if isinstance(transaction, CashTransaction | RefundTransaction)
    )


def separate_income_and_expense_stats(
    category_stats: dict[Category, TransactionBalance] | tuple[CategoryStats, ...],
    currency: Currency,
    divisor: int = 1,
) -> tuple[tuple[CategoryStats, ...], tuple[CategoryStats, ...]]:
    income_stats = []
    expense_stats = []
    if isinstance(category_stats, dict):
        for category, transactions_balance in category_stats.items():
            separate_stats(
                income_stats,
                expense_stats,
                transactions_balance.transactions,
                category,
                currency,
                divisor,
            )
    elif isinstance(category_stats, tuple):
        for stats in category_stats:
            separate_stats(
                income_stats,
                expense_stats,
                stats.transactions,
                stats.category,
                currency,
                divisor,
            )
    else:
        raise TypeError("Parameter 'category_stats' must be a dict or a tuple.")

    return income_stats, expense_stats


def separate_stats(
    income_stats: list[CategoryStats],
    expense_stats: list[CategoryStats],
    transactions: Collection[CashTransaction | RefundTransaction],
    category: Category,
    currency: Currency,
    divisor: int = 1,
) -> None:
    income_data = TransactionBalance(currency.zero_amount)
    expense_data = TransactionBalance(currency.zero_amount)
    for transaction in transactions:
        date_ = transaction.date_
        amount = transaction.get_amount_for_category(category, total=True).convert(
            currency, date_
        )
        if (
            isinstance(transaction, RefundTransaction)
            or transaction.type_ == CashTransactionType.INCOME
        ):
            income_data.add_transaction_balance({transaction}, amount)
        else:
            expense_data.add_transaction_balance({transaction}, amount)
    if len(income_data) > 0:
        income_stats_item = CategoryStats(
            category, 0, 0, income_data.balance / divisor, income_data.transactions
        )
        income_stats.append(income_stats_item)
    if len(expense_data) > 0:
        expense_stats_item = CategoryStats(
            category, 0, 0, expense_data.balance / divisor, expense_data.transactions
        )
        expense_stats.append(expense_stats_item)


def add_missing_parent_category_stats(
    periodic_category_stats: dict[str, list[CategoryStats]],
) -> tuple[CategoryStats, ...]:
    stats_to_add = []
    for period, stats_sequence in periodic_category_stats.items():
        categories = {s.category for s in stats_sequence}
        for stats in stats_sequence:
            if stats.category.parent is not None:
                parent = stats.category.parent
                while parent is not None and parent not in categories:
                    _stats = CategoryStats(
                        stats.category.parent,
                        0,
                        0,
                        stats.balance,
                        stats.transactions,
                    )
                    stats_to_add.append((period, _stats))
                    categories.add(parent)
                    parent = parent.parent

    for period, stats in stats_to_add:
        periodic_category_stats[period].append(stats)
