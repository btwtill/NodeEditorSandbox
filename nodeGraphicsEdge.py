import math

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from nodeSocket import RIGHT_TOP, RIGHT_BOTTOM, LEFT_BOTTOM, LEFT_TOP

DEBUG = False

EDGE_CP_ROUNDNESS = 100

class QDMGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge

        self._lastSelectedState = False
        self.hovered = False

        self.posSource = [0, 0]
        self.posDestination = [200, 100]

        self.initGraphicElements()
        self.initUI()

    def initUI(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)

        self.setZValue(-1)

    def initGraphicElements(self):
        self.color = self.defaultColor = QColor("#001000")
        self.colorSelected = QColor("#FFFF7700")
        self.colorHovered = QColor("#FFFFAA39")

        self.pen = QPen(self.color)
        self.pen.setWidth(2)

        self.penSelected = QPen(self.colorSelected)
        self.penSelected.setWidth(2)

        self.penHovered = QPen(self.colorHovered)
        self.penHovered.setWidthF(5.0)

        self.penDragged = QPen(self.color)
        self.penDragged.setWidthF(2.0)
        self.penDragged.setStyle(Qt.PenStyle.DashLine)

    def boundingRect(self):
        return self.shape().boundingRect()

    def shape(self):
        return self.calculatePath()

    def paint(self, painter, QPainter=None, *args, **kwargs):
        self.setPath(self.calculatePath())

        painter.setBrush(Qt.BrushStyle.NoBrush)
        if self.hovered and self.edge.endSocket is not None:
            painter.setPen(self.penHovered)
            painter.drawPath(self.path())

        if self.edge.endSocket == None:
            painter.setPen(self.penDragged)
        else:
            painter.setPen(self.pen if not self.isSelected() else self.penSelected)

        painter.drawPath(self.path())

    def changeColor(self, color):
        if DEBUG : print("GRAPHICSEDGE:: -changeColor:: Changing Edge Color to: ",
                         color.red(), color.green(), color.blue(), "on Edge: ", self.edge)
        self.color = QColor(color) if type(color) == str else color
        self.pen = QPen(self.color)
        self.pen.setWidthF(3.0)

    def setColorFromSockets(self):
        socketTypeStart = self.edge.startSocket.socketType
        socketTypeEnd = self.edge.endSocket.socketType
        if socketTypeStart != socketTypeEnd: return False
        self.changeColor(self.edge.startSocket.grSocket.getSocketColor(socketTypeStart))

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self._lastSelectedState != self.isSelected():
            self.edge.scene.resetLastSelectedStates()
            self._lastSelectedState = self.isSelected()
            self.onSelected()

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()

    def calculatePath(self):
        #Method to draw the path from a to b
        raise NotImplemented("This method has to to be overriden in a child class")

    def onSelected(self):
        self.edge.scene.grScene.itemsSelected.emit()

    def doSelect(self, newState = True):
        self.setSelected(newState)
        self.lastSelectedState = newState
        if newState: self.onSelected()

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

            startSocketInput = self.edge.startSocket.isInput
            startSocketOutput = self.edge.startSocket.isOutput

            if (self.posSource[0] > self.posDestination[0] and startSocketOutput or
                    self.posSource[0] < self.posDestination[0] and startSocketInput):

                cpxDestination *= -1
                cpxSource *= -1

                cpyDestination = (
                        (self.posSource[1] - self.posDestination[1]) / math.fabs(
                    (self.posSource[1] - self.posDestination[1]) if (self.posSource[1] -
                                                                     self.posDestination[1]) != 0 else 0.00001)
                ) * EDGE_CP_ROUNDNESS

                cpySource = (
                        (self.posDestination[1] - self.posSource[1]) / math.fabs(
                    (self.posDestination[1] - self.posSource[1]) if (self.posDestination[1] -
                                                                     self.posSource[1]) != 0 else 0.00001)
                ) * EDGE_CP_ROUNDNESS


        path = QPainterPath(QPointF(self.posSource[0], self.posSource[1]))

        path.cubicTo(self.posSource[0] + cpxSource, self.posSource[1] + cpySource,
                     self.posDestination[0] + cpxDestination, self.posDestination[1] + cpyDestination,
                     self.posDestination[0], self.posDestination[1])

        return path