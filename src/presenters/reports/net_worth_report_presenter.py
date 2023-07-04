from collections.abc import Collection
from datetime import datetime

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.currency_objects import Currency
from src.models.record_keeper import RecordKeeper
from src.models.statistics.net_worth_stats import (
    AssetStats,
    calculate_asset_stats,
    calculate_net_worth_over_time,
)
from src.models.transaction_filters.base_transaction_filter import FilterMode
from src.models.user_settings import user_settings
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.view_models.account_tree_model import AccountTreeModel
from src.view_models.asset_type_tree_model import AssetTypeTreeModel
from src.view_models.value_table_model import ValueTableModel, ValueType
from src.views.constants import AccountTreeColumn
from src.views.main_view import MainView
from src.views.reports.table_and_line_chart_report import TableAndLineChartReport
from src.views.reports.tree_and_sunburst_report import TreeAndSunburstReport


class NetWorthReportPresenter:
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
        self._main_view.signal_net_worth_accounts_report.connect(
            self._create_accounts_report
        )
        self._main_view.signal_net_worth_asset_type_report.connect(
            self._create_asset_type_report
        )
        self._main_view.signal_net_worth_time_report.connect(self._create_time_report)

    def _create_accounts_report(self) -> None:
        account_items = self._transactions_presenter.checked_account_items
        base_currency = self._record_keeper.base_currency
        data = calculate_accounts_sunburst_data(account_items, base_currency)
        label_text = (
            "NOTE: this chart does not display Accounts and Account Groups with "
            "zero or negative balance."
        )
        self.report = TreeAndSunburstReport(
            "Net Worth Report - Accounts", label_text, self._main_view
        )
        ordered_account_items = sorted(account_items, key=lambda item: item.path)
        self._proxy = QSortFilterProxyModel(self.report)
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._model = AccountTreeModel(self.report.treeView, self._proxy)
        self._model.pre_reset_model()
        self._model.load_data(ordered_account_items, base_currency)
        self._model.post_reset_model()
        self._proxy.setSourceModel(self._model)
        self.report.treeView.setModel(self._proxy)
        self.report.treeView.hideColumn(AccountTreeColumn.SHOW)
        self.report.finalize_setup()

        self.report.load_data(data)
        self.report.show_form()

    def _create_asset_type_report(self) -> None:
        base_currency = self._record_keeper.base_currency
        stats = calculate_asset_stats(self._record_keeper.accounts, base_currency)
        data = calculate_asset_type_sunburst_data(stats)
        label_text = (
            "NOTE: this chart does not display assets with zero or negative balance."
        )
        self.report = TreeAndSunburstReport(
            "Net Worth Report - Asset Types", label_text, self._main_view
        )
        self._proxy = QSortFilterProxyModel(self.report)
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._model = AssetTypeTreeModel(self.report.treeView, self._proxy)
        self._model.pre_reset_model()
        self._model.load_data(stats)
        self._model.post_reset_model()
        self._proxy.setSourceModel(self._model)
        self.report.treeView.setModel(self._proxy)
        self.report.finalize_setup()

        self.report.load_data(data)
        self.report.show_form()

    def _create_time_report(self) -> None:
        account_items = self._transactions_presenter.checked_account_items
        accounts = frozenset(
            account for account in account_items if isinstance(account, Account)
        )
        datetime_filter = (
            self._transactions_presenter.transaction_filter_form_presenter.transaction_filter.datetime_filter
        )
        if datetime_filter.mode != FilterMode.OFF:
            start = datetime_filter.start.date()
            end = datetime_filter.end.date()
        else:
            transactions = self._transactions_presenter.get_visible_transactions()
            transactions = sorted(
                transactions, key=lambda transaction: transaction.timestamp
            )
            start = transactions[0].datetime_.date()
            end = datetime.now(tz=user_settings.settings.time_zone).date()
        base_currency = self._record_keeper.base_currency
        if base_currency is None:
            raise ValueError("Variable 'base_currency' is None.")

        data = calculate_net_worth_over_time(accounts, base_currency, start, end)
        data = [(date, net_worth.value_rounded) for date, net_worth in data]

        self.report = TableAndLineChartReport(
            "Net Worth Report - Asset Types", "", self._main_view
        )
        self._proxy = QSortFilterProxyModel(self.report)
        self._proxy.setSortRole(Qt.ItemDataRole.UserRole)
        self._proxy.setSortCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._model = ValueTableModel(
            self.report.tableView,
            self._proxy,
            ValueType.NET_WORTH,
            base_currency.code,
        )
        self._model.pre_reset_model()
        self._model.load_data(data)
        self._model.post_reset_model()
        self._proxy.setSourceModel(self._model)
        self.report.tableView.setModel(self._proxy)
        self.report.finalize_setup()

        x = []
        y = []
        for date, net_worth in data:
            x.append(date)
            y.append(net_worth)

        places = (
            base_currency.places - 2
            if base_currency.places >= 2  # noqa: PLR2004
            else 0
        )
        format_ = "{x:,." + str(places) + "f}"
        self.report.load_data(
            x,
            y,
            ylabel="Net Worth (CZK)",
            format_=format_,
        )
        self.report.show_form()


def calculate_accounts_sunburst_data(
    account_items: Collection[Account | AccountGroup], base_currency: Currency
) -> tuple:
    balance = 0.0
    tuples = []
    for account in account_items:
        if account.parent is not None:
            continue
        account_item_tuple = create_account_item_tuple(
            account, account_items, base_currency
        )
        if account_item_tuple[1] == 0 and len(account_item_tuple[2]) == 0:
            continue
        balance += account_item_tuple[1]
        tuples.append(account_item_tuple)
    tuples.sort(key=lambda x: abs(x[1]), reverse=True)
    return [("", balance, tuples)]


def create_account_item_tuple(
    account_item: Account,
    account_items: Collection[Account | AccountGroup],
    currency: Currency,
) -> tuple[str, float, list]:
    children_tuples = []
    balance = 0

    if isinstance(account_item, AccountGroup):
        for _account_item in account_items:
            if _account_item in account_item.children:
                child_tuple = create_account_item_tuple(
                    _account_item, account_items, currency
                )
                if child_tuple[1] == 0 and len(child_tuple[2]) == 0:
                    continue
                children_tuples.append(child_tuple)
                balance += child_tuple[1]
    else:
        balance = float(account_item.get_balance(currency).value_rounded)
        balance = balance if balance > 0 else 0

    tuple_ = (
        account_item.name,
        balance,
        children_tuples,
    )

    children_tuples.sort(key=lambda x: abs(x[1]), reverse=True)
    return tuple_


def calculate_asset_type_sunburst_data(stats: Collection[AssetStats]) -> tuple:
    balance = 0.0
    tuples = []
    for item in stats:
        child_tuple = create_asset_tuple(item)
        if child_tuple[1] > 0:
            balance += child_tuple[1]
            tuples.append(child_tuple)
    tuples.sort(key=lambda x: abs(x[1]), reverse=True)
    return [("", balance, tuples)]


def create_asset_tuple(stats: AssetStats) -> tuple[str, float, list]:
    balance = 0
    name = stats.name
    children_tuples = []
    if stats.children:
        for item in stats.children:
            child_tuple = create_asset_tuple(item)
            if child_tuple[1] > 0:
                children_tuples.append(child_tuple)
                balance += child_tuple[1]
    else:
        balance = (
            float(stats.amount_base.value_rounded)
            if stats.amount_base.value_rounded > 0
            else 0
        )
    children_tuples.sort(key=lambda x: abs(x[1]), reverse=True)
    return (name, balance, children_tuples)
