import math
from collections.abc import Collection

import mplcursors
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.dates import DateFormatter
from matplotlib.ticker import StrMethodFormatter
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QSizePolicy,
    QSpacerItem,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from src.models.utilities.cashflow_report import CashFlowStats
from src.views import icons
from src.views.widgets.charts.canvas import Canvas

x_labels = ["Inflows", "Outflows", "Cash Flow", "Gain / Loss"]


class CashFlowOverallChartWidget(QWidget):
    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.horizontal_layout = QHBoxLayout()

        self.chart = Canvas()
        self.chart.axes.figure.set_layout_engine("tight")
        self.chart_toolbar = NavigationToolbar2QT(self.chart, None)

        self.vertical_layout = QVBoxLayout(self)
        self.vertical_layout.addLayout(self.horizontal_layout)
        self.vertical_layout.addWidget(self.chart)

        self._initialize_toolbar_buttons()
        self._initialize_toolbar_actions()

    def load_data(self, stats: CashFlowStats) -> None:
        self.chart.axes.clear()
        bar_incomes = self.chart.axes.bar(
            "Inflows", stats.incomes.value_rounded, color="green"
        )
        bar_inward_transfers = self.chart.axes.bar(
            "Inflows",
            stats.inward_transfers.value_rounded,
            bottom=stats.incomes.value_rounded,
            color="limegreen",
        )
        bar_refunds = self.chart.axes.bar(
            "Inflows",
            stats.refunds.value_rounded,
            bottom=stats.incomes.value_rounded + stats.inward_transfers.value_rounded,
            color="lime",
        )

        bar_expenses = self.chart.axes.bar(
            "Outflows", stats.expenses.value_rounded, color="red"
        )
        bar_outward_transfers = self.chart.axes.bar(
            "Outflows",
            stats.outward_transfers.value_rounded,
            bottom=stats.expenses.value_rounded,
            color="salmon",
        )

        bar_cash_flow = self.chart.axes.bar(
            "Cash Flow", stats.delta_neutral.value_rounded, color="royalblue"
        )

        bar_delta_performance = self.chart.axes.bar(
            "Gain / Loss",
            stats.delta_performance.value_rounded,
            color="orange",
        )

        self.chart.axes.bar_label(
            bar_refunds, labels=[f"{stats.inflows.value_rounded:,}"]
        )
        self.chart.axes.bar_label(
            bar_outward_transfers, labels=[f"{stats.outflows.value_rounded:,}"]
        )
        self.chart.axes.bar_label(
            bar_cash_flow, labels=[f"{stats.delta_neutral.value_rounded:,}"]
        )
        self.chart.axes.bar_label(
            bar_delta_performance, labels=[f"{stats.delta_performance.value_rounded:,}"]
        )

        self.chart.axes.set_axisbelow(True)
        self.chart.axes.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        self.chart.axes.grid(visible=True, axis="y")

        self.chart.axes.legend(
            bar_incomes.patches
            + bar_inward_transfers.patches
            + bar_refunds.patches
            + bar_expenses.patches
            + bar_outward_transfers.patches
            + bar_cash_flow.patches
            + bar_delta_performance.patches,
            [
                "Income",
                "Inward Transfers",
                "Refunds",
                "Expenses",
                "Outward Transfers",
                "Cash Flow",
                "Gain / Loss",
            ],
        )

        max_value = max(
            stats.inflows,
            stats.outflows,
            stats.delta_neutral,
            stats.delta_performance,
        )
        min_value = min(
            stats.inflows,
            stats.outflows,
            stats.delta_neutral,
            stats.delta_performance,
        )
        yticks = self.chart.axes.get_yticks()
        step = abs(yticks[1] - yticks[0])
        ymax = math.ceil(float(max_value.value_rounded) / step) * step
        ymin = math.floor(float(min_value.value_rounded) / step) * step
        self.chart.axes.set_ylim(ymin, ymax)
        self.chart.axes.set_ylabel(stats.inflows.currency.code)

    def _initialize_toolbar_buttons(self) -> None:
        self.homeToolButton = QToolButton(self)
        self.backToolButton = QToolButton(self)
        self.forwardToolButton = QToolButton(self)
        self.panToolButton = QToolButton(self)
        self.zoomToolButton = QToolButton(self)
        self.subplotsToolButton = QToolButton(self)
        self.customizeToolButton = QToolButton(self)
        self.saveToolButton = QToolButton(self)

        self.horizontal_spacer = QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontal_layout.addWidget(self.homeToolButton)
        self.horizontal_layout.addWidget(self.backToolButton)
        self.horizontal_layout.addWidget(self.forwardToolButton)
        self.horizontal_layout.addWidget(self.panToolButton)
        self.horizontal_layout.addWidget(self.zoomToolButton)
        self.horizontal_layout.addWidget(self.subplotsToolButton)
        self.horizontal_layout.addWidget(self.customizeToolButton)
        self.horizontal_layout.addWidget(self.saveToolButton)
        self.horizontal_layout.addItem(self.horizontal_spacer)

        self.layout().setContentsMargins(0, 0, 0, 0)

    def _initialize_toolbar_actions(self) -> None:
        self.chart_toolbar = NavigationToolbar2QT(self.chart, None)
        self.actionHome = QAction(icons.home, "Reset Chart", self)
        self.actionBack = QAction(icons.arrow_left, "Back", self)
        self.actionForward = QAction(icons.arrow_right, "Forward", self)
        self.actionPan = QAction(icons.arrow_move, "Pan", self)
        self.actionZoom = QAction(icons.magnifier, "Zoom", self)
        self.actionSubplots = QAction(icons.slider, "Subplots", self)
        self.actionCustomize = QAction(icons.settings, "Customize", self)
        self.actionSave = QAction(icons.disk, "Save", self)
        self.actionHome.triggered.connect(self.chart_toolbar.home)
        self.actionBack.triggered.connect(self.chart_toolbar.back)
        self.actionForward.triggered.connect(self.chart_toolbar.forward)
        self.actionPan.triggered.connect(self._pan_triggered)
        self.actionZoom.triggered.connect(self._zoom_triggered)
        self.actionSubplots.triggered.connect(self.chart_toolbar.configure_subplots)
        self.actionCustomize.triggered.connect(self.chart_toolbar.edit_parameters)
        self.actionSave.triggered.connect(self.chart_toolbar.save_figure)
        self.actionPan.setCheckable(True)
        self.actionZoom.setCheckable(True)
        self.homeToolButton.setDefaultAction(self.actionHome)
        self.backToolButton.setDefaultAction(self.actionBack)
        self.forwardToolButton.setDefaultAction(self.actionForward)
        self.panToolButton.setDefaultAction(self.actionPan)
        self.zoomToolButton.setDefaultAction(self.actionZoom)
        self.subplotsToolButton.setDefaultAction(self.actionSubplots)
        self.customizeToolButton.setDefaultAction(self.actionCustomize)
        self.saveToolButton.setDefaultAction(self.actionSave)

    def _pan_triggered(self) -> None:
        if self.actionZoom.isChecked():
            self.actionZoom.setChecked(False)
        self.chart_toolbar.pan()

    def _zoom_triggered(self) -> None:
        if self.actionPan.isChecked():
            self.actionPan.setChecked(False)
        self.chart_toolbar.zoom()
