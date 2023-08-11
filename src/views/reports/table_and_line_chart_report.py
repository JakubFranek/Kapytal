from collections.abc import Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.reports.Ui_table_and_line_chart_report import (
    Ui_TableAndLineChartReport,
)
from src.views.widgets.charts.line_chart_widget import LineChartWidget


class TableAndLineChartReport(CustomWidget, Ui_TableAndLineChartReport):
    def __init__(
        self,
        title: str,
        label_text: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle(title)
        self.setWindowIcon(icons.pie_chart)

        self.chart_widget = LineChartWidget(self)
        self.verticalLayout.insertWidget(0, self.chart_widget)

        if label_text:
            self.label.setText(label_text)
        else:
            self.label.hide()

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 0)

    def load_data(
        self,
        x: Sequence,
        y: Sequence,
        title: str = "",
        ylabel: str = "",
        xlabel: str = "",
        format_: str = "",
    ) -> None:
        self.chart_widget.load_data(x, y, title, ylabel, xlabel, format_)

    def finalize_setup(self) -> None:
        self.tableView.horizontalHeader().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.tableView.horizontalHeader().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.tableView.sortByColumn(0, Qt.SortOrder.DescendingOrder)
