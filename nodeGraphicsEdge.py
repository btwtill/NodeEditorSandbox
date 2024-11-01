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

        self._lastSelectedState = False

        self.posSource = [0, 0]
        self.posDestination = [200, 100]

        self.initGraphicElements()
        self.initUI()

    def initUI(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setZValue(-1)

    def initGraphicElements(self):
        self.color = QColor("#001000")
        self.colorSelected = QColor("#FFFF7700")

        self.pen = QPen(self.color)
        self.pen.setWidth(2)

        self.penSelected = QPen(self.colorSelected)
        self.penSelected.setWidth(2)

        self.penDragged = QPen(self.color)
        self.penDragged.setWidthF(2.0)
        self.penDragged.setStyle(Qt.PenStyle.DashLine)

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self.calculatePath()

    def paint(self, painter, QPainter=None, *args, **kwargs):
        self.setPath(self.calculatePath())
        self.calculatePath()

        if self.edge.endSocket == None:
            painter.setPen(self.penDragged)
        else:
            painter.setPen(self.pen if not self.isSelected() else self.penSelected)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self.path())

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self._lastSelectedState != self.isSelected():
            self.edge.scene.resetLastSelectedStates()
            self._lastSelectedState = self.isSelected()
            self.onSelected()

    def calculatePath(self):
        #Method to draw the path from a to b
        raise NotImplemented("This method has to to be overriden in a child class")

    def onSelected(self):
        self.edge.scene.grScene.itemsSelected.emit()

    def intersectsWith(self, p1, p2):
        cutpath = QPainterPath(p1)
        cutpath.lineTo(p2)
        path = self.calculatePath()
        return cutpath.intersects(path)

    def setSource(self, x, y):
        self.posSource = [x,y]

    def setDestination(self, x,y):
        self.posDestination = [x, y]


class QDMGraphicsEdgeDirect(QDMGraphicsEdge):
    def calculatePath(self):
        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))
        path.lineTo(self.posDestination[0], self.posDestination[1])
        return path

class QDMGraphicsEdgeBezier(QDMGraphicsEdge):
    def calculatePath(self):

        dist = (self.posDestination[0] - self.posSource[0]) * 0.5

        cpxSource = +dist
        cpxDestination = -dist
        cpySource = 0
        cpyDestination = 0

        if self.edge.startSocket is not None:
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

        return path