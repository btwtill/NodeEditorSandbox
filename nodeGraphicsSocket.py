from PyQt5.QtCore import QRectF
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem


class QDMGraphicsSocket(QGraphicsItem):
    def __init__(self, parent = None, socketType = 0):
        super().__init__(parent)

        self.radius = 6
        self.outlineWidth = 1
        self.socketType = socketType

        self.colors = [
            QColor("#FFFF7700"),
            QColor("#FF528220"),
            QColor("#FF0056a6"),
            QColor("#FFa86db1"),
            QColor("#FFb54747"),
            QColor("#FFdbe220")
        ]

        self.colorBackground = self.colors[self.socketType]
        self.colorOutline = QColor("#FF000000")

        self.pen = QPen(self.colorOutline)
        self.pen.setWidth(self.outlineWidth)
        self.brush = QBrush(self.colorBackground)

    def paint(self, painter , QStyleOptionGraphicsItem, widget = None):

        painter.setBrush(self.brush)
        painter.setPen(self.pen)

        painter.drawEllipse(-self.radius, -self.radius, 2 * self.radius, 2 * self.radius)

    def boundingRect(self):
        return QRectF(
            -self.radius - self.outlineWidth,
            -self.radius - self.outlineWidth,
            2 * (self.radius + self.outlineWidth),
            2 * (self.radius + self.outlineWidth)
        )