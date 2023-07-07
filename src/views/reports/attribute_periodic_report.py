from collections.abc import Collection
from typing import TYPE_CHECKING

from PyQt6.QtCore import QSignalBlocker, Qt
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QHeaderView, QWidget
from src.models.statistics.attribute_stats import AttributeStats
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.reports.Ui_attribute_report import (
    Ui_AttributeReport,
)
from src.views.widgets.charts.pie_chart_widget import PieChartWidget

if TYPE_CHECKING:
    from decimal import Decimal


class AttributeReport(CustomWidget, Ui_AttributeReport):
    def __init__(
        self,
        title: str,
        currency_code: str,
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
        self.currencyNoteLabel.setText(f"All values in {currency_code}")

        self.chart_widget = PieChartWidget(self)
        self.splitter.addWidget(self.chart_widget)

        self.typeComboBox = QComboBox(self)
        self.typeComboBox.addItem("Income")
        self.typeComboBox.addItem("Expense")
        self.typeComboBox.setCurrentText("Income")
        self.typeComboBox.currentTextChanged.connect(self._combobox_text_changed)

        self.periodComboBox = QComboBox(self)
        self.periodComboBox.currentTextChanged.connect(self._combobox_text_changed)

        self.combobox_horizontal_layout = QHBoxLayout()
        self.combobox_horizontal_layout.addWidget(self.typeComboBox)
        self.combobox_horizontal_layout.addWidget(self.periodComboBox)
        self.chart_widget.horizontal_layout.addLayout(self.combobox_horizontal_layout)

    def finalize_setup(self) -> None:
        for column in range(self.tableView.model().columnCount()):
            self.tableView.horizontalHeader().setSectionResizeMode(
                column,
                QHeaderView.ResizeMode.ResizeToContents,
            )

    def show_form(self) -> None:
        super().show_form()
        width = self.splitter.size().width()
        self.splitter.setSizes([width // 2, width // 2])

    def load_stats(
        self,
        income_periodic_stats: dict[str, Collection[AttributeStats]],
        expense_periodic_stats: dict[str, Collection[AttributeStats]],
    ) -> None:
        self._income_periodic_stats = income_periodic_stats
        self._expense_periodic_stats = expense_periodic_stats

        periods = list(income_periodic_stats.keys())
        self._setup_comboboxes(periods)

    def _setup_comboboxes(self, periods: Collection[str]) -> None:
        with QSignalBlocker(self.periodComboBox):
            for period in periods:
                self.periodComboBox.addItem(period)
        self.periodComboBox.setCurrentText(periods[-1])

    def _combobox_text_changed(self) -> None:
        type_ = self.typeComboBox.currentText()
        selected_period = self.periodComboBox.currentText()
        _periodic_stats = (
            self._income_periodic_stats
            if type_ == "Income"
            else self._expense_periodic_stats
        )

        data: list[tuple[Decimal, str]] = []
        for item in _periodic_stats[selected_period]:
            data.append((abs(item.balance.value_rounded), item.attribute.name))

        self.chart_widget.load_data(data)
