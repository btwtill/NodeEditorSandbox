from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QGraphicsView, QApplication

from nodeEdge import EDGE_TYPE_BEZIER, Edge, EDGE_TYPE_DIRECT
from nodeGraphicsCutLine import QDMCutLine
from nodeGraphicsEdge import QDMGraphicsEdge
from nodeGraphicsSocket import QDMGraphicsSocket
from utils import dumpException

#Constants
MODE_NOOP = 1
MODE_EDGEDRAG = 2
MODE_EDGE_CUT = 3

EDGE_START_DRAG_THRESHOLD = 50

#Debugging Mode
DEBUG = False

class QDMGraphicsView(QGraphicsView):

    scenePosChanged = pyqtSignal(int, int)

    def __init__(self, graphicsScene, parent = None):
        super().__init__(parent)
        self.graphicsScene = graphicsScene

        self.initUI()

        self.setScene(self.graphicsScene)

        self.mode = MODE_NOOP
        self.editingFlag = False
        self.rubberBandDraggingRectangle = False

        self.lastSceneMousePosition = QPoint(0,0)

        self.zoomInFactor = 1.25
        self.zoomClamp = True
        self.zoom = 10
        self.zoomStep = 1
        self.zoomRange = [0, 10]

        #Empy Object that will be drawn on ctrl left Mouse button
        self.cutline = QDMCutLine()
        self.graphicsScene.addItem(self.cutline)

        self._dragEnterListeners = []
        self._dropListeners = []

    def initUI(self):
        #Set rendering Attributes
        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.HighQualityAntialiasing |
                            QPainter.TextAntialiasing |
                            QPainter.SmoothPixmapTransform)

        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        #Set Scrollbar Config
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        #set Default Drag Behaviour
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.RubberBandDrag)

        self.setAcceptDrops(True)

    def mousePressEvent(self, event):

        #trigger different mouse Events based on input event
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonPress(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonPressEvent(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonPressEvent(event)
        else:
            super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):

        #Trigger different Release Events based on input Release Event
        if event.button() == Qt.MouseButton.MiddleButton:
            self.middleMouseButtonRelease(event)
        elif event.button() == Qt.MouseButton.LeftButton:
            self.leftMouseButtonReleaseEvent(event)
        elif event.button() == Qt.MouseButton.RightButton:
            self.rightMouseButtonReleaseEvent(event)
        else:
            super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        scenePosition = self.mapToScene(event.pos())

        if self.mode == MODE_EDGEDRAG:
            if self.dragEdge is not None and self.dragEdge.grEdge is not None:
                self.dragEdge.grEdge.setDestination(scenePosition.x(), scenePosition.y())
                self.dragEdge.grEdge.update()

            else:
                print("GRAPHICSVIEW:: -MouseMoveEvent:: Want to update self.dragedge grEdge, but it is None")

        if self.mode == MODE_EDGE_CUT and self.cutline is not None:
            self.cutline.linePoints.append(scenePosition)
            self.cutline.update()

        self.lastSceneMousePosition = scenePosition

        self.scenePosChanged.emit(int(scenePosition.x()), int(scenePosition.y()))

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

        if event.key() == Qt.Key.Key_Backspace:
            if not self.editingFlag:
                self.deleteSelected()
            else:
                super().keyPressEvent(event)

        #elif event.key() == Qt.Key.Key_S and event.modifiers() & Qt.Modifier.CTRL:
         #   self.graphicsScene.scene.saveToFile("graph.json")

        #elif event.key() == Qt.Key.Key_L and event.modifiers() & Qt.Modifier.CTRL:
         #   self.graphicsScene.scene.loadFromFile("graph.json")

        #elif self.isZKeyOnlyPressed(event) or self.isZAndCtrlKeyPressed(event):
         #   self.graphicsScene.scene.sceneHistory.undo()

        #elif self.isZAndCtrlAndAltPressed(event):
         #   self.graphicsScene.scene.sceneHistory.redo()

        #elif event.key() == Qt.Key.Key_H:

         #   print( "View : DEBUG : History:    len(%d)" % len(self.graphicsScene.scene.sceneHistory.historyStack),
          #         " --- current step", self.graphicsScene.scene.sceneHistory.historyCurrentStep)
           # ix = 0
            #for item in self.graphicsScene.scene.sceneHistory.historyStack:
             #   print ("View : DEBUG : History: #", ix, "--", item['desc'], self.graphicsScene.scene.sceneHistory.historyStack)
              #  ix += 1

        else:
            super().keyPressEvent(event)

    def dragEnterEvent(self, event):
        for callback in self._dragEnterListeners: callback(event)

    def dropEvent(self, event):
        for callback in self._dropListeners: callback(event)

    def addDragEnterListener(self, callback):
        self._dragEnterListeners.append(callback)

    def addDropListener(self, callback):
        self._dropListeners.append(callback)

    def middleMouseButtonPress(self, event):

        # Debug Item under mouse
        item = self.getItemAtClick(event)

        if DEBUG:
            if isinstance(item, QDMGraphicsEdge): print("GRAPHICSVIEW:: -middleMouseButtonPress:: EDGE:: "
                                                        ,item.edge, "connecting", item.edge.startSocket,
                                                        " <----> ", item.edge.endSocket)
            if isinstance(item == QDMGraphicsSocket):
                print("GRAPHICSVIEW:: -middleMouseButtonPress:: SOCKET:: ", item.socket,
                                                      " has Edges: ", "None" if item.socket.edges == [] else "")
                if item.socket.edges:
                    for edge in item.socket.edges:
                        print("GRAPHICSVIEW:: -middleMouseButtonPress:: \t ", edge)

            if item == None:
                print("GRAPHICSVIEW:: -middleMouseButtonPress:: Scene: ")
                print("GRAPHICSVIEW:: -middleMouseButtonPress:: \tNodes: ")
                for item in self.graphicsScene.scene.nodes:
                    print("GRAPHICSVIEW:: -middleMouseButtonPress:: \t \t", item)
                print("GRAPHICSVIEW:: -middleMouseButtonPress:: \tEdges: ")
                for item in self.graphicsScene.scene.edges:
                    print("GRAPHICSVIEW:: -middleMouseButtonPress:: \t \t", item)

            if event.modifiers() & Qt.Modifier.CTRL:
                print("GRAPHICSVIEW:: -middleMouseButtonPress:: Graphic Items: ")
                for item in self.graphicsScene.items():
                    print("GRAPHICSVIEW:: -middleMouseButtonPress:: \t ", item)

        if DEBUG and item is None:
            print("GRAPHICSVIEW:: -middleMouseButtonPress SCENE::")
            print("GRAPHICSVIEW:: -middleMouseButtonPress NODES:: ")
            for node in self.graphicsScene.scene.nodes: print("GRAPHICSVIEW:: -middleMouseButtonPress ", node)
            print("GRAPHICSVIEW:: -middleMouseButtonPress EDGES:: ")
            for edge in self.graphicsScene.scene.edges: print("GRAPHICSVIEW:: -middleMouseButtonPress ",
                                                              edge, "\n\tgrEdge:: ",
                                                              edge.grEdge if edge.grEdge is not None else None)

        #fake event, Release Middle Mouse button or any mouse button
        releaseEvent = QMouseEvent(QEvent.Type.MouseButtonRelease, event.localPos(), event.screenPos(),
                                   Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, event.modifiers())
        super().mouseReleaseEvent(releaseEvent)
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        #imiting that it would be a left mouse button klick event
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton,
                                event.buttons() | Qt.MouseButton.LeftButton, event.modifiers())

        super().mousePressEvent(fakeEvent)

    def middleMouseButtonRelease(self, event):

        #Fake Left Mouse release
        fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(), Qt.MouseButton.LeftButton,
                                event.buttons() | -Qt.MouseButton.LeftButton, event.modifiers())
        super().mouseReleaseEvent(fakeEvent)

        #resetting the drag behaviour to enable drag selection
        self.setDragMode(QGraphicsView.RubberBandDrag)

    def leftMouseButtonPressEvent(self, event):

        #retrieve and store the active object that was clicked on
        item  = self.getItemAtClick(event)

        #store the position it was clicked on
        self.lastMouseButtonClickedPosition = self.mapToScene(event.pos())

        if DEBUG : print("LMB Click on", item, self.debugModifiers(event))

        #if the recrieved object is eigther type node, edge or none
        if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item == None:
            if event.modifiers() & Qt.Modifier.SHIFT:

                event.ignore()

                #when shift is beeing hold down simulate a ctrl key event and left mouse button klick
                fakeEvent = QMouseEvent(QEvent.Type.MouseButtonPress, event.localPos(), event.screenPos(),
                                        Qt.MouseButton.LeftButton, event.buttons() | Qt.MouseButton.LeftButton,
                                        event.modifiers() | Qt.Modifier.CTRL)

                super().mousePressEvent(fakeEvent)
                return

        #when the type is of socket start dragging an edge
        if isinstance(item, QDMGraphicsSocket):
            #only if not already in drag mode or cut mode
            if self.mode == MODE_NOOP:
                self.mode = MODE_EDGEDRAG
                self.edgeDragStart(item)
                return

        #if pressed and the dragging edge is currently beeing dragged end the edge dragging
        if self.mode == MODE_EDGEDRAG:
            res = self.edgeDragEnd(item)
            if res: return

        # if the press is to the void check for ctrl key  (edge cutting )
        if item is None:
            if event.modifiers() & Qt.Modifier.CTRL:
                self.mode = MODE_EDGE_CUT

                #fake release event
                fakeEvent = QMouseEvent(QEvent.Type.MouseButtonRelease, event.localPos(), event.screenPos(),
                                        Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton, event.modifiers())

                super().mouseReleaseEvent(fakeEvent)

                #indicate the edge cut mode with a different cursor
                QApplication.setOverrideCursor(Qt.CursorShape.CrossCursor)
                return
            else:
                self.rubberBandDraggingRectangle = True

        super().mousePressEvent(event)

    def leftMouseButtonReleaseEvent(self, event):


        try:
            # retrieve and store the item that was clicked on in the canvas
            item = self.getItemAtClick(event)

            #check if the clicked item was of type node, edge or none
            if hasattr(item, "node") or isinstance(item, QDMGraphicsEdge) or item == None:
                #activate the ctrl key behavior if the shift key is pressed
                if event.modifiers() & Qt.Modifier.SHIFT:

                    event.ignore()
                    fakeEvent = QMouseEvent(event.type(), event.localPos(), event.screenPos(),
                                            Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton,
                                            event.modifiers() | Qt.Modifier.CTRL)
                    super().mouseReleaseEvent(fakeEvent)
                    return

            # if there is an edge beeing dragged
            if self.mode == MODE_EDGEDRAG:

                #and the distance between the click and release checks out end the dragging
                if self.distanceBetweenClickAndReleaseIsOff(event):
                    res = self.edgeDragEnd(item)
                    if res: return

            if self.mode == MODE_EDGE_CUT:
                self.cutIntersectingEdges()
                self.cutline.linePoints = []
                self.cutline.update()
                QApplication.setOverrideCursor(Qt.CursorShape.ArrowCursor)
                self.mode = MODE_NOOP
                return

            if self.rubberBandDraggingRectangle:
                self.rubberBandDraggingRectangle = False

                currentSelectedItems = self.graphicsScene.selectedItems()

                if DEBUG:
                    print("GRAPHICSVIEW:: -LeftMouseButtonReleaseEvent:: Before:: lastSelectedItems = ",
                          self.graphicsScene.scene._lastSelectedItems)
                    print("GRAPHICSVIEW:: -LeftMouseButtonReleaseEvent:: Before:: Current SelectedItems = ",
                          currentSelectedItems)


                if currentSelectedItems != self.graphicsScene.scene._lastSelectedItems:
                    if currentSelectedItems == []:
                        self.graphicsScene.itemsDeselected.emit()
                    else:
                        self.graphicsScene.itemsSelected.emit()

                    self.graphicsScene.scene._lastSelectedItems = currentSelectedItems

                    if DEBUG:
                        print("GRAPHICSVIEW:: -LeftMouseButtonReleaseEvent:: After:: lastSelectedItems = ",
                              self.graphicsScene.scene._lastSelectedItems)
                        print("GRAPHICSVIEW:: -LeftMouseButtonReleaseEvent:: After:: Current SelectedItems = ",
                              currentSelectedItems)

                return

            if item is None:
                self.graphicsScene.itemsDeselected.emit()

        except Exception as e: dumpException(e)

        super().mouseReleaseEvent(event)

    def rightMouseButtonPressEvent(self, event):
        super().mousePressEvent(event)

    def rightMouseButtonReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

    def getItemAtClick(self, event):
        pos = event.pos()
        obj = self.itemAt(pos)
        return obj

    def edgeDragStart(self, item):
        try:
            if DEBUG: print("View : edgeDragStart : Start Dragging Edge")
            if DEBUG: print("View : edgeDragStart :  assign Start Socket ")
            #self.previousEdge = item.socket.edges

            self.dragStartSocket = item.socket

            #create drag edge
            self.dragEdge = Edge(self.graphicsScene.scene, item.socket, None, EDGE_TYPE_BEZIER)

            if DEBUG : print("View : edgeDragStart : dragEdge", self.dragEdge)
        except Exception as e: dumpException(e)

    def edgeDragEnd(self, item):

        self.mode = MODE_NOOP

        if DEBUG: print("View : edgeDragEnd : end Dragging Edge")
        self.dragEdge.remove(silent=True)
        self.dragEdge = None

        try:
            #check if item is a socket
            if isinstance(item, QDMGraphicsSocket):

                #check if the socket is not the starting socket
                if item.socket != self.dragStartSocket:

                    #removing old connections from new Socket
                    for socket in (item.socket, self.dragStartSocket):
                        if not socket.isMultiEdges:
                            if socket.isInput:
                                socket.removeAllEdges(silent=True)
                            else:
                                socket.removeAlleEdges(silent=False)

                    newEdge = Edge(self.graphicsScene.scene, self.dragStartSocket, item.socket, edgeType=EDGE_TYPE_BEZIER)

                    if DEBUG : print("VIEW : edgeDragEnd : created new Edge: ", newEdge,
                                     "connecting", newEdge.startSocket, " <----> ", newEdge.endSocket)

                    for socket in [self.dragStartSocket, item.socket]:
                        socket.node.onEdgeConnectionChanged(newEdge)
                        if socket.isInput: socket.node.onInputChanged(socket)

                    self.graphicsScene.scene.sceneHistory.storeHistory("Create New Edge through dragging", setModified=True)
                    return True
        except Exception as e: dumpException(e)

        if DEBUG : print("View : edgeDragEnd - everything done.")
        return False

    def distanceBetweenClickAndReleaseIsOff(self, event):

        #store current mouse position
        newMouseButtonReleaseScenePosition = self.mapToScene(event.pos())

        mouseSceneDistance = newMouseButtonReleaseScenePosition - self.lastMouseButtonClickedPosition

        edgeDragThresholdSquared = EDGE_START_DRAG_THRESHOLD * EDGE_START_DRAG_THRESHOLD

        return (mouseSceneDistance.x() * mouseSceneDistance.x() + mouseSceneDistance.y() *
                mouseSceneDistance.y() > edgeDragThresholdSquared)

    def isZKeyOnlyPressed(self, event):

        isZkeyPressed = event.key() == Qt.Key.Key_Z
        isCtrlModifierActive = event.modifiers() & Qt.Modifier.CTRL
        isAltModifierActive = event.modifiers() & Qt.Modifier.ALT
        isShiftModifierActive = event.modifiers() & Qt.Modifier.SHIFT

        return isZkeyPressed and not isAltModifierActive and not isCtrlModifierActive and not isShiftModifierActive

    def isZAndCtrlKeyPressed(self, event):

        isZKeyPressed = event.key() == Qt.Key.Key_Z
        isCtrlModifierActive = event.modifiers() & Qt.Modifier.CTRL
        isAltModifierActive = event.modifiers() & Qt.Modifier.ALT
        isShiftModifierActive = event.modifiers() & Qt.Modifier.SHIFT


        return  isZKeyPressed and isCtrlModifierActive and not isAltModifierActive and not isShiftModifierActive

    def isZAndCtrlAndAltPressed(self, event):

        isZKeyPressed = event.key() == Qt.Key.Key_Z
        isCtrlModifierActive = event.modifiers() & Qt.Modifier.CTRL
        isAltModifierActive = event.modifiers() & Qt.Modifier.ALT
        isShiftModifierActive = event.modifiers() & Qt.Modifier.SHIFT

        return isZKeyPressed and isCtrlModifierActive and isAltModifierActive and not isShiftModifierActive

    def cutIntersectingEdges(self):

        for ix in range(len(self.cutline.linePoints) - 1):
            p1 = self.cutline.linePoints[ix]
            p2 = self.cutline.linePoints[ix + 1]

            for edge in self.graphicsScene.scene.edges:
                if edge.grEdge.intersectsWith(p1, p2):
                    edge.remove()

        self.graphicsScene.scene.sceneHistory.storeHistory("Cut Edge", setModified=True)

    def deleteSelected(self):

        for item in self.graphicsScene.selectedItems():
            if isinstance(item, QDMGraphicsEdge):
                item.edge.remove()
            elif hasattr(item, "node"):
                item.node.remove()

        self.graphicsScene.scene.sceneHistory.storeHistory("Delete Selected", setModified = True)

    def debugModifiers(self, event):
        out = "MODS: "
        if event.modifiers() & Qt.Modifier.SHIFT: out += " SHIFT"
        if event.modifiers() & Qt.Modifier.CTRL: out += " CTRL"
        if event.modifiers() & Qt.Modifier.ALT: out += " ALT"

        return out

