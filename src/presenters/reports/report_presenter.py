from src.models.record_keeper import RecordKeeper
from src.presenters.reports.attribute_report_presenter import AttributeReportPresenter
from src.presenters.reports.cash_flow_report_presenter import CashFlowReportPresenter
from src.presenters.widget.transactions_presenter import TransactionsPresenter
from src.views.main_view import MainView


class ReportPresenter:
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

        self.load_record_keeper(record_keeper)

    def load_record_keeper(self, record_keeper: RecordKeeper) -> None:
        self._cash_flow_presenter.load_record_keeper(record_keeper)
        self._tag_presenter.load_record_keeper(record_keeper)
