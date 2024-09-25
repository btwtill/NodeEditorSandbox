from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsView

from nodeEdge import EDGE_TYPE_BEZIER, Edge
from nodeGraphicsEdge import QDMGraphicsEdge
from nodeGraphicsSocket import QDMGraphicsSocket

MODE_NOOP = 1
MODE_EDGEDRAG = 2

EDGE_START_DRAG_THRESHOLD = 10

DEBUG = True

class QDMGraphicsView(QGraphicsView):
    def __init__(self, graphicsScene, parent = None):
        super().__init__(parent)
        self.graphicsScene = graphicsScene

        self.initUI()

        self.mode = MODE_NOOP
        self.editingFlag = False

        self.setScene(self.graphicsScene)

        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]



    def initUI(self):
        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.HighQualityAntialiasing |
                            QPainter.TextAntialiasing |
                            QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonPressEvent(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonPressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonReleaseEvent(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)

    def middleMouseButtonPress(self, event):
        releaseEvent = QMouseEvent(QEvent.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.MouseButton.LeftButton, Qt.NoButton, event.modifiers())

        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton, event.buttons() | Qt.MouseButton.LeftButton, event.modifiers())
        super().mousePressEvent(fakeEvent)


    def middleMouseButtonRelease(self, event):
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton, event.buttons() | -Qt.MouseButton.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def leftMouseButtonPressEvent(self, event):

        item  = self.getItemAtClick(event)
        self.lastMouseButtonClickedPosition = self.mapToScene(event.pos())

        if DEBUG : print("LMB Click on", item, self.debugModifiers(event))

        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item == None:
            if event.modifiers() & Qt.Modifier.SHIFT:

                event.ignore()
                fakeEvent = QMouseEvent(QEvent.MouseButtonPress, event.localPos(), event.screenPos(), Qt.LeftButton, event.buttons() | Qt.LeftButton,
                                        event.modifiers() | Qt.ControlModifier)

                super().mousePressEvent(fakeEvent)
                return

        if type(item) == QDMGraphicsSocket:
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGEDRAG
                self.edgeDragStart(item)
                return

        if self.mode == MODE_EDGEDRAG:
            res = self.edgeDragEnd(item)
            if res: return

        super().mousePressEvent(event)

    def leftMouseButtonReleaseEvent(self, event):

        item = self.getItemAtClick(event)

        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item == None:
            if event.modifiers() & Qt.Modifier.SHIFT:
                event.ignore()
                fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.LeftButton, Qt.MouseButton.NoButton,
                                        event.modifiers() | Qt.ControlModifier)
                super().mouseReleaseEvent(fakeEvent)
                return

        if self.mode == MODE_EDGEDRAG:
            if self.distanceBetweenClickAndReleaseIsOff(event):
                res = self.edgeDragEnd(item)
                if res: return

        super().mouseReleaseEvent(event)

    def rightMouseButtonPressEvent(self, event):

        item = self.getItemAtClick(event)
        if DEBUG:
            if isinstance(item, QDMGraphicsEdge): print("RMB : DEBUG : ", item.edge, "connecting" , item.edge.startSocket, " <----> ", item.edge.endSocket)
            if type(item) == QDMGraphicsSocket: print("RMB : DEBUG : " , item.socket, "has Edge" , item.socket.edge)

            if item == None:
                print("View : DEBUG : Scene: ")
                print("     Nodes: ")
                for item in self.graphicsScene.scene.nodes:
                    print("         ", item)
                print("     Edges: ")
                for item in self.graphicsScene.scene.edges:
                    print("         ", item)
            elif type(item) == QDMGraphicsEdge:
                print("View : DEBUG : Edge : ")

        super().mousePressEvent(event)

    def rightMouseButtonReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):

        if self.mode == MODE_EDGEDRAG:
            pos = self.mapToScene(event.pos())
            self.dragEdge.grEdge.setDestination(pos.x(), pos.y())
            self.dragEdge.grEdge.update()

        super().mouseMoveEvent(event)

    def wheelEvent(self, event):
        zoomOutFactor = 1 / self.zoomInFactor

        if event.angleDelta().y() > 0:
            zoomFactor = self.zoomInFactor
            self.zoom += self.zoomStep
        else:
            zoomFactor = zoomOutFactor
            self.zoom -= self.zoomStep

        clamped = False
        if self.zoom < self.zoomRange[0]: self.zoom, clamped = self.zoomRange[0], True
        if self.zoom > self.zoomRange[1]: self.zoom, clamped = self.zoomRange[1], True

        if not clamped or self.zoomClamp is False:
            self.scale(zoomFactor, zoomFactor)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            if not self.editingFlag:
                self.deleteSelected()
            else:
                super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

    def deleteSelected(self):

        for item in self.graphicsScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, "node"):
                item.node.remove()



    def getItemAtClick(self, event):
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def edgeDragStart(self, item):

        if DEBUG: print("View : edgeDragStart : Start Dragging Edge")
        if DEBUG: print("View : edgeDragStart :  assign Start Socket ")
        self.previousEdge = item.socket.edge
        self.lastStartSocket = item.socket

        self.dragEdge = Edge(self.graphicsScene.scene, item.socket, None, EDGE_TYPE_BEZIER)

        if DEBUG : print("View : edgeDragStart : dragEdge", self.dragEdge)

    def edgeDragEnd(self, item):

        self.mode = MODE_NOOP

        if type(item) == QDMGraphicsSocket:
            if item.socket != self.lastStartSocket:
                if DEBUG : print("View : edgeDragEnd : previouse Edge" , self.previousEdge)
                if item.socket.hasEdge():
                    item.socket.edge.remove()

                if DEBUG : print("View : edgeDragEnd : assign End Socket", item.socket)

                if self.previousEdge is not None: self.previousEdge.remove()
                if DEBUG: print("View : EdgeDragEnd -- previous Edge Removed")

                self.dragEdge.startSocket = self.lastStartSocket
                self.dragEdge.endSocket = item.socket
                self.dragEdge.startSocket.setConnectedEdge(self.dragEdge)
                self.dragEdge.endSocket.setConnectedEdge(self.dragEdge)

                if DEBUG : print("View: EdgeDragEnd -- assigned Start & end Sockets to drag edge")

                self.dragEdge.updatePositions()
                return True

        if DEBUG : print( "View : edgeDragEnd -- about to set socket to previous edge", self.previousEdge)

        if DEBUG: print("View : edgeDragEnd : end Dragging Edge")
        self.dragEdge.remove()
        self.dragEdge = None

        if self.previousEdge is not None:
            self.previousEdge.startSocket.edge = self.previousEdge
            if DEBUG : print("Viewv : edgeDragEnd -- previous Start socket " , self.previousEdge.startSocket.edge)

        if DEBUG : print("View : edgeDragEnd - everithing done.")

        return False

    def distanceBetweenClickAndReleaseIsOff(self, event):

        newMouseButtonReleaseScenePosition = self.mapToScene(event.pos())
        mouseSceneDistance = newMouseButtonReleaseScenePosition - self.lastMouseButtonClickedPosition
        edgeDragThresholdSquared = EDGE_START_DRAG_THRESHOLD * EDGE_START_DRAG_THRESHOLD
        return (mouseSceneDistance.x() * mouseSceneDistance.x() + mouseSceneDistance.y() * mouseSceneDistance.y() > edgeDragThresholdSquared)

    def debugModifiers(self, event):
        out = "MODS: "
        if event.modifiers() & Qt.Modifier.SHIFT: out += " SHIFT"
        if event.modifiers() & Qt.Modifier.CTRL: out += " CTRL"
        if event.modifiers() & Qt.Modifier.ALT: out += " ALT"

        return out

