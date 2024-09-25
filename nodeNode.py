from nodeContentWidget import QDMNodeContentWidget
from nodeGraphicsNode import QDMGraphicsNode
from nodeSocket import Socket, LEFT_TOP, RIGHT_TOP, LEFT_BOTTOM, RIGHT_BOTTOM

DEBUG = False

class Node():
    def __init__(self, scene, title = "undifined Node", inputs = [], outputs = []):
        self.scene = scene
        self.title = title

        self.content = QDMNodeContentWidget(self)
        self.grNode = QDMGraphicsNode(self)

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