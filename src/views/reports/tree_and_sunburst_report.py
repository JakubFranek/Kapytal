from collections.abc import Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.reports.Ui_tree_and_sunburst_report import (
    Ui_TreeAndSunburstReport,
)
from src.views.widgets.charts.sunburst_chart_view import SunburstChartView, SunburstNode


class TreeAndSunburstReport(CustomWidget, Ui_TreeAndSunburstReport):
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

        self.chart_widget = SunburstChartView(self, clickable_slices=False)
        self.verticalLayout.insertWidget(0, self.chart_widget)

        if label_text:
            self.label.setText(label_text)
        else:
            self.label.hide()

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 0)

        self.actionExpand_All.setIcon(icons.expand)
        self.actionCollapse_All.setIcon(icons.collapse)
        self.actionExpand_All.triggered.connect(self.treeView.expandAll)
        self.actionCollapse_All.triggered.connect(self.treeView.collapseAll)
        self.expandAllToolButton.setDefaultAction(self.actionExpand_All)
        self.collapseAllToolButton.setDefaultAction(self.actionCollapse_All)

    def load_data(self, data: Sequence[SunburstNode]) -> None:
        self.chart_widget.load_data(data)

    def finalize_setup(self) -> None:
        self.treeView.header().setSectionResizeMode(
            0,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            1,
            QHeaderView.ResizeMode.ResizeToContents,
        )
        self.treeView.header().setSectionResizeMode(
            2,
            QHeaderView.ResizeMode.ResizeToContents,
        )

        self.treeView.sortByColumn(2, Qt.SortOrder.DescendingOrder)
