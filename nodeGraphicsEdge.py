from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


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
        if self.posSource[0] > self.posDestination[0]: dist *= -1

        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))

        path.cubicTo(self.posSource[0] + dist, self.posSource[1],
                     self.posDestination[0] - dist, self.posDestination[1],
                     self.posDestination[0], self.posDestination[1])

        self.setPath(path)