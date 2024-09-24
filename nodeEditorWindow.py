from idlelib.iomenu import encoding

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

from nodeEdge import Edge, EDGE_TYPE_DIRECT, EDGE_TYPE_BEZIER
from nodeNode import Node
from nodeGraphicsView import QDMGraphicsView
from nodeScene import Scene
from nodeSocket import Socket


class NodeEditorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        #load nodestyle from stylesheet
        self.styleSheetFileName = 'qss/nodestyle.qss'
        self.loadStyleSheet(self.styleSheetFileName)

        #initiate the Window
        self.initUI()

    def initUI(self):

        #set inital Window size
        self.setGeometry(200, 200, 800, 600)

        #create layout
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        #create Scene
        self.scene = Scene()

        # crate View
        self.view = QDMGraphicsView(self.scene.grScene, self)
        self.layout.addWidget(self.view)

        #set widget window title
        self.setWindowTitle('MNRB')

        self.addNodes()

       #display
        self.show()

    def loadStyleSheet(self, filename):
        print("loading Style")
        file = QFile(filename)
        file.open(QFile.ReadOnly | QFile.Text)

        stylesheet = file.readAll()

        QApplication.instance().setStyleSheet(str(stylesheet, encoding='utf-8'))

    def addNodes(self):

        # add Nodes
        node = Node(self.scene, "New Amazing Node", inputs=[1, 1, 1], outputs=[1])
        node2 = Node(self.scene, "Secon node", inputs=[2, 2], outputs=[3, 3, 3])
        node2.setPosition(-350, -200)

        edge1 = Edge(self.scene, node2.outputs[0], node.inputs[0], type=EDGE_TYPE_BEZIER)
        edge2 = Edge(self.scene, node2.outputs[2], node.inputs[1], type=EDGE_TYPE_BEZIER)
