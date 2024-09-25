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
        return QRectF(0,0,1,1)

    def paint(self, painter, option, widget = None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(self.pen)

        polyline = QPolygonF(self.linePoints)
        painter.drawPolyline(polyline)