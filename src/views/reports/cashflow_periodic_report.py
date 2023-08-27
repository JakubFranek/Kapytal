from collections.abc import Collection

from PyQt6.QtCore import QSortFilterProxyModel, Qt
from PyQt6.QtWidgets import QApplication, QComboBox, QWidget
from src.models.statistics.cashflow_stats import CashFlowStats
from src.presenters.utilities.handle_exception import handle_exception
from src.view_models.cash_flow_table_model import CashFlowTableModel
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.dialogs.busy_dialog import create_simple_busy_indicator
from src.views.ui_files.reports.Ui_cash_flow_periodic_report import (
    Ui_CashFlowPeriodicReport,
)
from src.views.widgets.charts.cash_flow_periodic_chart_widget import (
    CashFlowPeriodicChartWidget,
    ChartData,
)

STR_TO_CHART_DATA = {
    "All data": ChartData.ALL,
    "Inflows": ChartData.INFLOWS,
    "Outflows": ChartData.OUTFLOWS,
    "Cash Flow": ChartData.CASH_FLOW,
    "Total Gain / Loss": ChartData.GAIN_LOSS,
    "Net Growth": ChartData.NET_GROWTH,
    "Savings Rate": ChartData.SAVINGS_RATE,
}

MINIMUM_TABLE_HEIGHT = 600
MAXIMUM_TABLE_HEIGHT = 800


class CashFlowPeriodicReport(CustomWidget, Ui_CashFlowPeriodicReport):
    def __init__(
        self,
        title: str,
        currency_code: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle(title)
        self.setWindowIcon(icons.bar_chart)

        self.currencyNoteLabel.setText(f"All values in {currency_code}")

        self.chart_widget = CashFlowPeriodicChartWidget(self)
        self.chartTabVerticalLayout.addWidget(self.chart_widget)

        self._proxy_model = QSortFilterProxyModel(self)
        self._proxy_model.setSortRole(Qt.ItemDataRole.UserRole)
        self._table_model = CashFlowTableModel(self.tableView, self._proxy_model)
        self._proxy_model.setSourceModel(self._table_model)
        self.tableView.setModel(self._proxy_model)
        self.tableView.horizontalHeader().setSortIndicatorClearable(True)

        self.dataSelectorComboBox = QComboBox(self)
        self.dataSelectorComboBox.addItem("All data")
        self.dataSelectorComboBox.addItem("Inflows")
        self.dataSelectorComboBox.addItem("Outflows")
        self.dataSelectorComboBox.addItem("Cash Flow")
        self.dataSelectorComboBox.addItem("Total Gain / Loss")
        self.dataSelectorComboBox.addItem("Net Growth")
        self.dataSelectorComboBox.addItem("Savings Rate")
        self.dataSelectorComboBox.setCurrentText("All data")
        self.dataSelectorComboBox.currentTextChanged.connect(
            lambda: self._combobox_text_changed(show_busy_indicator=True)
        )  # show busy indicator when combo box has been changed by user
        self.chart_widget.horizontal_layout.addWidget(self.dataSelectorComboBox)

    def load_stats(self, stats: Collection[CashFlowStats]) -> None:
        self._table_model.pre_reset_model()
        self._table_model.load_cash_flow_stats(stats)
        self._table_model.post_reset_model()
        self.tableView.resizeColumnsToContents()
        self.tableView.sortByColumn(-1, Qt.SortOrder.AscendingOrder)

        self._stats = stats
        # don't show busy indicator when loading report
        self._combobox_text_changed(show_busy_indicator=False)

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

    def _combobox_text_changed(self, *, show_busy_indicator: bool) -> None:
        if not show_busy_indicator:
            chart_data = STR_TO_CHART_DATA[self.dataSelectorComboBox.currentText()]
            self.chart_widget.load_data(
                self._stats[:-1], chart_data  # pass stats without Total
            )
            return

        self._busy_dialog = create_simple_busy_indicator(
            self, "Redrawing chart, please wait..."
        )
        self._busy_dialog.open()
        QApplication.processEvents()
        try:
            chart_data = STR_TO_CHART_DATA[self.dataSelectorComboBox.currentText()]
            self.chart_widget.load_data(
                self._stats[:-1], chart_data  # pass stats without Total
            )
        except Exception as exception:  # noqa: BLE001
            handle_exception(exception)
        finally:
            self._busy_dialog.close()
