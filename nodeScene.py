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

        self.sceneWidth = 64000
        self.sceneHeight = 64000

        self._silentSelectionEvents = False
        self._hasBeenModified = False
        self._lastSelectedItems = None

        self._hasBeenModifiedListeners = []
        self._itemsSelectedListeners = []
        self._itemDeselectedListeners = []

        self.nodeClassSelector = None

        self.initUI()

        self.sceneHistory = SceneHistory(self)
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

    def setSilentSelectionEvents(self, value = True):
        self._silentSelectionEvents = value

    def onItemSelected(self, silent=False):

        if self._silentSelectionEvents: return

        if DEBUG : print("SCENE:: -onItemSelected")

        currentSelectedItems = self.getSelectedItems()

        if DEBUG:
            print("NODESCENE:: -onItemSelected:: Current Selected Items =", currentSelectedItems)
            print("NODESCENE:: -onItemSelected:: Last Selected Items =", self._lastSelectedItems)

        if currentSelectedItems != self._lastSelectedItems:
            self._lastSelectedItems = currentSelectedItems
            if not silent:
                for callback in self._itemsSelectedListeners: callback()
                self.sceneHistory.storeHistory("SelectionChanged")

    def onItemDeselected(self, silent = False):

        if DEBUG : print("SCENE:: -onItemDeselected")

        currentSelectedItems = self.getSelectedItems()
        if currentSelectedItems == self._lastSelectedItems:
            return

        self.resetLastSelectedStates()

        if currentSelectedItems == []:
            self._lastSelectedItems = []
            if not silent:
                self.sceneHistory.storeHistory("DeselectedEverything")
                for callback in self._itemDeselectedListeners: callback()

    def doDeselectItems(self, silent = False):
        for item in self.getSelectedItems():
            item.setSelected(False)
        if not silent:
            self.onItemDeselected()

    def isModified(self):
        return self.hasBeenModified

    def getSelectedItems(self):
        return self.grScene.selectedItems()

    def getEdgeClass(self):
        return Edge

    def getNodeById(self, nodeID):
        for node in self.nodes:
            if node.id == nodeID:
                return node
        return None

    def addHasBeenModifiedListener(self, callback):
        self._hasBeenModifiedListeners.append(callback)

    def addItemSelectedListener(self, callback):
        self._itemsSelectedListeners.append(callback)

    def addItemDeselectedListener(self, callback):
        self._itemDeselectedListeners.append(callback)

    def addDragEnterListener(self, callback):
        self.getView().addDragEnterListener(callback)

    def addDropListener(self, callback):
        self.getView().addDropListener(callback)

    def resetLastSelectedStates(self):
        for node in self.nodes:
            node.grNode._lastSelectedState = False
        for edge in self.edges:
            edge.grEdge._lastSelectedState = False

    def getView(self):
        return self.grScene.views()[0]

    def getItemAt(self, position):
        return self.getView().itemAt(position)

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        if node in self.nodes: self.nodes.remove(node)
        else: print("SCENE:: -removeNode:: %s ::  !Warning:: trying remove node" % node.__class__.__name__,
                    node, " from self.nodes but its not there. Current Nodes: ", self.nodes)

    def removeEdge(self, edge):
        if edge in self.edges: self.edges.remove(edge)
        else: print("SCENE:: -removeEdges:: %s :: !Warning:: trying remove edge" % edge.__class__.__name__,
                    edge, " from self.edges but its not there. Current Edges: ", self.edges)

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

    def getEdgeClass(self):
        return Edge

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

        hashmap = {}

        if restoreId: self.id = data['id']

        allNodes = self.nodes.copy()

        for nodeData in data["nodes"]:
            found = False
            for node in allNodes:
                if node.id == nodeData['id']:
                    found = node
                    break
            if not found:
                newNode = self.getNodeClassFromData(nodeData)(self)
                newNode.deserialize(nodeData, hashmap, restoreId)
                newNode.onDeserialized(nodeData)
            else:
                found.deserialize(nodeData, hashmap, restoreId)
                found.onDeserialized(nodeData)
                allNodes.remove(found)

        while allNodes != []:
            node = allNodes.pop()
            node.remove()

        allEdges = self.edges.copy()

        for edgeData in data["edges"]:
            found = False
            for edge in allEdges:
                if edge.id == edgeData['id']:
                    found = edge
                    break
            if not found:
                newEdge = self.getEdgeClass()(self).deserialize(edgeData, hashmap, restoreId)
            else:
                found.deserialize(edgeData, hashmap, restoreId)
                allEdges.remove(found)

        while allEdges != []:
            edge = allEdges.pop()
            edge.remove()

        return True
