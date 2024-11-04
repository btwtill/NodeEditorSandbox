from nodeGraphicsEdge import *
from collections import OrderedDict
from nodeSerializable import Serializable
from utils import dumpException

EDGE_TYPE_DIRECT = 1
EDGE_TYPE_BEZIER = 2

DEBUG = False

class Edge(Serializable):
    def __init__(self, scene, startSocket = None, endSocket = None, edgeType = EDGE_TYPE_DIRECT):
        super().__init__()

        self.scene = scene

        #default init
        self._startSocket = None
        self._endSocket = None

        self.startSocket = startSocket
        self.endSocket = endSocket
        self.edgeType = edgeType

        self.scene.addEdge(self)

        if DEBUG: print("Edge: ", self.grEdge.posSource, "to", self.grEdge.posDestination)

    @property
    def startSocket(self): return self._startSocket
    @startSocket.setter
    def startSocket(self, value):
        #if we were assigned to some socket ebfore, delete from the socket
        if self._startSocket is not None:
            self._startSocket.removeEdge(self)
        #assign new start socket
        self._startSocket = value
        # add edge to socket class
        if self.startSocket is not None:
            self.startSocket.addEdge(self)

    @property
    def endSocket(self):
        return self._endSocket
    @endSocket.setter
    def endSocket(self, value):
        # if we were assigned to some socket bfore, delete from the socket
        if self._endSocket is not None:
            self._endSocket.removeEdge(self)
        #assign new end socket
        self._endSocket = value
        #add edge to socket class
        if self.endSocket is not None:
            self.endSocket.addEdge(self)

    @property
    def edgeType(self): return self._edgeType
    @edgeType.setter
    def edgeType(self, value):
        #If there is a graphical edge to it remove it from the graphics scene

        if hasattr(self, 'grEdge') and self.grEdge is not None:
            if DEBUG : print("EDGE : DEBUG : has gredge ")
            self.scene.grScene.removeItem(self.grEdge)

        self._edgeType = value
        if self.edgeType == EDGE_TYPE_DIRECT:
            self.grEdge = QDMGraphicsEdgeDirect(self)
        elif self.edgeType == EDGE_TYPE_BEZIER:
            self.grEdge = QDMGraphicsEdgeBezier(self)
        else:
            self.grEdge = QDMGraphicsEdgeBezier(self)

        self.scene.grScene.addItem(self.grEdge)

        if self.startSocket is not None:
            self.updatePositions()

    def getOtherSocket(self, knownSocket):
        return self.startSocket if knownSocket == self.endSocket else self.endSocket

    def doSelect(self, newState = True):
        self.grEdge.doSelect(newState)

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
        else:
            self.grEdge.setDestination(*sourcePos)

        self.grEdge.update()

    def removeFromSockets(self):
        # @TODO: Fix me
        #if self.startSocket is not None:
        #    self.startSocket.removeEdge(None)
        #if self.endSocket is not None:
        #    self.endSocket.removeEdge(None)

        self.endSocket = None
        self.startSocket = None

    def remove(self):
        oldSockets = [self.startSocket, self.endSocket]

        if DEBUG: print("Edge : DEBUG : removing edge", self)
        if DEBUG: print("Edge : DEBUG : removing edge from Sockets", self)

        self.removeFromSockets()

        if DEBUG: print("Edge : DEBUG : removing graphical Edge from Scene", self)

        self.scene.grScene.removeItem(self.grEdge)

        self.grEdge = None

        if DEBUG: print("Edge : DEBUG : removing edge from Scene", self)

        try:
            self.scene.removeEdge(self)
        except ValueError:
            pass
        if DEBUG: print("Edge : DEBUG : DONE!!", self)

        try:
            for socket in oldSockets:
                if socket and socket.node:
                    socket.node.onEdgeConnectionChanged(self)
                    if socket.isInput: socket.node.onInputChanged(self)

        except Exception as e: dumpException(e)

    def __str__(self):
        return "<Edge %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    def serialize(self):
        return OrderedDict([
            ("id" , self.id),
            ("edgeType", self.edgeType),
            ("start", self.startSocket.id),
            ("end", self.endSocket.id),
            ]
        )

    def deserialize(self, data, hashmap = {}, restoreId = True):

        if restoreId : self.id = data['id']

        self.startSocket = hashmap[data['start']]
        self.endSocket = hashmap[data['end']]
        self.edgeType = data['edgeType']

        return True