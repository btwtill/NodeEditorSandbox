
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from nodeSocket import RIGHT_TOP, RIGHT_BOTTOM, LEFT_BOTTOM, LEFT_TOP
from nodeGraphicsEdgePath import GraphicsEdgePathDirect, GraphicsEdgePathBezier

DEBUG = False


class QDMGraphicsEdge(QGraphicsPathItem):
    def __init__(self, edge, parent=None):
        super().__init__(parent)

        self.edge = edge

        self.pathCalculator = self.determineEdgePathClass()(self)
        #if DEBUG: print("GRAPHICSEDGE:: __init__:: path Calculator:: ", self.pathCalculator)

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

    def createEdgePathCalculator(self):
        self.pathCalculator = self.determineEdgePathClass()(self)
        return self.pathCalculator

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

    def determineEdgePathClass(self):

        from nodeEdge import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT
        if self.edge.edgeType == EDGE_TYPE_BEZIER:
            return GraphicsEdgePathBezier
        if self.edge.edgeType == EDGE_TYPE_DIRECT:
            return GraphicsEdgePathDirect
        else:
            return GraphicsEdgePathBezier

    def calculatePath(self):
        #Method to draw the path from a to b
        #if DEBUG :  print("GRAPHICSEDGE:: --calculatePath:: PathCalculator::", self.pathCalculator)
        #if DEBUG : print("GRAPHICSEDGE:: --calculatePath:: result:: ", self.pathCalculator.calcPath())
        return self.pathCalculator.calcPath()

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


