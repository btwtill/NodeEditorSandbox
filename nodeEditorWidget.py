from idlelib.iomenu import encoding
from plistlib import InvalidFileException

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
import os

from nodeEdge import Edge, EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER
from nodeNode import Node
from nodeGraphicsView import QDMGraphicsView
from nodeScene import Scene, InvalidFile
from nodeSocket import Socket


class NodeEditorWidget(QWidget):
    SceneClass = Scene

    def __init__(self, parent=None):
        super().__init__(parent)

        self.filename = None

        #initiate the Window
        self.initUI()

    def initUI(self):

        #create layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        #create Scene
        self.scene = self.__class__.SceneClass()

        # crate View
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)

    def isFileNameSet(self):
        return self.filename is not None

    def isModified(self):
        return self.scene.hasBeenModified

    def getUserFriendlyFileName(self):
        name = os.path.basename(self.filename) if self.isFileNameSet() else "New Graph"

        return name + ('*' if self.isModified() else '')

    def fileLoad(self, fileName):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        try:
            self.scene.loadFromFile(fileName)
            self.filename = fileName
            self.scene.sceneHistory.clear()
            self.scene.sceneHistory.storeInitialHistoryStamp()

            return True
        except InvalidFile as e:
            print(e)
            QApplication.restoreOverrideCursor()
            QMessageBox.warning(self, "Error loading %s" % os.path.basename(fileName), str(e))

            return False
        finally:
            QApplication.restoreOverrideCursor()

        return False

    def fileSave(self, filename=None):
        if filename is not None: self.filename = filename
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.scene.saveToFile(self.filename)
        QApplication.restoreOverrideCursor()

        return True

    def fileNew(self):
        self.scene.clearScene()
        self.filename = None
        self.scene.sceneHistory.clear()
        self.scene.sceneHistory.storeInitialHistoryStamp()

    def getSelectedItems(self):
        return self.scene.getSelectedItems()

    def hasSelectedItems(self):
        return self.getSelectedItems() != []

    def canUndo(self):
        return self.scene.sceneHistory.canUndo()

    def canRedo(self):
        return self.scene.sceneHistory.canRedo()

    def addNodes(self):

        # add Nodes
        node = Node(self.scene, "New Amazing Node", inputs=[1, 1, 1], outputs=[1])
        node2 = Node(self.scene, "Second node", inputs=[2, 2], outputs=[3, 3, 3])
        node2.setPosition(-350, -200)
        node3  = Node(self.scene, "Third Node", inputs = [1, 1, 1, 1], outputs=[1, 1, 1])
        node3.setPosition(100, -100)

        edge1 = Edge(self.scene, node2.outputs[0], node.inputs[0], edgeType=EDGE_TYPE_BEZIER)
        edge2 = Edge(self.scene, node2.outputs[2], node.inputs[1], edgeType=EDGE_TYPE_BEZIER)
        edge3 = Edge(self.scene, node.outputs[0], node3.inputs[1], edgeType=EDGE_TYPE_BEZIER)

        self.scene.sceneHistory.storeInitialHistoryStamp()

    def addCustomNode(self):
        from nodeContentWidget import QDMNodeContentWidget
        from nodeSerializable import Serializable

        class NNodeContent(QLabel):
            def __init__(self,node, parent = None):
                super().__init__("foobar")
                self.node = node
                self.setParent(parent)

        class NNode(Node):
            NodeContentClass = NNodeContent

        self.scnee.setNodeClassSelector(lambda data: NNode)
        node = NNode(self.scene, "A Custom Node 1", inputs=[0, 1, 2])

        print("NODEEDITORWIDGET:: -addCustomNode:: Node Content:: ", node.content)