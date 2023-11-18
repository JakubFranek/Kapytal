import logging
from collections.abc import Collection, Sequence
from datetime import datetime

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication
from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.currency_objects import Currency
from src.models.record_keeper import RecordKeeper
from src.models.statistics.net_worth_stats import (
    AssetStats,
    calculate_asset_stats,
    calculate_net_worth_over_time,
)
from src.models.user_settings import user_settings
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.view_models.account_tree_model import AccountTreeModel
from src.view_models.asset_type_tree_model import AssetTypeTreeModel
from src.view_models.value_table_model import ValueTableModel, ValueType
from src.views.constants import AccountTreeColumn
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.main_view import MainView
from src.views.reports.table_and_line_chart_report import TableAndLineChartReport
from src.views.reports.tree_and_sunburst_report import TreeAndSunburstReport
from src.views.utilities.handle_exception import display_error_message
from src.views.widgets.charts.sunburst_chart_view import SunburstNode


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
            self._create_accounts_report_with_busy_dialog
        )
        self._main_view.signal_net_worth_asset_type_report.connect(
            self._create_asset_type_report_with_busy_dialog
        )
        self._main_view.signal_net_worth_time_report.connect(
            self._create_time_report_with_busy_dialog
        )

    def _create_accounts_report_with_busy_dialog(self) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self._main_view, "Preparing report, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            self._create_accounts_report()
        except:  # noqa: TRY302
            raise
        finally:
            self._busy_dialog.close()

    def _create_asset_type_report_with_busy_dialog(self) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self._main_view, "Preparing report, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            self._create_asset_type_report()
        except:  # noqa: TRY302
            raise
        finally:
            self._busy_dialog.close()

    def _create_time_report_with_busy_dialog(self) -> None:
        self._busy_dialog = create_simple_busy_indicator(
            self._main_view, "Preparing report, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            self._create_time_report()
        except:  # noqa: TRY302
            raise
        finally:
            self._busy_dialog.close()

    def _create_accounts_report(self) -> None:
        logging.debug("Net Worth Accounts Report requested")

        account_items = self._transactions_presenter.checked_account_items
        base_currency = self._record_keeper.base_currency
        if base_currency is None:
            display_error_message(
                "Set a base Currency before running this report.",
                title="Warning",
            )
            return
        if not account_items:
            display_error_message(
                "Select at least one Account before running this report.",
                title="Warning",
            )
            return

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
        logging.debug("Net Worth Asset Type Report requested")

        accounts = self._transactions_presenter.checked_accounts
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

        stats = calculate_asset_stats(accounts, base_currency)
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
        logging.debug("Net Worth Time Report requested")

        account_items = self._transactions_presenter.checked_account_items
        accounts = frozenset(
            account for account in account_items if isinstance(account, Account)
        )
        transactions = self._transactions_presenter.get_visible_transactions()
        transactions = sorted(
            transactions, key=lambda transaction: transaction.timestamp
        )
        if not transactions:
            display_error_message(
                "This report cannot be run because there are no Transactions passing "
                "Transaction filter.",
                title="Warning",
            )
            return
        start = transactions[0].datetime_.date()
        end = datetime.now(tz=user_settings.settings.time_zone).date()

        base_currency = self._record_keeper.base_currency
        if base_currency is None:
            display_error_message(
                "Set a base Currency before running this report.",
                title="Warning",
            )
            return
        if not account_items:
            display_error_message(
                "Select at least one Account before running this report.",
                title="Warning",
            )
            return

        data = calculate_net_worth_over_time(accounts, base_currency, start, end)
        data = [(date, net_worth.value_rounded) for date, net_worth in data]

        label_text = (
            "NOTE: to change the date range, use the Date & Time Filter. "
            "Net Worth is calculated based on Account Filter settings."
        )
        self.report = TableAndLineChartReport(
            "Net Worth Report - Time", label_text, self._main_view
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
        self.report.load_data(
            x,
            y,
            y_label=f"Net Worth [{base_currency.code}]",
            y_unit=base_currency.code,
            y_decimals=places,
        )
        self.report.show_form()


def calculate_accounts_sunburst_data(
    account_items: Collection[Account | AccountGroup], base_currency: Currency
) -> tuple[SunburstNode]:
    balance = 0.0
    level = 1
    nodes: list[SunburstNode] = []
    root_node = SunburstNode(
        "Total", "Total", 0, base_currency.code, base_currency.places, [], None
    )
    for account in account_items:
        if account.parent is not None:
            continue
        child_node = _create_account_item_node(
            account, account_items, base_currency, level + 1, root_node
        )
        if child_node.value == 0 and len(child_node.children) == 0:
            continue
        balance += child_node.value
        nodes.append(child_node)
    nodes.sort(key=lambda x: abs(x.value), reverse=True)
    root_node.children = nodes
    root_node.value = balance
    return (root_node,)


def _create_account_item_node(
    account_item: Account,
    account_items: Collection[Account | AccountGroup],
    currency: Currency,
    level: int,
    parent: SunburstNode,
) -> SunburstNode:
    children: list[SunburstNode] = []
    balance = 0

    node = SunburstNode(
        account_item.name,
        account_item.path,
        0,
        currency.code,
        currency.places,
        [],
        parent,
    )

    if isinstance(account_item, AccountGroup):
        for _account_item in account_items:
            if _account_item in account_item.children:
                child_node = _create_account_item_node(
                    _account_item, account_items, currency, level + 1, node
                )
                if child_node.value == 0 and len(child_node.children) == 0:
                    continue
                children.append(child_node)
                balance += child_node.value
    else:
        balance = float(account_item.get_balance(currency).value_rounded)
        balance = balance if balance > 0 else 0

    children.sort(key=lambda x: abs(x.value), reverse=True)
    node.children = children
    node.value = balance
    return node


def calculate_asset_type_sunburst_data(
    stats: Sequence[AssetStats],
) -> tuple[SunburstNode]:
    try:
        currency = stats[0].amount_base.currency
        currency_code = currency.code
        currency_places = currency.places
    except IndexError:
        currency_code = ""
        currency_places = 0

    balance = 0.0
    level = 1
    children: list[SunburstNode] = []
    root_node = SunburstNode(
        "Total", "Total", 0, currency_code, currency_places, [], None
    )
    for item in stats:
        child_node = _create_asset_node(item, level + 1, root_node)
        if child_node.value > 0:
            balance += child_node.value
            children.append(child_node)
    children.sort(key=lambda x: abs(x.value), reverse=True)
    root_node.children = children
    root_node.value = balance
    return (root_node,)


def _create_asset_node(
    stats: AssetStats, level: int, parent: SunburstNode
) -> SunburstNode:
    balance = 0
    node = SunburstNode(
        stats.name, stats.path, 0, parent.unit, parent.decimals, [], parent
    )
    children: list[SunburstNode] = []
    if stats.children:
        if any(child.amount_base.value_rounded < 0 for child in stats.children):
            balance = float(
                sum(child.amount_base.value_rounded for child in stats.children)
            )
        else:
            for item in stats.children:
                child_node = _create_asset_node(item, level + 1, node)
                children.append(child_node)
                balance += child_node.value
    else:
        balance = (
            float(stats.amount_base.value_rounded)
            if stats.amount_base.value_rounded > 0
            else 0
        )
    children.sort(key=lambda x: abs(x.value), reverse=True)
    node.children = children
    node.value = balance
    return node
