from nodeGraphicsSocket import QDMGraphicsSocket
from collections import OrderedDict
from nodeSerializable import Serializable

LEFT_TOP = 1
LEFT_BOTTOM = 2
RIGHT_TOP = 3
RIGHT_BOTTOM = 4

DEBUG = False

class Socket(Serializable):
    def __init__(self, node, index=0, position=LEFT_TOP, socketType = 0):
        super().__init__()

        self.node = node
        self.index = index
        self.position = position
        self.socketType = socketType

        if DEBUG : print("Socket -- creating with" ,self.index, self.position, "for node", self.node)

        self.grSocket = QDMGraphicsSocket(self, self.socketType)

        self.grSocket.setPos(*self.node.getSocketPosition(index, position))

        self.edge = None

    def getSocketPosition(self):

        if DEBUG : print(" GSP: ", self.index, self.position, " node: ", self.node)
        result =  self.node.getSocketPosition(self.index, self.position)
        if DEBUG : print( " res: " , result)

        return result

    def setConnectedEdge(self, edge = None):
        self.edge = edge

    def hasEdge(self):
        return self.edge is not None

    def __str__(self):
        return "<Socket %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    def serialize(self):
        return OrderedDict([
            ("id" , self.id),
            ("index", self.index),
            ("position", self.position),
            ("socketType", self.socketType)
            ]
        )

    def deserialize(self, data, hashmap = {}, restoreId = True):
        if restoreId : self.id = data['id']

        hashmap[data['id']] = self

        return True