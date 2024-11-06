from collections import OrderedDict
from distutils.command.install_egg_info import install_egg_info

from nodeSerializable import Serializable
from nodeContentWidget import QDMNodeContentWidget
from nodeGraphicsNode import QDMGraphicsNode
from nodeSocket import Socket, LEFT_TOP, RIGHT_TOP, LEFT_BOTTOM, RIGHT_BOTTOM, LEFT_CENTER, RIGHT_CENTER
from utils import dumpException

DEBUG = False

class Node(Serializable):

    GraphicsNodeClass = QDMGraphicsNode
    NodeContentClass = QDMNodeContentWidget
    SocketClass = Socket

    def __init__(self, scene, title = "undifined Node", inputs = [], outputs = []):
        super().__init__()

        self._title = title
        self.scene = scene

        self.content = None
        self.grNode = None

        self.initInnerClasses()
        self.initSettings()

        self.title = title

        self.scene.addNode(self)
        self.scene.grScene.addItem(self.grNode)

        self.inputs = []
        self.outputs = []
        self.initSockets(inputs, outputs)

        self._isDirty = False
        self._isInvalid = False

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

    def initSettings(self):

        self.socketSpacing = 24

        self.inputSocketPosition = LEFT_TOP
        self.outputSocketPosition = RIGHT_TOP
        self.inputMulitEdged = False
        self.outputMultiEdged = True
        self.socketOffsets = {
            LEFT_BOTTOM: -1,
            LEFT_CENTER: -1,
            LEFT_TOP: -1,
            RIGHT_BOTTOM: 1,
            RIGHT_CENTER: 1,
            RIGHT_TOP: 1,
        }

    def initInnerClasses(self):
        nodeContentClass = self.getNodeContentClass()
        nodeGraphicsClass = self.getGraphicsNodeClass()
        if nodeContentClass is not None: self.content = nodeContentClass(self)
        if nodeGraphicsClass is not None: self.grNode = nodeGraphicsClass(self)

    def getNodeContentClass(self):
        return self.__class__.NodeContentClass

    def getGraphicsNodeClass(self):
        return self.__class__.GraphicsNodeClass

    def initSockets(self, inputs, outputs, reset=True):

        if reset:
            if hasattr(self, 'inputs') and hasattr(self, 'outputs'):
                for socket in (self.inputs + self.outputs):
                    self.scene.grScene.removeItem(socket.grSocket)
                self.inputs = []
                self.outputs = []

        counter = 0
        for item in inputs:
            socket = self.__class__.SocketClass(node=self, index=counter, position=self.inputSocketPosition,
                            socketType=item, multiEdges=self.inputMulitEdged,
                            countOnThisNodeSide=len(inputs), isInput=True )
            counter += 1
            self.inputs.append(socket)

        counter = 0
        for item in outputs:
            socket = self.__class__.SocketClass(node=self, index=counter, position=self.outputSocketPosition,
                            socketType=item, multiEdges=self.outputMultiEdged,
                            countOnThisNodeSide=len(outputs), isInput=False)
            counter += 1
            self.outputs.append(socket)

    def getSocketPosition(self, index, position, numberOfSockets = 1):

        x = self.socketOffsets[position] if position in (LEFT_TOP, LEFT_CENTER, LEFT_BOTTOM) else self.grNode.width

        if position in (LEFT_BOTTOM, RIGHT_BOTTOM):
            y = (self.grNode.height -
                 self.grNode.edgeRoundness -
                 self.grNode.titleHorizontalPadding -
                 index * self.socketSpacing)

        elif position in (LEFT_CENTER, RIGHT_CENTER):

            nodeHeight =self.grNode.height
            topOffset = self.grNode.titleHeight + 2 * self.grNode.titleVerticalPadding + self.grNode.edgePadding
            availableHeight = nodeHeight - topOffset

            totalHeightAllSockets = numberOfSockets * self.socketSpacing

            newTop = availableHeight - totalHeightAllSockets

            #y = topOffset + index * self.socketSpacing + newTop / 2
            y = topOffset + availableHeight/2.0 +(index-0.5) * self.socketSpacing
            if numberOfSockets > 1:
                y -= self.socketSpacing * (numberOfSockets -1) /2

        elif position in (LEFT_TOP, RIGHT_TOP):
            y = (self.grNode.titleHeight +
                 self.grNode.titleHorizontalPadding +
                 self.grNode.edgeRoundness +
                 index * self.socketSpacing)
        else:
            y = 0

        return [x, y]

    def setPosition(self, x, y):
        self.grNode.setPos(x, y)

    def updateConnectedEdges(self):
        for socket in self.inputs + self.outputs:
            for edge in socket.edges:
                edge.updatePositions()

    def remove(self):
        if DEBUG : print("Node : DEBUG : removing node", self)
        if DEBUG : print("Node : DEBUG : removing all edges form sockets")

        for socket in (self.inputs + self.outputs):
            for edge in socket.edges:
                if DEBUG : print("Node : DEBUG : from socket ", socket, "edge:", edge)
                edge.remove()
        if DEBUG:  print("Node : DEBUG : removing gr Node")
        self.scene.grScene.removeItem(self.grNode)
        self.grNode = None
        if DEBUG:  print("Node : DEBUG : removing node from scene list")
        self.scene.removeNode(self)
        if DEBUG:  print("Node : DEBUG : DONE!!")

    def __str__(self):
        return "<%s: %s %s..%s>" % (self.title, self.__class__.__name__,hex(id(self))[2:5], hex(id(self))[-3:])

    def isDirty(self):
        return self._isDirty

    def markDirty(self, value = True):
        self._isDirty = value
        if self._isDirty: self.onMarkedDirty()

    def isInvalid(self):
        return self._isInvalid

    def isSelected(self):
        return self.grNode.isSelected()

    def markInvalid(self, value = True):
        self._isInvalid = value
        if self._isDirty: self.onMarkedInvalid()

    def onMarkedDirty(self):
        pass

    def onMarkedInvalid(self):
        pass

    def doSelect(self, newState):
        self.grNode.doSelect(newState)

    def eval(self, index=0):
        self.markDirty(False)
        self.markInvalid(False)
        return 0

    def evalChildren(self):
        for node in self.getChildrenNodes():
            node.eval()

    def markChildrenDirty(self, value=True):
        for otherNode in self.getChildrenNodes():
            otherNode.markDirty(value)

    def markDescendeantsDirty(self, value = True):
        for otherNode in self.getChildrenNodes():
            otherNode.markDirty(value)
            otherNode.markChildrenDirty(value)

    def markChildrenInvalid(self, value=True):
        for otherNode in self.getChildrenNodes():
            otherNode.markInvalid(value)

    def markDescendeantsInvalid(self, value = True):
        for otherNode in self.getChildrenNodes():
            otherNode.markInvalid(value)
            otherNode.markChildrenInvalid(value)

    def getChildrenNodes(self):
        if self.outputs == []: return []

        otherNodes = []

        for index in range(len(self.outputs)):
            for edge in self.outputs[index].edges:
                otherNode = edge.getOtherSocket(self.outputs[index]).node
                otherNodes.append(otherNode)

        return otherNodes

    def getInput(self, index=0):
        try:
            inputSocket = self.inputs[index]
            if len(inputSocket.edges) == 0: return None, None
            connectingEdge = inputSocket.edges[0]
            otherSocket = connectingEdge.getOtherSocket(self.inputs[index])
            return otherSocket.node
        except Exception as e:
            dumpException(e)
            return None

    def getInputWithSocket(self, index=0):
        try:
            inputSocket=self.inputs[index]
            if len(inputSocket.edges) == 0: return None, None
            connectingEdge = inputSocket.edges[0]
            otherSocket = connectingEdge.getOtherSocket(self.inputs[index])
            return otherSocket.node, otherSocket
        except Exception as e:
            dumpException(e)
            return None, None

    def getInpputWithSocketIndex(self, index=0):
        try:
            edge = self.inputs[index].edges[0]
            socket = edge.getOtherSocket(self.inputs[index])
            return socket.node, socket.index
        except IndexError:
            return None, None
        except Exception as e:
            dumpException(e)
            return None, None

    def getInputs(self, index=0):
        inputs = []
        for edge in self.inputs[index].edges:
            otherSocket = edge.getOtherSocket(self.inputs[index])
            inputs.append(otherSocket.node)

        return inputs

    def getOutputs(self, index = 0):
        outputs = []
        for edge in self.outputs[index].edges:
            otherSocket = edge.getOtherSocket(self.outputs[index])
            outputs.append(otherSocket.node)

        return outputs

    def onEdgeConnectionChanged(self, newEdge):
        if DEBUG : print("%s:: onEdgeConnectionChanged:: changed" % self.__class__.__name__, newEdge)
        pass

    def onDoubleCLicked(self, event):
        pass

    def onInputChanged(self, newEdge):
        print("%s:: onInputChanged:: input changed" % self.__class__.__name__, newEdge)
        self.markDirty()
        self.markDescendeantsDirty()

    def serialize(self):
        inputs, outputs = [], []

        for socket in self.inputs: inputs.append(socket.serialize())
        for socket in self.outputs: outputs.append(socket.serialize())

        serializedContent = self.content.serialize() if isinstance(self.content, Serializable) else {}

        return OrderedDict([
            ("id" , self.id),
            ("title", self._title),
            ("pos_x", self.grNode.scenePos().x()),
            ("pos_y", self.grNode.scenePos().y()),
            ("inputs", inputs),
            ("outputs", outputs),
            ("content", serializedContent),
            ]
        )

    def deserialize(self, data, hashmap = {}, restoreId = True):

        try:
            if DEBUG : print("NODE : DEBUG : Deserializing data", data)

            if restoreId : self.id = data['id']

            hashmap[data['id']] = self
            self.title = data['title']

            self.setPosition(data['pos_x'], data['pos_y'])

            data['inputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 1000 )
            data['outputs'].sort(key=lambda socket: socket['index'] + socket['position'] * 1000)

            numberOfInputs = len(data['inputs'])
            numberOfOutputs = len(data['outputs'])

            for socketData in data['inputs']:

                found = None
                for socket in self.inputs:
                    if socket.index == socketData['index']:
                        found = socket
                        break
                if found is None:
                    print("%s :: -deserialize:: Socket data has not found input socket with index:"
                          % self.__class__.__name__, socketData['index'])
                    print("%s :: -deserialize:: actual Socket Data: ", socketData)

                    found = self.__class__.SocketClass(node = self, index = socketData['index'],
                                       position = socketData['position'],
                                       socketType = socketData['socketType'],
                                       countOnThisNodeSide=numberOfInputs, isInput=True)

                    self.inputs.append(found)
                found.deserialize(socketData, hashmap, restoreId)

            for socketData in data['outputs']:

                found = None

                for socket in self.outputs:
                    if socket.index == socketData['index']:
                        found = socket
                        break

                if found is None:
                    print("%s :: -deserialize:: Socket data has not found output socket with index:"
                          % self.__class__.__name__, socketData['index'])
                    print("%s :: -deserialize:: actual Socket Data: ", socketData)

                    found = self.__class__.SocketClass(node = self, index = socketData['index'],
                                       position = socketData['position'],
                                       socketType = socketData['socketType'],
                                       countOnThisNodeSide=numberOfOutputs, isInput=False)

                    self.outputs.append(found)
                found.deserialize(socketData, hashmap, restoreId)


            if DEBUG : print("NODE : DEBUG : Hashmap...", hashmap)
        except Exception as e: dumpException(e)

        if isinstance(self.content, Serializable):
            result = self.content.deserialize(data['content'], hashmap)
            return result

        return True
