import json
import os
from collections import OrderedDict

from nodeSceneClipboard import SceneClipboard
from nodeSerializable import Serializable
from nodeGraphicsScene import QDMGraphicsScene
from nodeNode import Node
from nodeEdge import Edge
from nodeSceneHistory import SceneHistory
from utils import dumpException

DEBUG = False

class InvalidFile(Exception): pass



class Scene(Serializable):
    def __init__(self):
        super().__init__()

        self.nodes = []
        self.edges = []

        self.sceneHistory = SceneHistory(self)

        self._hasBeenModified = False
        self._hasBeenModifiedListeners = []

        self.sceneWidth = 64000
        self.sceneHeight = 64000

        self.initUI()

        self.clipboard = SceneClipboard(self)

    @property
    def hasBeenModified(self): return self._hasBeenModified

    @hasBeenModified.setter
    def hasBeenModified(self, value):
        if not self._hasBeenModified and value:
            self._hasBeenModified = value

            for callback in self._hasBeenModifiedListeners:
                callback()

        self._hasBeenModified = value

    def addHasBeenModifiedListener(self, callback):
        self._hasBeenModifiedListeners.append(callback)

    def initUI(self):
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.sceneWidth, self.sceneHeight)

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        if node in self.nodes: self.nodes.remove(node)
        else: print("!Warning", "Scene::removeNode", "wanna remove node", node, "from self.nodes but its not there")

    def removeEdge(self, edge):
        if edge in self.edges: self.edges.remove(edge)
        else: print("!Warning", "Scene::removeEdge", "wanna remove edge", edge, "from self.edge but its not there")

    def clearScene(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()

        self.hasBeenModified = False

    def saveToFile(self, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
            print("saving to", filename, "was successful")

            self.hasBeenModified = False

    def loadFromFile(self, filename):
        with open(filename, "r") as file:
            rawData = file.read()
            try:
                data = json.loads(rawData)
                self.deserialize(data)
                self.hasBeenModified = False
            except json.JSONDecodeError:
                raise InvalidFile("%s is not a valid Json file" % os.path.basename(filename))
            except Exception as e:
                dumpException(e)

    def serialize(self):
        nodes, edges = [], []

        if DEBUG : print("SCENE : DEBUG : current Scene Nodes: ", self.nodes)
        if DEBUG: print("SCENE : DEBUG : current Scene Edges: ", self.edges)

        for node in self.nodes: nodes.append(node.serialize())
        for edge in self.edges: edges.append(edge.serialize())

        return OrderedDict([
            ("id" , self.id),
            ("sceneWidth" , self.sceneWidth),
            ("sceneHeight" , self.sceneHeight),
            ("nodes", nodes),
            ("edges", edges),
            ]
        )

    def deserialize(self, data, hashmap = {}, restoreId = True):

        self.clearScene()
        hashmap = {}

        if restoreId : self.id = data['id']

        for nodeData in data["nodes"]:
            Node(self).deserialize(nodeData, hashmap, restoreId)

        for edgeData in data["edges"]:
           Edge(self).deserialize(edgeData, hashmap, restoreId)

        return True