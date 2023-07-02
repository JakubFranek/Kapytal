from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QWidget
from src.models.utilities.cashflow_report import CashFlowStats
from src.view_models.cash_flow_table_model import CashFlowTableModel
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.reports.Ui_cash_flow_periodic_report import (
    Ui_CashFlowPeriodicReport,
)
from src.views.widgets.charts.cash_flow_periodic_chart_widget import (
    CashFlowPeriodicChartWidget,
)

MINIMUM_TABLE_HEIGHT = 600
MAXIMUM_TABLE_HEIGHT = 800


class CashFlowPeriodicReport(CustomWidget, Ui_CashFlowPeriodicReport):
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

        self.chart_widget = CashFlowPeriodicChartWidget(self)
        self.chartTabVerticalLayout.addWidget(self.chart_widget)

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
        self.chart_widget.load_data(stats)
        width, height = self._calculate_table_view_size()
        self.resize(width, height)

    def _calculate_table_view_size(self) -> tuple[int, int]:
        """Calculates a good size for the table view which
        should fit it inside the parent widget. Returns (width, height)"""

        table = self.tableView
        horizontal_header_length = table.horizontalHeader().length()
        vertical_header_length = table.verticalHeader().length()
        vertical_header_width = table.verticalHeader().width()
        horizontal_header_height = table.horizontalHeader().height()
        width = horizontal_header_length + vertical_header_width + 140
        height = vertical_header_length + horizontal_header_height + 80
        if height < MINIMUM_TABLE_HEIGHT:
            height = MINIMUM_TABLE_HEIGHT
        elif height > MAXIMUM_TABLE_HEIGHT:
            height = MAXIMUM_TABLE_HEIGHT
        return width, height
