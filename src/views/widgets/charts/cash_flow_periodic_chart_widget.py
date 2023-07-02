import math
from collections.abc import Sequence

import mplcursors
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.container import BarContainer
from matplotlib.text import Annotation
from matplotlib.ticker import StrMethodFormatter
from mplcursors import Selection
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

BAR_WIDTH = 0.2


class CashFlowPeriodicChartWidget(QWidget):
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

    def load_data(self, stats_sequence: Sequence[CashFlowStats]) -> None:
        axes = self.chart.axes
        axes.clear()

        currency = stats_sequence[0].inflows.currency

        incomes = []
        inward_transfers = []
        refunds = []
        expenses = []
        outward_transfers = []
        cash_flow = []
        gain_loss = []
        max_value = 0
        min_value = 0
        for stats in stats_sequence:
            incomes.append(stats.incomes.value_rounded)
            inward_transfers.append(stats.inward_transfers.value_rounded)
            refunds.append(stats.refunds.value_rounded)
            expenses.append(stats.expenses.value_rounded)
            outward_transfers.append(stats.outward_transfers.value_rounded)
            cash_flow.append(stats.delta_neutral.value_rounded)
            gain_loss.append(stats.delta_performance.value_rounded)
            max_value = max(
                stats.inflows.value_rounded,
                stats.outflows.value_rounded,
                stats.delta_neutral.value_rounded,
                stats.delta_performance.value_rounded,
                max_value,
            )
            min_value = min(
                stats.inflows.value_rounded,
                stats.outflows.value_rounded,
                stats.delta_neutral.value_rounded,
                stats.delta_performance.value_rounded,
                min_value,
            )

        refund_bottom = [x + y for x, y in zip(incomes, inward_transfers)]

        x1 = list(range(len(incomes)))
        x2 = [x + BAR_WIDTH for x in x1]
        x3 = [x + BAR_WIDTH for x in x2]
        x4 = [x + BAR_WIDTH for x in x3]
        axes.bar(x1, incomes, width=BAR_WIDTH, color="green", label="Income")
        axes.bar(
            x1,
            inward_transfers,
            width=BAR_WIDTH,
            bottom=incomes,
            color="limegreen",
            label="Inward Transfers",
        )
        axes.bar(
            x1,
            refunds,
            width=BAR_WIDTH,
            bottom=refund_bottom,
            color="lime",
            label="Refunds",
        )
        axes.bar(x2, expenses, width=BAR_WIDTH, color="red", label="Expenses")
        axes.bar(
            x2,
            outward_transfers,
            width=BAR_WIDTH,
            bottom=expenses,
            color="salmon",
            label="Outward Transfers",
        )
        axes.bar(x3, cash_flow, width=BAR_WIDTH, color="royalblue", label="Cash Flow")
        axes.bar(x4, gain_loss, width=BAR_WIDTH, color="orange", label="Gain / Loss")

        axes.set_axisbelow(True)
        axes.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
        axes.grid(visible=True, axis="y")
        axes.set_ylabel(currency.code)
        axes.set_xticks(
            [x + 1.5 * BAR_WIDTH for x in x1],
            [stats.period for stats in stats_sequence],
        )

        yticks = axes.get_yticks()
        step = abs(yticks[1] - yticks[0])
        ymax = math.ceil(float(max_value) / step) * step
        ymin = math.floor(float(min_value) / step) * step
        axes.set_ylim(ymin, ymax)

        def show_annotation(sel: Selection) -> None:
            if type(sel.artist) == BarContainer:
                bar = sel.artist[sel.index]
                annotation: Annotation = sel.annotation
                annotation.set_text(
                    f"{sel.artist.get_label()}: {round(bar.get_height(),currency.places):,.{currency.places}f} {currency.code}"
                )
                annotation.xy = (
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_y() + bar.get_height() / 2,
                )
                annotation.get_bbox_patch().set_alpha(0.8)
            else:
                sel.annotation.remove()

        cursor = mplcursors.cursor(pickables=[axes])
        cursor.connect("add", show_annotation)

        axes.legend()

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
