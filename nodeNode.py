from collections import OrderedDict
from socket import socket

from nodeSerializable import Serializable
from nodeContentWidget import QDMNodeContentWidget
from nodeGraphicsNode import QDMGraphicsNode
from nodeSocket import Socket, LEFT_TOP, RIGHT_TOP, LEFT_BOTTOM, RIGHT_BOTTOM

DEBUG = False

class Node(Serializable):
    def __init__(self, scene, title = "undifined Node", inputs = [], outputs = []):
        super().__init__()

        self._title = title

        self.scene = scene


        self.content = QDMNodeContentWidget(self)
        self.grNode = QDMGraphicsNode(self)

        self.title = title

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        self.socketSpacing = 24

        self.inputs = []
        self.outputs = []

        counter = 0
        for item in inputs:
            socket = Socket(node=self, index = counter, position = LEFT_TOP, socketType = item)
            counter += 1
            self.inputs.append(socket)

        counter = 0
        for item in outputs:
            socket = Socket(node = self, index = counter, position = RIGHT_TOP, socketType = item)
            counter += 1
            self.outputs.append(socket)

    @property
    def pos(self):
        return self.grNode.pos()

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, value):
        self._title = value
        self.grNode.title = self._title

    def getSocketPosition(self, index, position):

        x = 0 if position in (LEFT_TOP, LEFT_BOTTOM) else self.grNode.width

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            y = self.grNode.height - self.grNode.edgeSize - self.grNode.padding - index * self.socketSpacing
        else:
            y = self.grNode.titleHeight + self.grNode.padding + self.grNode.edgeSize + index * self.socketSpacing

        return [x, y]

    def setPosition(self, x, y):
        self.grNode.setPos(x, y)

    def updateConnectedEdges(self):
        for socket in self.inputs + self.outputs:
            if socket.hasEdge():
                socket.edge.updatePositions()

    def remove(self):
        if DEBUG : print("Node : DEBUG : removing node", self)
        if DEBUG : print("Node : DEBUG : removing all edges form sockets")

        for socket in (self.inputs + self.outputs):
            if socket.hasEdge():
                if DEBUG : print("Node : DEBUG : removing edge ", socket.edge, "From Socket", socket)
                socket.edge.remove()
        if DEBUG:  print("Node : DEBUG : removing gr Node")
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        if DEBUG:  print("Node : DEBUG : removing node from scene list")
        self.scene.removeNode(self)
        if DEBUG:  print("Node : DEBUG : DONE!!")


    def __str__(self):
        return "<Node %s..%s>" % (hex(id(self))[2:5], hex(id(self))[-3:])

    def serialize(self):
        inputs, outputs = [], []

        for socket in self.inputs: inputs.append(socket.serialize())
        for socket in self.outputs: outputs.append(socket.serialize())

        return OrderedDict([
            ("id" , self.id),
            ("title", self._title),
            ("pos_x", self.grNode.scenePos().x()),
            ("pos_y", self.grNode.scenePos().y()),
            ("inputs", inputs),
            ("outputs", outputs),
            ("content", self.content.serialize()),
            ]
        )

    def deserialize(self, data, hashmap = {}):

        if DEBUG : print("NODE : DEBUG : Deserializing data", data)

        self.id = data['id']
        hashmap[data['id']] = self
        self.title = data['title']

        self.setPosition(data['pos_x'], data['pos_y'])

        data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 1000 )
        data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 1000)

        self.inputs = []
        self.outputs = []

        for socketData in data['inputs']:
            newSocket = Socket(node = self, index = socketData['index'],
                               position = socketData['position'],
                               socketType = socketData['socketType'])

            newSocket.deserialize(socketData, hashmap)
            self.inputs.append(newSocket)

        for socketData in data['outputs']:
            newSocket = Socket(node = self, index = socketData['index'],
                               position = socketData['position'],
                               socketType = socketData['socketType'])
            newSocket.deserialize(socketData, hashmap)
            self.outputs.append(newSocket)

        if DEBUG : print("NODE : DEBUG : Hashmap...", hashmap)

        return True