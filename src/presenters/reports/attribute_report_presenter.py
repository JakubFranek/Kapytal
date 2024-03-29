import logging
from collections.abc import Collection

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication
from src.models.base_classes.transaction import Transaction
from src.models.custom_exceptions import InvalidOperationError
from src.models.model_objects.attributes import AttributeType
from src.models.model_objects.cash_objects import CashTransaction, RefundTransaction
from src.models.record_keeper import RecordKeeper
from src.models.statistics.attribute_stats import (
    AttributeStats,
    calculate_periodic_attribute_stats,
    calculate_periodic_totals_and_averages,
)
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.view_models.periodic_attribute_stats_table_model import (
    PeriodicAttributeStatsTableModel,
)
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.main_view import MainView
from src.views.reports.attribute_report import AttributeReport, StatsType
from src.views.utilities.handle_exception import display_error_message
from src.views.utilities.message_box_functions import ask_yes_no_question

N_TRANSACTIONS_THRESHOLD = 500


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
        self._main_view.signal_tag_monthly_report.connect(
            lambda: self._create_periodic_report_with_busy_dialog(
                period_format="%b %Y",
                title="Tag Report - Monthly",
                attribute_type=AttributeType.TAG,
            )
        )
        self._main_view.signal_tag_annual_report.connect(
            lambda: self._create_periodic_report_with_busy_dialog(
                period_format="%Y",
                title="Tag Report - Annual",
                attribute_type=AttributeType.TAG,
            )
        )
        self._main_view.signal_payee_monthly_report.connect(
            lambda: self._create_periodic_report_with_busy_dialog(
                period_format="%b %Y",
                title="Payee Report - Monthly",
                attribute_type=AttributeType.PAYEE,
            )
        )
        self._main_view.signal_payee_annual_report.connect(
            lambda: self._create_periodic_report_with_busy_dialog(
                period_format="%Y",
                title="Payee Report - Annual",
                attribute_type=AttributeType.PAYEE,
            )
        )

    def _create_periodic_report_with_busy_dialog(
        self, period_format: str, title: str, attribute_type: AttributeType
    ) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self._main_view, "Preparing report, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            self._create_periodic_report(period_format, title, attribute_type)
        except:  # noqa: TRY302
            raise
        finally:
            self._busy_dialog.close()

    def _create_periodic_report(
        self, period_format: str, title: str, attribute_type: AttributeType
    ) -> None:
        logging.debug(
            f"Attribute Report requested: {period_format=}, "
            f"attribute_type={attribute_type.name}"
        )

        transactions = self._transactions_presenter.get_visible_transactions()
        transactions = _filter_transactions(transactions)
        base_currency = self._record_keeper.base_currency
        if base_currency is None:
            display_error_message(
                "Set a base Currency before running this report.",
                title="Warning",
            )
            return

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

        attributes = (
            self._record_keeper.tags
            if attribute_type == AttributeType.TAG
            else self._record_keeper.payees
        )

        periodic_stats = calculate_periodic_attribute_stats(
            transactions,
            base_currency,
            attributes,
            period_format=period_format,
        )

        # keep only stats which are are non-zero in at least one period
        _periodic_stats: dict[str, list[AttributeStats]] = {}
        for period, stats in periodic_stats.items():
            _stats = [item for item in stats if item.balance.value_rounded != 0]
            _periodic_stats[period] = _stats

        (
            period_totals,
            attribute_averages,
            attribute_totals,
        ) = calculate_periodic_totals_and_averages(
            _periodic_stats, self._record_keeper.base_currency
        )

        self._report = AttributeReport(
            title, base_currency.code, attribute_type, self._main_view
        )
        self._report.signal_show_transactions.connect(self._show_selected_transactions)
        self._report.signal_recalculate_report.connect(
            lambda: self._recalculate_report(period_format, title, attribute_type)
        )
        self._report.signal_selection_changed.connect(self._selection_changed)
        self._report.signal_pie_slice_clicked.connect(self._pie_slice_clicked)
        self._report.signal_search_text_changed.connect(self._filter)
        self._report.searchLineEdit.setPlaceholderText(
            f"Search {attribute_type.name.title()}s"
        )

        self._proxy = QSortFilterProxyModel(self._report)
        self._model = PeriodicAttributeStatsTableModel(
            self._report.tableView, self._proxy
        )
        self._model.load_periodic_attribute_stats(
            _periodic_stats,
            period_totals,
            attribute_averages,
            attribute_totals,
        )
        self._proxy.setSourceModel(self._model)
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy.setFilterCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._proxy.setFilterRole(Qt.ItemDataRole.UserRole + 1)
        self._report.tableView.setModel(self._proxy)
        self._report.tableView.sortByColumn(
            self._model.AVERAGE_COLUMN_INDEX, Qt.SortOrder.DescendingOrder
        )

        income_periodic_stats: dict[str, list[AttributeStats]] = {}
        expense_periodic_stats: dict[str, list[AttributeStats]] = {}
        for period in periodic_stats:
            income_periodic_stats[period] = []
            expense_periodic_stats[period] = []
            for stats in periodic_stats[period]:
                if stats.balance.value_rounded > 0:
                    income_periodic_stats[period].append(stats)
                elif stats.balance.value_rounded < 0:
                    expense_periodic_stats[period].append(stats)

        income_periodic_stats["Average"] = []
        expense_periodic_stats["Average"] = []
        for attribute, transaction_balance in attribute_averages.items():
            stats = AttributeStats(
                attribute,
                0,
                transaction_balance.balance,
                transaction_balance.transactions,
            )
            if transaction_balance.balance.value_rounded > 0:
                income_periodic_stats["Average"].append(stats)
            elif transaction_balance.balance.value_rounded < 0:
                expense_periodic_stats["Average"].append(stats)

        income_periodic_stats["Total"] = []
        expense_periodic_stats["Total"] = []
        for attribute, transaction_balance in attribute_totals.items():
            stats = AttributeStats(
                attribute,
                0,
                transaction_balance.balance,
                transaction_balance.transactions,
            )
            if transaction_balance.balance.value_rounded > 0:
                income_periodic_stats["Total"].append(stats)
            elif transaction_balance.balance.value_rounded < 0:
                expense_periodic_stats["Total"].append(stats)

        self._income_stats = income_periodic_stats
        self._expense_stats = expense_periodic_stats
        self._attribute_type = attribute_type

        self._report.load_stats(income_periodic_stats, expense_periodic_stats)
        self._report.finalize_setup()
        self._selection_changed()
        self._report.show_form()

    def _show_selected_transactions(self) -> None:
        transactions, period, path = self._model.get_selected_transactions()
        title = f"{self._attribute_type.name.title()} Report - {path}, {period}"
        self._show_transaction_table(transactions, title)

    def _pie_slice_clicked(self, name: str) -> None:
        stats_type = self._report.stats_type
        period = self._report.period
        title = f"{self._attribute_type.name.title()} Report - {name}, {period}"

        data = (
            self._income_stats[period]
            if stats_type == StatsType.INCOME
            else self._expense_stats[period]
        )

        transactions = None
        for stats in data:
            if stats.attribute.name == name:
                transactions = stats.transactions
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

    def _recalculate_report(
        self, period_format: str, title: str, attribute_type: AttributeType
    ) -> None:
        self._report.close()
        self._create_periodic_report_with_busy_dialog(
            period_format, title, attribute_type
        )

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

    def _filter(self, pattern: str) -> None:
        if ("[" in pattern and "]" not in pattern) or "[]" in pattern:
            return
        self._proxy.setFilterWildcard(pattern)


def _filter_transactions(
    transactions: Collection[Transaction],
) -> tuple[CashTransaction | RefundTransaction, ...]:
    return tuple(
        transaction
        for transaction in transactions
        if isinstance(transaction, CashTransaction | RefundTransaction)
    )
