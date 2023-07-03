from collections.abc import Collection

from src.models.base_classes.account import Account
from src.models.model_objects.account_group import AccountGroup
from src.models.model_objects.currency_objects import Currency
from src.models.record_keeper import RecordKeeper
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.views.main_view import MainView
from src.views.reports.sunburst_report import SunburstReport


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

    def _create_accounts_report(self) -> None:
        account_items = self._transactions_presenter.checked_account_items
        base_currency = self._record_keeper.base_currency
        data = calculate_accounts_sunburst_data(account_items, base_currency)
        label_text = (
            "NOTE: this report ignores all Accounts and Account Groups with "
            "zero or negative balance."
        )
        self.report = SunburstReport(
            "Net Worth Report - Accounts", label_text, self._main_view
        )
        self.report.load_data(data)
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
