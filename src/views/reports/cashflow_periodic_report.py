from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QWidget
from src.models.utilities.cashflow_report import CashFlowStats
from src.view_models.cash_flow_table_model import CashFlowTableModel
from src.views import colors, icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.reports.Ui_cash_flow_period_report import (
    Ui_CashFlowPeriodReport,
)
from src.views.widgets.charts.cash_flow_overall_chart_widget import (
    CashFlowOverallChartWidget,
)


class CashFlowPeriodicReport(CustomWidget, Ui_CashFlowPeriodReport):
    def __init__(
        self,
        period: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)
        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle(f"Cash Flow Report - {period}")
        self.setWindowIcon(icons.bar_chart)

        # self.chart_widget = CashFlowOverallChartWidget(self)
        # self.horizontalLayout.addWidget(self.chart_widget)

        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self._table_model = CashFlowTableModel(self.tableView, self._proxy_model)
        self._proxy_model.setSourceModel(self._table_model)
        self.tableView.setModel(self._proxy_model)
        self.tableView.horizontalHeader().setSortIndicatorClearable(True)

    def load_stats(self, stats: CashFlowStats) -> None:
        self._table_model.pre_reset_model()
        self._table_model.load_cash_flow_stats(stats)
        self._table_model.post_reset_model()
        self.tableView.resizeColumnsToContents()
        self.tableView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)
        # self.chart_widget.load_data(stats)
