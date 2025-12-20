from collections.abc import Sequence
from enum import Enum, auto
from functools import partial
from typing import Any

from PyQt6.QtCharts import (
    QBarCategoryAxis,
    QBarSeries,
    QBarSet,
    QChart,
    QChartView,
    QValueAxis,
)
from PyQt6.QtCore import QMargins, QPointF, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QCursor, QFont, QMouseEvent, QPainter
from PyQt6.QtWidgets import QGraphicsScene, QWidget
from src.models.statistics.cashflow_stats import CashFlowStats
from src.utilities.formatting import format_real
from src.views import colors
from src.views.widgets.charts.general_chart_callout import GeneralChartCallout


class ChartData(Enum):
    ALL = auto()
    INFLOWS = auto()
    OUTFLOWS = auto()
    CASH_FLOW = auto()
    GAIN_LOSS = auto()
    NET_GROWTH = auto()
    SAVINGS_RATE = auto()


class BarSet(QBarSet):
    def __init__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init__(*args, **kwargs)
        self.extra_text: list[str] = []


class CashFlowPeriodicChartView(QChartView):
    signal_mouse_move = pyqtSignal()

    def __init__(self, parent: QWidget | None) -> None:
        super().__init__(parent)

        self.setScene(QGraphicsScene(self))

        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMouseTracking(True)
        self.setRubberBand(QChartView.RubberBand.RectangleRubberBand)

        self.setBackgroundBrush(colors.get_tab_widget_background())

        self._font = QFont()
        self._font.setPointSize(10)

        self._font_bold = QFont()
        self._font_bold.setPointSize(10)
        self._font_bold.setBold(True)

        self._unit = ""
        self._decimals = 0

    def load_data(
        self, stats_sequence: Sequence[CashFlowStats], chart_data: ChartData
    ) -> None:
        if hasattr(self, "_chart"):
            self._chart.removeAllSeries()
        if hasattr(self, "axis_x"):
            self._chart.removeAxis(self.axis_x)
        if hasattr(self, "axis_y"):
            self._chart.removeAxis(self.axis_y)

        if chart_data == ChartData.SAVINGS_RATE:
            self._unit = "%"
        else:
            self._unit = stats_sequence[0].inflows.balance.currency.code
        self._decimals = stats_sequence[0].inflows.balance.currency.decimals

        bar_inflows = BarSet("Inflows")
        bar_inflows.setColor(QColor("darkgreen"))

        bar_outflows = BarSet("Outflows")
        bar_outflows.setColor(QColor("red"))

        bar_cash_flow = BarSet("Cash Flow")
        bar_cash_flow.setColor(QColor("royalblue"))

        bar_gain_loss = BarSet("Total Gain / Loss")
        bar_gain_loss.setColor(QColor("orange"))

        bar_net_growth = BarSet("Net Growth")
        bar_net_growth.setColor(QColor("deeppink"))

        bar_savings_rate = BarSet("Savings Rate")
        bar_savings_rate.setColor(QColor("purple"))

        self.categories = []
        for stats in stats_sequence:
            self.categories.append(stats.period)

            inflows = float(
                stats.incomes.balance.value_rounded
                + stats.inward_transfers.balance.value_rounded
                + stats.refunds.balance.value_rounded
                + stats.initial_balances.value_rounded
            )
            bar_inflows.append(inflows)
            bar_inflows.extra_text.append(
                f"\n\nIncome: {stats.incomes.balance.to_str_rounded()}"
                f"\nInward Transfers: {stats.inward_transfers.balance.to_str_rounded()}"
                f"\nRefunds: {stats.refunds.balance.to_str_rounded()}"
                f"\nInitial Balances: {stats.initial_balances.to_str_rounded()}"
            )

            bar_outflows.append(
                float(stats.expenses.balance.value_rounded)
                + float(stats.outward_transfers.balance.value_rounded)
            )
            bar_outflows.extra_text.append(
                f"\n\nExpenses: {stats.expenses.balance.to_str_rounded()}"
                "\nOutward Transfers: "
                f"{stats.outward_transfers.balance.to_str_rounded()}"
            )

            bar_cash_flow.append(float(stats.delta_neutral.balance.value_rounded))
            bar_gain_loss.append(float(stats.delta_performance.value_rounded))
            bar_net_growth.append(float(stats.delta_total.value_rounded))
            if stats.savings_rate.is_nan():
                bar_savings_rate.append(0)
            else:
                bar_savings_rate.append(100 * float(stats.savings_rate))

        series = QBarSeries()
        if chart_data in {ChartData.ALL, ChartData.INFLOWS}:
            series.append(bar_inflows)
        if chart_data in {ChartData.ALL, ChartData.OUTFLOWS}:
            series.append(bar_outflows)
        if chart_data in {ChartData.ALL, ChartData.CASH_FLOW}:
            series.append(bar_cash_flow)
        if chart_data in {ChartData.ALL, ChartData.GAIN_LOSS}:
            series.append(bar_gain_loss)
        if chart_data == ChartData.NET_GROWTH:
            series.append(bar_net_growth)
        if chart_data == ChartData.SAVINGS_RATE:
            series.append(bar_savings_rate)

        for bar_set in series.barSets():
            bar_set.hovered[bool, int].connect(partial(self.on_hover, bar_set=bar_set))

        if not hasattr(self, "_chart"):
            self._chart = QChart()
        else:
            self.scene().removeItem(self._chart)
        self._chart.setMargins(QMargins(5, 5, 5, 5))
        self._chart.legend().setVisible(True)
        self._chart.legend().setAlignment(Qt.AlignmentFlag.AlignBottom)
        self._chart.legend().setFont(self._font)
        self._chart.addSeries(series)
        self._chart.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)

        self.axis_x = QBarCategoryAxis()
        self.axis_x.setLabelsFont(self._font)
        self.axis_x.setGridLineVisible(False)
        self.axis_x.append(self.categories)
        self._chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
        series.attachAxis(self.axis_x)

        self.axis_y = QValueAxis()
        if chart_data == ChartData.SAVINGS_RATE:
            self.axis_y.setTitleText("Savings Rate [%]")
        else:
            self.axis_y.setTitleText(self._unit)
        self.axis_y.setTitleFont(self._font_bold)
        self.axis_y.setLabelsFont(self._font)
        self._chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
        series.attachAxis(self.axis_y)

        self.signal_mouse_move.connect(self.update_callout)

        self.setChart(self._chart)
        self.scene().addItem(self._chart)

        self._tooltip = GeneralChartCallout(self._chart, QPointF(0, 0))

        self.axis_y.applyNiceNumbers()

    def on_hover(
        self,
        state: bool,  # noqa: FBT001
        index: int,
        bar_set: BarSet,
    ) -> None:
        label = bar_set.label()
        value = bar_set.at(index)

        cursor_pos = QCursor.pos()
        view_pos = self.mapFromGlobal(cursor_pos)
        scene_pos = self.mapToScene(view_pos)

        tooltip_text = (
            f"{self.axis_x.categories()[index]}\n"
            f"{label}: {format_real(value, self._decimals)} {self._unit}"
        )

        if len(bar_set.extra_text) > index and bar_set.extra_text[index]:
            tooltip_text += bar_set.extra_text[index]

        left = index > 0.15 * len(bar_set)

        self._tooltip.set_text(tooltip_text, left=left)
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

    def mouseReleaseEvent(self, event: QMouseEvent | None) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            self.chart().zoomReset()
            self._tooltip.hide()
            return
        self._tooltip.hide()
        super().mouseReleaseEvent(event)
