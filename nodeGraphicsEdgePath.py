import math
from PyQt5.QtCore import *
from PyQt5.QtGui import *

EDGE_CP_ROUNDNESS = 100

class GraphicsEdgePathBase:

    def __init__(self, owner):
        self.owner = owner

    def calcPath(self):
        return None

class GraphicsEdgePathDirect(GraphicsEdgePathBase):

    def calcPath(self):
        path = QPainterPath(QPointF(self.owner.posSource[0], self.owner.posSource[1]))
        path.lineTo(self.owner.posDestination[0], self.owner.posDestination[1])
        return path

class GraphicsEdgePathBezier(GraphicsEdgePathBase):

    def calcPath(self):

        dist = (self.owner.posDestination[0] - self.owner.posSource[0]) * 0.5

        cpxSource = +dist
        cpxDestination = -dist
        cpySource = 0
        cpyDestination = 0

        if self.owner.edge.startSocket is not None:

            startSocketInput = self.owner.edge.startSocket.isInput
            startSocketOutput = self.owner.edge.startSocket.isOutput

            if (self.owner.posSource[0] > self.owner.posDestination[0] and startSocketOutput or
                    self.owner.posSource[0] < self.owner.posDestination[0] and startSocketInput):

                cpxDestination *= -1
                cpxSource *= -1

                cpyDestination = (
                        (self.owner.posSource[1] - self.owner.posDestination[1]) / math.fabs(
                    (self.owner.posSource[1] - self.owner.posDestination[1]) if (self.owner.posSource[1] -
                                                                     self.owner.posDestination[1]) != 0 else 0.00001)
                ) * EDGE_CP_ROUNDNESS

                cpySource = (
                        (self.owner.posDestination[1] - self.owner.posSource[1]) / math.fabs(
                    (self.owner.posDestination[1] - self.owner.posSource[1]) if (self.owner.posDestination[1] -
                                                                     self.owner.posSource[1]) != 0 else 0.00001)
                ) * EDGE_CP_ROUNDNESS


        path = QPainterPath(QPointF(self.owner.posSource[0], self.owner.posSource[1]))

        path.cubicTo(self.owner.posSource[0] + cpxSource, self.owner.posSource[1] + cpySource,
                     self.owner.posDestination[0] + cpxDestination, self.owner.posDestination[1] + cpyDestination,
                     self.owner.posDestination[0], self.owner.posDestination[1])

        return path