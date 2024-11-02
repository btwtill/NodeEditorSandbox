from PyQt5.QtGui import *
from nodeEditorWidget import NodeEditorWidget
from PyQt5.QtCore import *
from calculatorConf import *
from nodeNode import Node
DEBUG = False

class CalculatorSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setTitle()

        self.scene.addHasBeenModifiedListener(self.setTitle)
        self.scene.addDragEnterListener(self.onDragEnter)
        self.scene.addDropListener(self.onDrop)

        self._closeEventListeners = []

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
            scenePosition = self.scene.grScene.views()[0].mapToScene(mousePosition)

            print("CALCULATORSUBWINOW::: -onDrop:: Mouse Position: ", mousePosition)
            print("CALCULATORSUBWINOW::: -onDrop:: Scene Position: ", scenePosition)

            node = Node(self.scene, text, inputs=[1, 1], outputs=[2])
            node.setPosition(scenePosition.x(), scenePosition.y())

            event.setDropAction(Qt.DropAction.MoveAction)
            event.accept()
        else:
            if DEBUG : print("CALCULATORSUBWINOW::: -onDrop:: Drop Ignored, not requested Format '%s' "
                             % LISTBOX_MIMETYPE)
            event.ignore()

    def closeEvent(self, event):
        for callback in self._closeEventListeners: callback(self, event)
