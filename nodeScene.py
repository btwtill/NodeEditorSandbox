import json
from collections import OrderedDict
from nodeSerializable import Serializable
from nodeGraphicsScene import QDMGraphicsScene
from nodeNode import Node
from nodeEdge import Edge
from nodeSceneHistory import SceneHistory

class Scene(Serializable):
    def __init__(self):
        super().__init__()

        self.nodes = []
        self.edges = []

        self.sceneHistory = SceneHistory(self)

        self.sceneWidth = 64000
        self.sceneHeight = 64000

        self.initUI()

    def initUI(self):
        self.grScene = QDMGraphicsScene(self)
        self.grScene.setGrScene(self.sceneWidth, self.sceneHeight)

    def addNode(self, node):
        self.nodes.append(node)

    def addEdge(self, edge):
        self.edges.append(edge)

    def removeNode(self, node):
        self.nodes.remove(node)

    def removeEdge(self, edge):
        self.edges.remove(edge)

    def clearScene(self):
        while len(self.nodes) > 0:
            self.nodes[0].remove()

    def saveToFile(self, filename):
        with open(filename, "w") as file:
            file.write(json.dumps(self.serialize(), indent=4))
        print("saving to", filename, "was successful")

    def loadFromFile(self, filename):
        with open(filename, "r") as file:
            rawData = file.read()
            data = json.loads(rawData)
            self.deserialize(data)

    def serialize(self):
        nodes, edges = [], []
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

    def deserialize(self, data, hashmap = {}):
        print("Deserializing data", data)

        self.clearScene()

        hashmap = {}

        for nodeData in data["nodes"]:
            Node(self).deserialize(nodeData, hashmap)

        for edgeData in data["edges"]:
           Edge(self).deserialize(edgeData, hashmap)

        return True