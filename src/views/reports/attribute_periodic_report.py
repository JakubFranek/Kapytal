from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QHeaderView, QWidget
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.reports.Ui_attribute_periodic_report import (
    Ui_AttributePeriodicReport,
)


class AttributePeriodicReport(CustomWidget, Ui_AttributePeriodicReport):
    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        font = self.font()
        font_size = font.pointSize()
        table_font = self.tableView.font()
        table_font.setPointSize(font_size)
        self.tableView.setFont(table_font)

        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle(title)
        self.setWindowIcon(icons.bar_chart)

    def finalize_setup(self) -> None:
        for column in range(self.tableView.model().columnCount()):
            self.tableView.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )
