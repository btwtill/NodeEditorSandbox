from PyQt5.QtGui import *
from select import select
from PyQt5.QtCore import *
from nodeNode import Node
from nodeEdge import EDGE_TYPE_BEZIER, EDGE_TYPE_DIRECT
from nodeEditorWidget import NodeEditorWidget
from calculatorConf import *
from examples.calculatorExample.calculatorConf import CALC_NODES, getClassFromOPCode
from calculatorNodeBase import *
from utils import dumpException

DEBUG = False

class CalculatorSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setTitle()

        self.initNewNodeActions()

        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)

        self.scene.setNodeClassSelector(self.getNodeClassFromData)

        self._closeEventListeners = []

    def fileLoad(self, fileName):
        if super().fileLoad(fileName):
            for node in self.scene.nodes:
                if node.__class__.__name__ == "CalcNode_Output":
                    node.eval()
            return True
        else:
            return False

    def getNodeClassFromData(self, data):
        if DEBUG:
            print("CALCULATORSUBWINDOW:: -getNodeClassFromData:: data: ", data)
            print("CALCULATORSUBWINDOW:: -getNodeClassFromData:: opCode in data: ", ('opCode' in data))
        if 'opCode' not in data: return Node
        return getClassFromOPCode(data['opCode'])

    def initNewNodeActions(self):
        self.nodeActions = {}
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys:
            node = CALC_NODES[key]
            self.nodeActions[node.opCode] = QAction(QIcon(node.icon), node.opTitle)
            self.nodeActions[node.opCode].setData(node.opCode)

    def initNodesContextMenu(self):
        contextMenu = QMenu()
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys: contextMenu.addAction(self.nodeActions[key])
        return contextMenu

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFileName())

    def addCloseEventListener(self, callback):
        self._closeEventListeners.append(callback)

    def onDragEnter(self, event):
        if DEBUG :
            print("CALCULATORSUBWINOW::: -onDragEnter:: DragEntered")
            print("CALCULATORSUBWINOW::: -onDragEnter:: event MimeData Text : '%s'" % event.mimeData().text())

        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            event.acceptProposedAction()
        else:
            if DEBUG : print("CALCULATORSUBWINOW::: -onDragEnter:: denied drag enter event")
            event.setAccepted(False)

    def onDrop(self, event):
        if DEBUG :
            print("CALCULATORSUBWINOW::: -onDrop:: Dropped")
            print("CALCULATORSUBWINOW::: -onDrop:: event MimeData text: '%s'" % event.mimeData().text())

        if event.mimeData().hasFormat(LISTBOX_MIMETYPE):
            eventData =event.mimeData().data(LISTBOX_MIMETYPE)
            dataStream = QDataStream(eventData, QIODevice.OpenModeFlag.ReadOnly)
            pixmap = QPixmap()
            dataStream >> pixmap
            opCode = dataStream.readInt()
            text = dataStream.readQString()

            if DEBUG : print("CALCULATORSUBWINOW::: -onDrop:: received: [%d] '%s'" % (opCode, text))

            mousePosition = event.pos()
            scenePosition = self.scene.getView().mapToScene(mousePosition)

            if DEBUG:
                print("CALCULATORSUBWINOW::: -onDrop:: Mouse Position: ", mousePosition)
                print("CALCULATORSUBWINOW::: -onDrop:: Scene Position: ", scenePosition)

            try:
                node = getClassFromOPCode(opCode)(self.scene)
                node.setPosition(scenePosition.x(), scenePosition.y())
                self.scene.sceneHistory.storeHistory("Created node %s" % node.__class__.__name__)
            except Exception as e: dumpException(e)

            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
        else:
            if DEBUG : print("CALCULATORSUBWINOW::: -onDrop:: Drop Ignored, not requested Format '%s' "
                             % LISTBOX_MIMETYPE)
            event.ignore()

    def closeEvent(self, event):
        for callback in self._closeEventListeners: callback(self, event)

    def handleNodeContextMenu(self, event):
        if DEBUG: print("CALCULATORSUBWINDOW:: -handleNodeContextMenu:: DisplayWindow NodeContextMenu")

        contextMenu = QMenu(self)

        markDirtyAction = contextMenu.addAction("Mark Dirty")
        markDirtyDescendantsAction = contextMenu.addAction("MarkDescendants Dirty")
        markInvalidAction = contextMenu.addAction("Mark Invalid")
        unmarkInvalidAction = contextMenu.addAction("Unmark Invalid")
        evalAction = contextMenu.addAction("Eval")
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())

        if type(item) == QGraphicsProxyWidget:
            selected = item.widget().node

        if hasattr(item, 'node'):
            selected = item.node
        if hasattr(item, 'socket'):
            selected = item.socket.node

        if DEBUG: print("CALCULATORSUBWINDOW:: -handleNodeContextMenu:: Got Item: ", selected)

        if selected and action == markDirtyAction: selected.markDirty()
        if selected and action == markInvalidAction: selected.markInvalid()
        if selected and action == unmarkInvalidAction: selected.markInvalid(False)
        if selected and action == markDirtyDescendantsAction: selected.markDescendeantsDirty()

        if selected and action == evalAction:
            value = selected.eval()

            if DEBUG : print("CALCULATORSUBWINDOW:: -handleNodeContextMenu:: evalAction: Evaluated: ", value)

    def handleEdgeContextMenu(self, event):
        if DEBUG: print("CALCULATORSUBWINDOW:: -handleEdgeContextMenu:: DisplayWindow EdgeContextMenu")

        contextMenu = QMenu(self)
        bezierAction = contextMenu.addAction("Bezier Edge")
        directAction = contextMenu.addAction("Direct Edge")
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))

        selected = None
        item = self.scene.getItemAt(event.pos())

        if hasattr(item, 'edge'):
            selected = item.edge

        if selected and action == bezierAction: selected.edgeType = EDGE_TYPE_BEZIER
        if selected and action == directAction: selected.edgeType = EDGE_TYPE_DIRECT

    def handleNewNodeContextMenu(self, event):
        if DEBUG: print("CALCULATORSUBWINDOW:: -handleNewNodeContextMenu:: DisplayWindow NewNodeContextMenu ")

        contextMenu = self.initNodesContextMenu()
        action = contextMenu.exec_(self.mapToGlobal(event.pos()))

        if DEBUG : print("CALCULATORSUBWINDOW:: -handleNewNodeContextMenu:: action: ", action)
        if action is not None:
            newCalcNode =getClassFromOPCode(action.data())(self.scene)
            scenePosition = self.scene.getView().mapToScene(event.pos())
            newCalcNode.setPosition(scenePosition.x(), scenePosition.y())

    def contextMenuEvent(self, event):
        try:
            item = self.scene.getItemAt(event.pos())
            if DEBUG : print("CALCULATORSUBWINDOW:: -contextMenuEvent:: Item: ", item)

            if type(item) == QGraphicsProxyWidget:
                item = item.widget()

            if hasattr(item, 'node') or hasattr(item, 'socket'):
                self.handleNodeContextMenu(event)
            elif hasattr(item, 'edge'):
                self.handleEdgeContextMenu(event)
            else:
                self.handleNewNodeContextMenu(event)

            return super().contextMenuEvent(event)
        except Exception as e: dumpException(e)