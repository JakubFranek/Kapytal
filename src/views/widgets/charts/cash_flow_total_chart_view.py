from functools import partial

from PyQt6.QtCharts import (
    QBarCategoryAxis,
    QBarSet,
    QChart,
    QChartView,
    QStackedBarSeries,
    QValueAxis,
)
from PyQt6.QtCore import QMargins, QPointF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QCursor, QFont, QMouseEvent, QPainter
from PyQt6.QtWidgets import QGraphicsScene, QWidget
from src.models.statistics.cashflow_stats import CashFlowStats
from src.utilities.formatting import format_real
from src.views.widgets.charts.general_chart_callout import GeneralChartCallout


class CashFlowTotalChartView(QChartView):
    signal_mouse_move = pyqtSignal()

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMouseTracking(True)

        self._currency_code = ""
        self._decimals = 0

        self._font = QFont()
        self._font.setPointSize(10)

        self._font_bold = QFont()
        self._font_bold.setPointSize(10)
        self._font_bold.setBold(True)

    def load_data(self, stats: CashFlowStats) -> None:  # noqa: PLR0915
        self._currency_code = stats.incomes.balance.currency.code
        self._decimals = stats.incomes.balance.currency.decimals

        bar_income = QBarSet("Income")
        bar_income.setColor(QColor("darkgreen"))
        bar_income.append([float(stats.incomes.balance.value_rounded), 0, 0, 0])

        bar_inward_transfers = QBarSet("Inward Transfers")
        bar_inward_transfers.setColor(QColor("green"))
        bar_inward_transfers.append(
            [float(stats.inward_transfers.balance.value_rounded), 0, 0, 0]
        )

        bar_refunds = QBarSet("Refunds")
        bar_refunds.setColor(QColor("limegreen"))
        bar_refunds.append([float(stats.refunds.balance.value_rounded), 0, 0, 0])

        bar_initial_balances = QBarSet("Initial Balances")
        bar_initial_balances.setColor(QColor("lime"))
        bar_initial_balances.append(
            [float(stats.initial_balances.value_rounded), 0, 0, 0]
        )

        bar_expenses = QBarSet("Expenses")
        bar_expenses.setColor(QColor("red"))
        bar_expenses.append([0, float(stats.expenses.balance.value_rounded), 0, 0])

        bar_outward_transfers = QBarSet("Outward Transfers")
        bar_outward_transfers.setColor(QColor("salmon"))
        bar_outward_transfers.append(
            [0, float(stats.outward_transfers.balance.value_rounded), 0, 0]
        )

        bar_cash_flow = QBarSet("Cash Flow")
        bar_cash_flow.setColor(QColor("royalblue"))
        bar_cash_flow.append(
            [0, 0, float(stats.delta_neutral.balance.value_rounded), 0]
        )

        bar_delta_performance = QBarSet("Total Gain / Loss")
        bar_delta_performance.setColor(QColor("orange"))
        bar_delta_performance.append(
            [0, 0, 0, float(stats.delta_performance.value_rounded)]
        )

        series = QStackedBarSeries()
        series.append(bar_income)
        series.append(bar_inward_transfers)
        series.append(bar_refunds)
        series.append(bar_initial_balances)
        series.append(bar_expenses)
        series.append(bar_outward_transfers)
        series.append(bar_cash_flow)
        series.append(bar_delta_performance)

        for bar_set in series.barSets():
            bar_set.hovered[bool, int].connect(partial(self.on_hover, bar_set=bar_set))

        self._chart = QChart()
        self._chart.setMargins(QMargins(5, 5, 5, 5))
        self._chart.legend().setVisible(True)
        self._chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self._chart.legend().setFont(self._font)
        self._chart.addSeries(series)
        self._chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.categories = ["Inflow", "Outflow", "Cash Flow", "Total Gain / Loss"]
        self.axis_x = QBarCategoryAxis()
        self.axis_x.setLabelsFont(self._font)
        self.axis_x.setGridLineVisible(False)
        self.axis_x.append(self.categories)
        self._chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        self.axis_y.setTitleText(self._currency_code)
        self.axis_y.setTitleFont(self._font_bold)
        self.axis_y.setLabelsFont(self._font)
        self._chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(self.axis_y)

        self.signal_mouse_move.connect(self.update_callout)

        self.setScene(QGraphicsScene(self))
        self.setChart(self._chart)
        self.scene().addItem(self._chart)

        self._tooltip = GeneralChartCallout(self._chart, QPointF(0, 0))

        self.axis_y.applyNiceNumbers()

    def on_hover(
        self,
        state: bool,  # noqa: FBT001
        index: int,
        bar_set: QBarSet,
    ) -> None:
        label = bar_set.label()
        value = bar_set.at(index)

        cursor_pos = QCursor.pos()
        view_pos = self.mapFromGlobal(cursor_pos)
        scene_pos = self.mapToScene(view_pos)

        self._tooltip.set_text(
            f"{label}\n{format_real(value, self._decimals)} {self._currency_code}"
        )
        self._tooltip.set_anchor(scene_pos)
        self._tooltip.setZValue(11)
        self._tooltip.update_geometry()
        if state:
            self._tooltip.show()
        else:
            self._tooltip.hide()

    def update_callout(self) -> None:
        if self._tooltip.isVisible():
            cursor_pos = QCursor.pos()
            view_pos = self.mapFromGlobal(cursor_pos)
            scene_pos = self.mapToScene(view_pos)
            self._tooltip.set_anchor(scene_pos)
            self._tooltip.update_geometry()

    def mouseMoveEvent(self, event: QMouseEvent | None) -> None:
        self.signal_mouse_move.emit()
        return super().mouseMoveEvent(event)
