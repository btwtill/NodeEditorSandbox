from idlelib.configdialog import is_int

from nodeGraphicsSocket import QDMGraphicsSocket
from collections import OrderedDict
from nodeSerializable import Serializable

LEFT_TOP = 1
LEFT_CENTER = 2
LEFT_BOTTOM = 3
RIGHT_TOP = 4
RIGHT_CENTER = 5
RIGHT_BOTTOM = 6

DEBUG = False

class Socket(Serializable):
    def __init__(self, node, index=0, position=LEFT_TOP, socketType = 0,
                 multiEdges = True, countOnThisNodeSide = 1, isInput = False):
        super().__init__()

        self.node = node
        self.index = index
        self.position = position
        self.socketType = socketType
        self.isMultiEdges = multiEdges
        self.countOnThisNodeSide = countOnThisNodeSide
        self.isInput = isInput
        self.isOutput = not self.isInput

        if DEBUG : print("Socket -- creating with" ,self.index, self.position, "for node", self.node)

        self.grSocket = QDMGraphicsSocket(self, self.socketType)

        self.setSocketPosition()

        self.edges = []

    def setSocketPosition(self):
        self.grSocket.setPos(*self.node.getSocketPosition(self.index, self.position, self.countOnThisNodeSide))

    def getSocketPosition(self):

        if DEBUG : print("NODESOCKET:: -getSocketPosition:: Graphics Socket Position (Index, Position): "
                         , self.index, self.position, " node: ", self.node)

        result =  self.node.getSocketPosition(self.index, self.position, self.countOnThisNodeSide)

        if DEBUG : print( " NODESOCKET:: -getSocketPosition:: Result : " , result)

        return result

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeEdge(self, edge):
        if edge in self.edges: self.edges.remove(edge)
        else: print("!Warning", "Socket:removeEdge", "wanna remove edge", edge, "from self.edges but its not there")

    def removeAllEdges(self):
        while self.edges:
            edge = self.edges.pop(0)
            edge.remove()

    def __str__(self):
        return "<Socket %s %s..%s>" % ("ME" if self.isMultiEdges else "SE",hex(id(self))[2:5], hex(id(self))[-3:])

    def determinMultiEdges(self, data):
        if 'isMultiEdge' in data:
            return data['isMultiEdge']
        else:
            return data['position'] in (RIGHT_BOTTOM, RIGHT_TOP)
            #implement other behavior

    def serialize(self):
        return OrderedDict([
            ("id" , self.id),
            ("index", self.index),
            ("isMultiEdge", self.isMultiEdges),
            ("position", self.position),
            ("socketType", self.socketType)
            ]
        )

    def deserialize(self, data, hashmap = {}, restoreId = True):

        if restoreId : self.id = data['id']
        self.isMultiEdges = self.determinMultiEdges(data)
        hashmap[data['id']] = self

        return True