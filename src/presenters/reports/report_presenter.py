from datetime import datetime

from src.models.record_keeper import RecordKeeper
from src.presenters.reports.attribute_report_presenter import AttributeReportPresenter
from src.presenters.reports.cash_flow_report_presenter import CashFlowReportPresenter
from src.presenters.reports.category_report_presenter import CategoryReportPresenter
from src.presenters.reports.net_worth_report_presenter import NetWorthReportPresenter
from src.presenters.utilities.event import Event
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.views.main_view import MainView


class ReportPresenter:
    event_update_filter_end_datetime = Event()

    def __init__(
        self,
        main_view: MainView,
        transactions_presenter: TransactionsPresenter,
        record_keeper: RecordKeeper,
    ) -> None:
        self._main_view = main_view
        self._transactions_presenter = transactions_presenter

        self._cash_flow_presenter = CashFlowReportPresenter(
            main_view, transactions_presenter, record_keeper
        )
        self._tag_presenter = AttributeReportPresenter(
            main_view, transactions_presenter, record_keeper
        )
        self._category_presenter = CategoryReportPresenter(
            main_view, transactions_presenter, record_keeper
        )
        self._net_worth_presenter = NetWorthReportPresenter(
            main_view, transactions_presenter, record_keeper
        )
        self._net_worth_presenter.event_update_filter_end_datetime.append(
            self.event_update_filter_end_datetime
        )
        self.load_record_keeper(record_keeper)

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._cash_flow_presenter.load_record_keeper(record_keeper)
        self._tag_presenter.load_record_keeper(record_keeper)
        self._category_presenter.load_record_keeper(record_keeper)
        self._net_worth_presenter.load_record_keeper(record_keeper)

    def update_filter_end_datetime(self, end_date: datetime | None) -> None:
        self._net_worth_presenter.set_filter_end_date(end_date)
