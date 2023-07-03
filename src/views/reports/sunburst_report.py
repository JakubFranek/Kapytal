from collections.abc import Sequence

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.reports.Ui_sunburst_report import Ui_SunburstReport
from src.views.widgets.charts.sunburst_chart_widget import SunburstChartWidget


class SunburstReport(CustomWidget, Ui_SunburstReport):
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
        self.setWindowIcon(icons.bar_chart)

        self.chart_widget = SunburstChartWidget(self)
        self.verticalLayout.insertWidget(0, self.chart_widget)

        if label_text:
            self.label.setText(label_text)
        else:
            self.label.hide()

        self.verticalLayout.setStretch(0, 1)
        self.verticalLayout.setStretch(1, 0)

    def load_data(self, data: Sequence) -> None:
        self.chart_widget.load_data(data)
