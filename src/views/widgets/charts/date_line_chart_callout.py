from PyQt6.QtCharts import QChart, QDateTimeAxis
from PyQt6.QtCore import QPoint, QPointF, QRect, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QPainter,
    QPainterPath,
)
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QGraphicsSceneMouseEvent,
    QStyleOptionGraphicsItem,
    QWidget,
)


class DateLineChartCallout(QGraphicsItem):
    def __init__(self, chart: QChart) -> None:
        super().__init__(chart)
        self._chart = chart
        self._text = ""
        self._textRect = QRectF()
        self._anchor = QPointF()
        self._font = QFont()
        self._rect = QRectF()

    def boundingRect(self) -> QRectF:
        anchor = self.mapFromParent(self._chart.mapToPosition(self._anchor))
        rect = QRectF()
        rect.setLeft(min(self._rect.left(), anchor.x()))
        rect.setRight(max(self._rect.right(), anchor.x()))
        rect.setTop(min(self._rect.top(), anchor.y()))
        rect.setBottom(max(self._rect.bottom(), anchor.y()))

        return rect

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionGraphicsItem,  # noqa: ARG002
        widget: QWidget,  # noqa: ARG002
    ) -> None:
        path = QPainterPath()
        path.addRoundedRect(self._rect, 5, 5)
        anchor = self.mapFromParent(self._chart.mapToPosition(self._anchor))
        if not self._rect.contains(anchor) and not self._anchor.isNull():
            point1 = QPointF()
            point2 = QPointF()

            # establish the position of the anchor point in relation to _rect
            above = anchor.y() <= self._rect.top()
            above_center = (
                anchor.y() > self._rect.top() and anchor.y() <= self._rect.center().y()
            )
            below_center = (
                anchor.y() > self._rect.center().y()
                and anchor.y() <= self._rect.bottom()
            )
            below = anchor.y() > self._rect.bottom()

            on_left = anchor.x() <= self._rect.left()
            left_of_center = (
                anchor.x() > self._rect.left() and anchor.x() <= self._rect.center().x()
            )
            right_of_center = (
                anchor.x() > self._rect.center().x()
                and anchor.x() <= self._rect.right()
            )
            on_right = anchor.x() > self._rect.right()

            # get the nearest _rect corner.
            x = (on_right + right_of_center) * self._rect.width() + self._rect.left()
            y = (below + below_center) * self._rect.height() + self._rect.top()
            corner_case = (
                (above and on_left)
                or (above and on_right)
                or (below and on_left)
                or (below and on_right)
            )
            vertical = abs(anchor.x() - x) > abs(anchor.y() - y)

            x1 = (
                x
                + left_of_center * 10
                - right_of_center * 20
                + corner_case * int(not vertical) * (on_left * 10 - on_right * 20)
            )
            y1 = (
                y
                + above_center * 10
                - below_center * 20
                + corner_case * vertical * (above * 10 - below * 20)
            )
            point1.setX(x1)
            point1.setY(y1)

            x2 = (
                x
                + left_of_center * 20
                - right_of_center * 10
                + corner_case * int(not vertical) * (on_left * 20 - on_right * 10)
            )
            y2 = (
                y
                + above_center * 20
                - below_center * 10
                + corner_case * vertical * (above * 20 - below * 10)
            )
            point2.setX(x2)
            point2.setY(y2)

            path.moveTo(point1)
            path.lineTo(anchor)
            path.lineTo(point2)
            path = path.simplified()

        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(self._font)
        painter.drawPath(path)
        painter.drawText(self._textRect, self._text)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        event.setAccepted(True)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.setPos(
                self.mapToParent(
                    event.pos() - event.buttonDownPos(Qt.MouseButton.LeftButton)
                )
            )
            event.setAccepted(True)
        else:
            event.setAccepted(False)

    def set_text(self, text: str) -> None:
        self._text = text
        metrics = QFontMetrics(self._font)
        self._textRect = QRectF(
            metrics.boundingRect(
                QRect(0, 0, 150, 150), Qt.AlignmentFlag.AlignLeft, self._text
            )
        )
        # QFontMetrics.boundingRect is broken, extra padding is needed
        self._textRect.adjust(0, 0, 10, 2)

        x_axis: QDateTimeAxis = self._chart.axes(Qt.Orientation.Horizontal)[0]
        x_min = x_axis.min().toMSecsSinceEpoch()
        x_max = x_axis.max().toMSecsSinceEpoch()
        x_anchor = self._anchor.x()

        # if the anchor point is close to the left edge of the chart,
        # move text rectangle to the right
        if abs(x_anchor - x_max) < 4 * abs(x_anchor - x_min):
            self._textRect.translate(
                -self._textRect.width() - 20, -self._textRect.height() - 10
            )
        else:
            self._textRect.moveTopLeft(QPointF(20, -self._textRect.height() - 10))

        self.prepareGeometryChange()
        self._rect = self._textRect.adjusted(-5, -5, 5, 5)

    def set_anchor(self, point: QPoint) -> None:
        self._anchor = QPointF(point)

    def update_geometry(self) -> None:
        self.prepareGeometryChange()
        self.setPos(self._chart.mapToPosition(self._anchor))
