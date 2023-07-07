from collections.abc import Collection

from PyQt6.QtCore import QSignalBlocker, Qt
from PyQt6.QtWidgets import QComboBox, QHBoxLayout, QHeaderView, QWidget
from src.models.statistics.category_stats import CategoryStats
from src.views import icons
from src.views.base_classes.custom_widget import CustomWidget
from src.views.ui_files.reports.Ui_category_report import Ui_CategoryReport
from src.views.widgets.charts.sunburst_chart_widget import (
    SunburstChartWidget,
    SunburstNode,
)


class CategoryReport(CustomWidget, Ui_CategoryReport):
    def __init__(
        self,
        title: str,
        currency_code: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent=parent)
        self.setupUi(self)

        # BUG: figure out why this is needed at all
        font = self.font()
        font_size = font.pointSize()
        tree_font = self.treeView.font()
        tree_font.setPointSize(font_size)
        self.treeView.setFont(tree_font)

        self.setWindowFlag(Qt.WindowType.Window)
        self.setWindowTitle(title)
        self.setWindowIcon(icons.category)
        self.currencyNoteLabel.setText(f"All values in {currency_code}")

        self.chart_widget = SunburstChartWidget(self)
        self.splitter.addWidget(self.chart_widget)

        self.actionExpand_All.setIcon(icons.expand)
        self.actionCollapse_All.setIcon(icons.collapse)

        self.actionExpand_All.triggered.connect(self.treeView.expandAll)
        self.actionCollapse_All.triggered.connect(self.treeView.collapseAll)

        self.expandAllToolButton.setDefaultAction(self.actionExpand_All)
        self.collapseAllToolButton.setDefaultAction(self.actionCollapse_All)

        self.typeComboBox = QComboBox(self)
        self.typeComboBox.addItem("Income")
        self.typeComboBox.addItem("Expense")
        self.typeComboBox.setCurrentText("Income")
        self.typeComboBox.currentTextChanged.connect(self._combobox_text_changed)

        self.periodComboBox = QComboBox(self)
        self.periodComboBox.currentTextChanged.connect(self._combobox_text_changed)

        self.combo_box_horizontal_layout = QHBoxLayout()
        self.combo_box_horizontal_layout.addWidget(self.typeComboBox)
        self.combo_box_horizontal_layout.addWidget(self.periodComboBox)
        self.chart_widget.horizontal_layout.addLayout(self.combo_box_horizontal_layout)

    def finalize_setup(self) -> None:
        for column in range(self.treeView.model().columnCount()):
            self.treeView.header().setSectionResizeMode(
                column, QHeaderView.ResizeMode.ResizeToContents
            )

    def show_form(self) -> None:
        super().show_form()
        width = self.splitter.size().width()
        self.splitter.setSizes([width // 2, width // 2])

    def load_stats(
        self,
        income_periodic_stats: dict[str, Collection[CategoryStats]],
        expense_periodic_stats: dict[str, Collection[CategoryStats]],
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
        data = (
            self._income_periodic_stats
            if type_ == "Income"
            else self._expense_periodic_stats
        )
        selected_period = self.periodComboBox.currentText()
        sunburst_data = _convert_category_stats_to_sunburst_data(data[selected_period])
        self.chart_widget.load_data(sunburst_data)


def _convert_category_stats_to_sunburst_data(
    stats: Collection[CategoryStats],
) -> tuple[SunburstNode]:
    total = sum((stats.balance.value_rounded) for stats in stats)
    no_label_threshold = abs(float(total) * 0.4 / 100)
    balance = 0.0
    level = 1
    children: list[SunburstNode] = []
    for item in stats:
        if item.category.parent is not None:
            continue
        node = _create_node(
            item, stats, no_label_threshold, level + 1, parent_label_visible=True
        )
        balance += node.value
        if abs(node.value) < no_label_threshold:
            node.clear_label()
        children.append(node)
    children.sort(key=lambda x: abs(x.value), reverse=True)
    return (SunburstNode("", balance, children),)


def _create_node(
    stats: CategoryStats,
    all_stats: Collection[CategoryStats],
    no_label_threshold: float,  # abs value
    level: int,
    *,
    parent_label_visible: bool,
) -> SunburstNode:
    node = SunburstNode(
        stats.category.name,
        float(stats.balance.value_rounded),
        [],
    )
    label_visible = abs(node.value) >= no_label_threshold / (level - 1)

    for item in all_stats:
        if item.category in stats.category.children:
            child_node = _create_node(
                item,
                all_stats,
                no_label_threshold,
                level + 1,
                parent_label_visible=label_visible,
            )
            if (
                abs(child_node.value) < no_label_threshold / level
                or not parent_label_visible
                or not label_visible
            ):
                child_node.clear_label()
            node.children.append(child_node)
    node.children.sort(key=lambda x: abs(x.value), reverse=True)
    return node
