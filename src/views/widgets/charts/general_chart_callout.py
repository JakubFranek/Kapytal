from PyQt6.QtCore import QPointF, QRect, QRectF, Qt
from PyQt6.QtGui import (
    QColor,
    QFont,
    QFontMetrics,
    QPainter,
    QPainterPath,
)
from PyQt6.QtWidgets import (
    QGraphicsItem,
    QStyleOptionGraphicsItem,
    QWidget,
)


class GeneralChartCallout(QGraphicsItem):
    def __init__(
        self, parent: QWidget | None = None, local_anchor: QPointF | None = None
    ) -> None:
        super().__init__(parent)
        self._text = ""
        self._textRect = QRectF()
        self._global_anchor = QPointF()
        self._local_anchor = (
            local_anchor if local_anchor is not None else QPointF(-10, -10)
        )
        self._font = QFont()
        self._rect = QRectF()
        self.setVisible(False)

    def boundingRect(self):  # noqa: ANN201
        anchor = self._local_anchor
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
        local_anchor = self._local_anchor
        x = local_anchor.x()
        y = local_anchor.y()
        if not self._rect.contains(local_anchor) and not self._global_anchor.isNull():
            path = QPainterPath()
            path.addRoundedRect(self._rect, 5, 5)
            point1 = QPointF()
            point2 = QPointF()

            # establish the position of the anchor point in relation to _rect
            above = local_anchor.y() <= self._rect.top()
            above_center = (
                local_anchor.y() > self._rect.top()
                and local_anchor.y() <= self._rect.center().y()
            )
            below_center = (
                local_anchor.y() > self._rect.center().y()
                and local_anchor.y() <= self._rect.bottom()
            )
            below = local_anchor.y() > self._rect.bottom()

            on_left = local_anchor.x() <= self._rect.left()
            left_of_center = (
                local_anchor.x() > self._rect.left()
                and local_anchor.x() <= self._rect.center().x()
            )
            right_of_center = (
                local_anchor.x() > self._rect.center().x()
                and local_anchor.x() <= self._rect.right()
            )
            on_right = local_anchor.x() > self._rect.right()

            # get the nearest _rect corner.
            x = (
                self._rect.topLeft().x()
                + (on_right + right_of_center) * self._rect.width()
            )
            y = self._rect.topLeft().y() + (below + below_center) * self._rect.height()
            corner_case = (
                (above and on_left)
                or (above and on_right)
                or (below and on_left)
                or (below and on_right)
            )
            vertical = abs(local_anchor.x() - x) > abs(local_anchor.y() - y)

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
            path.lineTo(local_anchor)
            path.lineTo(point2)
            path = path.simplified()

            painter.setBrush(QColor(255, 255, 255))
            painter.setPen(QColor(0, 0, 0))
            painter.setFont(self._font)
            painter.drawPath(path)
            painter.drawText(self._textRect, self._text)

    def set_text(self, text: str, *, left: bool = True) -> None:
        self._text = text
        metrics = QFontMetrics(self._font)
        self._textRect = QRectF(
            metrics.boundingRect(
                QRect(0, 0, 150, 150), Qt.AlignmentFlag.AlignLeft, self._text
            )
        )
        # QFontMetrics.boundingRect is broken, extra padding is needed
        # more vertical padding is needed for taller text rectangles
        self._textRect.adjust(0, 0, 15, int(self._textRect.height() / 8))

        if not left:
            self._textRect.moveTopLeft(QPointF(20, -self._textRect.height() - 10))
        else:
            self._textRect.translate(
                -self._textRect.width() - 20, -self._textRect.height() - 10
            )
        self.prepareGeometryChange()
        self._rect = self._textRect.adjusted(-5, -5, 5, 5)

    def set_anchor(self, point: QPointF) -> None:
        self._global_anchor = QPointF(point)

    def update_geometry(self) -> None:
        self.prepareGeometryChange()
        self.setPos(self._global_anchor)
