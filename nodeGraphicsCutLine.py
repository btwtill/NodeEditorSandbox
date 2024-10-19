from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class QDMCutLine(QGraphicsItem):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.linePoints = []
        self.pen = QPen(Qt.GlobalColor.white)
        self.pen.setWidthF(2.0)
        self.pen.setDashPattern([3, 3])

        self.setZValue(2)

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        polygon = QPolygonF(self.linePoints)

        if len(self.linePoints) > 1:
            path = QPainterPath(self.linePoints[0])
            for pt in self.linePoints[1:]:
                path.lineTo(pt)
        else:
            path = QPainterPath(QPointF(0, 0))
            path.lineTo(QPoint(1,1))

        return path

    def paint(self, painter, option, widget = None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(self.pen)

        polyline = QPolygonF(self.linePoints)
        painter.drawPolyline(polyline)