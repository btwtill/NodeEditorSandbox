import math

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from nodeSocket import RIGHT_TOP, RIGHT_BOTTOM, LEFT_BOTTOM, LEFT_TOP


EDGE_CP_ROUNDNESS = 100

class QDMGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge
        self.color = QColor("#001000")
        self.colorSelected = QColor("#FFFF7700")

        self.pen = QPen(self.color)
        self.pen.setWidth(2)

        self.penSelected = QPen(self.colorSelected)
        self.penSelected.setWidth(2)

        self.penDragged = QPen(self.color)
        self.penDragged.setWidthF(2.0)
        self.penDragged.setStyle(Qt.PenStyle.DashLine)

        self.setFlag(QGraphicsItem.ItemIsSelectable)

        self.setZValue(-1)

        self.posSource = [0, 0]
        self.posDestination = [200, 100]

    def setSource(self, x, y):
        self.posSource = [x,y]

    def setDestination(self, x,y):
        self.posDestination = [x, y]

    def paint(self, painter, QPainter=None, *args, **kwargs):

        self.updatePath()

        if self.edge.endSocket == None:
            painter.setPen(self.penDragged)
        else:
            painter.setPen(self.pen if not self.isSelected() else self.penSelected)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())

    def updatePath(self):
        #Method to draw the path from a to b
        raise NotImplemented("This method has to to be overriden in a child class")


class QDMGraphicsEdgeDirect(QDMGraphicsEdge):
    def updatePath(self):
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        self.setPath(path)

class QDMGraphicsEdgeBezier(QDMGraphicsEdge):
    def updatePath(self):

        dist = (self.posDestination[0] - self.posSource[0]) * 0.5

        cpxSource = +dist
        cpxDestination = -dist
        cpySource = 0
        cpyDestination = 0

        startSocketPosition = self.edge.startSocket.position

        if self.posSource[0] > self.posDestination[0] and startSocketPosition in (RIGHT_TOP, RIGHT_BOTTOM) or self.posSource[0] < self.posDestination[0] and startSocketPosition in (LEFT_BOTTOM, LEFT_TOP):
            cpxDestination *= -1
            cpxSource *= -1

            cpyDestination = (
                    (self.posSource[1] - self.posDestination[1]) / math.fabs(
                (self.posSource[1] - self.posDestination[1]) if (self.posSource[1] - self.posDestination[1]) != 0 else 0.00001
                )
            ) * EDGE_CP_ROUNDNESS

            cpySource = (
                    (self.posDestination[1] - self.posSource[1]) / math.fabs(
                (self.posDestination[1] - self.posSource[1]) if (self.posDestination[1] - self.posSource[1]) != 0 else 0.00001
                )
            ) * EDGE_CP_ROUNDNESS




        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))

        path.cubicTo(self.posSource[0] + cpxSource, self.posSource[1] + cpySource,
                     self.posDestination[0] + cpxDestination, self.posDestination[1] + cpyDestination,
                     self.posDestination[0], self.posDestination[1])

        self.setPath(path)