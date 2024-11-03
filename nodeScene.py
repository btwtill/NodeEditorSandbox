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
        self._itemsSelectedListeners = []
        self._itemDeselectedListeners = []
        self._lastSelectedItems = []

        self.sceneWidth = 64000
        self.sceneHeight = 64000

        self.nodeClassSelector = None

        self.initUI()

        self.clipboard = SceneClipboard(self)

        self.grScene.itemsSelected.connect(self.onItemSelected)
        self.grScene.itemsDeselected.connect(self.onItemDeselected)

    @property
    def hasBeenModified(self): return self._hasBeenModified

    @hasBeenModified.setter
    def hasBeenModified(self, value):
        if not self._hasBeenModified and value:
            self._hasBeenModified = value

            for callback in self._hasBeenModifiedListeners: callback()

        self._hasBeenModified = value

    def initUI(self):
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.sceneWidth, self.sceneHeight)

    def onItemSelected(self):

        if DEBUG : print("SCENE:: -onItemSelected")

        currentSelectedItems = self.getSelectedItems()

        if DEBUG:
            print("NODESCENE:: -onItemSelected:: Current Selected Items =", currentSelectedItems)
            print("NODESCENE:: -onItemSelected:: Last Selected Items =", self._lastSelectedItems)

        if currentSelectedItems != self._lastSelectedItems:
            self._lastSelectedItems = currentSelectedItems
            self.sceneHistory.storeHistory("SelectionChanged")
            for callback in self._itemsSelectedListeners: callback()

    def onItemDeselected(self):

        if DEBUG : print("SCENE:: -onItemDeselected")

        self.resetLastSelectedStates()

        if self._lastSelectedItems != []:
            self._lastSelectedItems = []
            self.sceneHistory.storeHistory("DeselectedEverything")
            for callback in self._itemDeselectedListeners: callback()

    def isModified(self):
        return self.hasBeenModified

    def getSelectedItems(self):
        return self.grScene.selectedItems()

    def addHasBeenModifiedListener(self, callback):
        self._hasBeenModifiedListeners.append(callback)

    def addItemSelectedListener(self, callback):
        self._itemsSelectedListeners.append(callback)

    def addItemDeselectedListener(self, callback):
        self._itemDeselectedListeners.append(callback)

    def addDragEnterListener(self, callback):
        self.grScene.views()[0].addDragEnterListener(callback)

    def addDropListener(self, callback):
        self.grScene.views()[0].addDropListener(callback)

    def resetLastSelectedStates(self):
        for node in self.nodes:
            node.grNode._lastSelectedState = False
        for edge in self.edges:
            edge.grEdge._lastSelectedState = False

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

    def setNodeClassSelector(self, classSelectingFunction):
        self.nodeClassSelector = classSelectingFunction

    def getNodeClassFromData(self, nodeData):
        if DEBUG :
            print("NODESCENE:: -getNodeClassFromData:: nodeClassSelector: ", self.nodeClassSelector)
            print("NODESCENE:: -getNodeClassFromData:: nodeClassSelectorResult: ", self.nodeClassSelector(nodeData))

        return Node if self.nodeClassSelector is None else self.nodeClassSelector(nodeData)

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
            self.getNodeClassFromData(nodeData)(self).deserialize(nodeData, hashmap, restoreId)

        for edgeData in data["edges"]:
            Edge(self).deserialize(edgeData, hashmap, restoreId)

        return True
