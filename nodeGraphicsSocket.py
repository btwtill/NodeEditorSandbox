from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QGraphicsItem


SOCKET_COLOR = [
    QColor("#FFFF7700"),
    QColor("#FF528220"),
    QColor("#FF0056a6"),
    QColor("#FFa86db1"),
    QColor("#FFb54747"),
    QColor("#FFdbe220")
]

class QDMGraphicsSocket(QGraphicsItem):
    def __init__(self, socket):
        super().__init__(socket.node.grNode)

        self.socket = socket

        self.radius = 6
        self.outlineWidth = 1

        self.initGraphicsAssets()

    @property
    def socketType(self):
        return self.socket.socketType

    def getSocketColor(self, key):
        if type(key) == int : return SOCKET_COLOR[key]
        if type(key) == str : return QColor(key)
        return Qt.transparent

    def changeSocketType(self):

        self.colorBackground = self.getSocketColor(self.socketType)
        self.brush = QBrush(self.colorBackground)
        self.update()

    def initGraphicsAssets(self):
        self.colorBackground = self.getSocketColor(self.socketType)
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
