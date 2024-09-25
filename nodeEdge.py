from nodeGraphicsEdge import *

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2

DEBUG = False

class Edge():
    def __init__(self, scene, startSocket, endSocket, edgeType = EDGE_TYPE_DIRECT):

        self.scene = scene

        self.startSocket = startSocket
        self.endSocket = endSocket

        self.startSocket.setConnectedEdge(self)
        self.endSocket.setConnectedEdge(self)

        self.grEdge = QDMGraphicsEdgeDirect(self) if edgeType == EDGE_TYPE_DIRECT else QDMGraphicsEdgeBezier(self)

        self.updatePositions()

        if DEBUG : print("Edge: ", self.grEdge.posSource, "to", self.grEdge.posDestination)

        self.scene.grScene.addItem(self.grEdge)
        self.scene.addEdge(self)

    def updatePositions(self):

        sourcePos = self.startSocket.getSocketPosition()
        sourcePos[0] += self.startSocket.node.grNode.pos().x()
        sourcePos[1] += self.startSocket.node.grNode.pos().y()

        self.grEdge.setSource(*sourcePos)

        if self.endSocket is not None:
            endPos = self.endSocket.getSocketPosition()
            endPos[0] += self.endSocket.node.grNode.pos().x()
            endPos[1] += self.endSocket.node.grNode.pos().y()

            self.grEdge.setDestination(*endPos)

        if DEBUG : print(" SS:", self.startSocket)
        if DEBUG : print(" ES:", self.endSocket)

        self.grEdge.update()

    def removeFromSockets(self):
        if self.startSocket is not None:
            self.startSocket.edge = None
        if self.endSocket is not None:
            self.endSocket.edge = None

        self.endSocket = None
        self.startSocket = None

    def remove(self):
        self.removeFromSockets()
        self.scene.grScene.removeItem(self.grEdge)
        self.grEdge = None
        self.scene.removeEdge(self)

    def __str__(self):
        return "<Edge %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])