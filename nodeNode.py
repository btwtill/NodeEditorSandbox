from nodeContentWidget import QDMNodeContentWidget
from nodeGraphicsNode import QDMGraphicsNode
from nodeSocket import Socket, LEFT_TOP, RIGHT_TOP, LEFT_BOTTOM, RIGHT_BOTTOM


class Node():
    def __init__(self, scene, title = "undifined Node", inputs = [], outputs = []):
        self.scene = scene
        self.title = title

        self.content = QDMNodeContentWidget()
        self.grNode = QDMGraphicsNode(self)

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        self.socketSpacing = 24

        self.inputs = []
        self.outputs = []

        counter = 0
        for item in inputs:
            socket = Socket(node=self, index = counter, position = LEFT_BOTTOM)
            counter += 1
            self.inputs.append(socket)

        counter = 0
        for item in outputs:
            socket = Socket(node = self, index = counter, position = RIGHT_TOP)
            counter += 1
            self.outputs.append(socket)


    def getSocketPosition(self, index, position):

        x = 0 if position in (LEFT_TOP, LEFT_BOTTOM) else self.grNode.width

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            y = self.grNode.height - index * self.socketSpacing
        else:
            y = self.grNode.titleHeight + self.grNode.padding + self.grNode.edgeSize + index * self.socketSpacing

        return x, y