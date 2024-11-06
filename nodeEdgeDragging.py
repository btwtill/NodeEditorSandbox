from nodeEdge import EDGE_TYPE_BEZIER, Edge, EDGE_TYPE_DIRECT
from utils import dumpException
from nodeGraphicsSocket import QDMGraphicsSocket

DEBUG = False

class EdgeDragging:
    def __init__(self, grView):
        self.grView = grView

        self.dragEdge = None
        self.dragStartSocket = None

    def getEdgeClass(self):
        return self.grView.graphicsScene.scene.getEdgeClass()

    def edgeDragStart(self, item):
        try:
            if DEBUG: print("View : edgeDragStart : Start Dragging Edge")
            if DEBUG: print("View : edgeDragStart :  assign Start Socket ")
            # self.previousEdge = item.socket.edges

            self.dragStartSocket = item.socket

            # create drag edge
            self.dragEdge = self.getEdgeClass()(item.socket.node.scene, item.socket, None, EDGE_TYPE_BEZIER)

            if DEBUG: print("View : edgeDragStart : dragEdge", self.dragEdge)
        except Exception as e:
            dumpException(e)

    def edgeDragEnd(self, item):

        self.grView.resetMode()

        if DEBUG: print("View : edgeDragEnd : end Dragging Edge")
        self.dragEdge.remove(silent=True)
        self.dragEdge = None

        try:
            # check if item is a socket
            if isinstance(item, QDMGraphicsSocket):

                # check if the socket is not the starting socket
                if item.socket != self.dragStartSocket:

                    # removing old connections from new Socket
                    for socket in (item.socket, self.dragStartSocket):
                        if not socket.isMultiEdges:
                            if socket.isInput:
                                socket.removeAllEdges(silent=True)
                            else:
                                socket.removeAlleEdges(silent=False)

                    newEdge = self.getEdgeClass()(item.socket.node.scene, self.dragStartSocket, item.socket,
                                   edgeType=EDGE_TYPE_BEZIER)

                    if DEBUG: print("VIEW : edgeDragEnd : created new Edge: ", newEdge,
                                    "connecting", newEdge.startSocket, " <----> ", newEdge.endSocket)

                    for socket in [self.dragStartSocket, item.socket]:
                        socket.node.onEdgeConnectionChanged(newEdge)
                        if socket.isInput: socket.node.onInputChanged(socket)

                    item.socket.node.scene.sceneHistory.storeHistory("Create New Edge through dragging",
                                                                       setModified=True)
                    return True
        except Exception as e:
            dumpException(e)

        if DEBUG: print("View : edgeDragEnd - everything done.")
        return False

    def updateDestination(self, x, y):
        if self.dragEdge is not None and self.dragEdge.grEdge is not None:
            self.dragEdge.grEdge.setDestination(x, y)
            self.dragEdge.grEdge.update()

        else:
            print("GRAPHICSVIEW:: -MouseMoveEvent:: Want to update self.dragedge grEdge, but it is None")