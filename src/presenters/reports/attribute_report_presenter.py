from collections.abc import Collection

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.base_classes.transaction import Transaction
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
from src.views.main_view import MainView
from src.views.reports.attribute_periodic_report import AttributeReport
from src.views.utilities.handle_exception import display_error_message


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
            lambda: self._create_periodic_report(
                period_format="%b %Y",
                title="Tag Report - Monthly",
                attribute_type=AttributeType.TAG,
            )
        )
        self._main_view.signal_tag_annual_report.connect(
            lambda: self._create_periodic_report(
                period_format="%Y",
                title="Tag Report - Annual",
                attribute_type=AttributeType.TAG,
            )
        )
        self._main_view.signal_payee_monthly_report.connect(
            lambda: self._create_periodic_report(
                period_format="%b %Y",
                title="Payee Report - Monthly",
                attribute_type=AttributeType.PAYEE,
            )
        )
        self._main_view.signal_payee_annual_report.connect(
            lambda: self._create_periodic_report(
                period_format="%Y",
                title="Payee Report - Annual",
                attribute_type=AttributeType.PAYEE,
            )
        )

    def _create_periodic_report(
        self, period_format: str, title: str, attribute_type: AttributeType
    ) -> None:
        transactions = self._transactions_presenter.get_visible_transactions()
        transactions = _filter_transactions(transactions)
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
            _stats = []
            for item in stats:
                if item.balance.value_rounded != 0:
                    _stats.append(item)
            _periodic_stats[period] = _stats

        (
            period_totals,
            attribute_averages,
            attribute_totals,
        ) = calculate_periodic_totals_and_averages(_periodic_stats)

        self.report = AttributeReport(title, base_currency.code, self._main_view)

        self._proxy = QSortFilterProxyModel(self.report)
        self._model = PeriodicAttributeStatsTableModel(
            self.report.tableView, self._proxy
        )
        self._model.load_periodic_attribute_stats(
            _periodic_stats,
            period_totals,
            attribute_averages,
            attribute_totals,
            base_currency,
        )
        self._proxy.setSourceModel(self._model)
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self.report.tableView.setModel(self._proxy)
        self.report.tableView.sortByColumn(
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

        income_average_stats = [
            AttributeStats(attribute, 0, balance)
            for attribute, balance in attribute_averages.items()
            if balance.value_rounded > 0
        ]
        expense_average_stats = [
            AttributeStats(attribute, 0, balance)
            for attribute, balance in attribute_averages.items()
            if balance.value_rounded < 0
        ]
        income_periodic_stats["Average / Total"] = income_average_stats
        expense_periodic_stats["Average / Total"] = expense_average_stats

        self.report.load_stats(income_periodic_stats, expense_periodic_stats)
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
