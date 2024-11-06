from collections import OrderedDict
from nodeNode import Node
from nodeEdge import Edge
from nodeGraphicsEdge import QDMGraphicsEdge

DEBUG = False

class SceneClipboard():
    def __init__(self, scene):
        self.scene = scene

    def serializeSelected(self, delete = False):
        if DEBUG : print("copy to clipboard")

        selectedNodes, selectedEdges, selectedSockets = [], [], {}

        #sort the nodes edges and sockets form the selection to the lists

        for item in self.scene.grScene.selectedItems():
            if hasattr(item, 'node'):
                selectedNodes.append(item.node.serialize())

                for socket in (item.node.inputs + item.node.outputs):

                    selectedSockets[socket.id] = socket

            elif isinstance(item, QDMGraphicsEdge):
                selectedEdges.append(item.edge)

        #remove edges that are not connected to two need in the selection
        edgeToRemove = []

        for edge in selectedEdges:
            if edge.startSocket.id in selectedSockets and edge.endSocket.id in selectedSockets:
                pass
            else:
                if DEBUG : print("CLIPBOARD : serialize selected, adding edge to edged that need to be deleted", edge)
                edgeToRemove.append(edge)

        for edge in edgeToRemove:
            selectedEdges.remove(edge)

        if DEBUG :
            print("CLIPBOARD : DEBUG : Nodes ---", selectedNodes)
            print("CLIPBOARD : DEBUG : Edges ---", selectedEdges)
            print("CLIPBOARD : DEBUG : sockets ---", selectedSockets)

        edge_final = []
        for edge in selectedEdges:
            edge_final.append(edge.serialize())

        if delete :
            for node in selectedNodes:
                self.scene.getView().deleteSelected()
                self.scene.sceneHistory.storeHistory("Cut out Elements From Scene", setModified = True)

        return OrderedDict([
            ("nodes", selectedNodes),
            ("edges", edge_final),
            ]
        )

    def deserializeFromClipboard(self, data):

        if DEBUG : print("CLIPBOARD:: -deserializeFromClipboard:: Deserializing current Clipboard")

        hashmap = {}

        view = self.scene.getView()
        mouseScenePosition = view.lastSceneMousePosition
        minX, maxX, minY, maxY = 10000000,10000000,10000000,10000000

        for nodeData in data["nodes"]:
            x,y = nodeData["pos_x"], nodeData["pos_y"]
            if x < minX: minX = x
            if x > maxX: maxX = x
            if y < minY: minY = y
            if y > maxY: maxY = y

        maxX -= 180
        maxY += 100

        #currentViewCenterPos = view.mapToScene(view.rect().center())

        offsetX = (minX + maxX) / 2 - minY
        offsetY = (minY + maxY) / 2 - minY

        mouseX, mouseY = mouseScenePosition.x(), mouseScenePosition.y()

        createdNodes = []

        self.scene.setSilentSelectionEvents()
        self.scene.doDeselectionItems()

        for nodeData in data["nodes"]:
            newNode = self.scene.getNodeClassFromData(nodeData)(self.scene)
            newNode.deserialize(nodeData, hashmap, restoreId=False)

            createdNodes.append(newNode)

            posX, posY = newNode.pos.x(), newNode.pos.y()
            newX, newY = mouseY + posX - minX, mouseY + posY - minY

            newNode.setPosition(newX, newY)

            newNode.doSelect()

        if "edges" in data:
            for edgeData in data["edges"]:
                newEdge = Edge(self.scene)
                newEdge.deserialize(edgeData, hashmap, restoreId=False)

        self.scene.setSilentSelectionEvents(False)

        self.scene.sceneHistory.storeHistory("Pasted Elements in Scene", setModified=True)

        return createdNodes
