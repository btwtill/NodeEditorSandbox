from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from nodeNode import Node
from nodeGraphicsView import QDMGraphicsView
from nodeScene import Scene


class NodeEditorWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.initUI()

    def initUI(self):
        self.setGeometry(200, 200, 800, 600)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.scene = Scene()

        node = Node(self.scene, "New Amazing Node")

        self.view = QDMGraphicsView(self.scene.grScene, self)

        self.layout.addWidget(self.view)

        self.setWindowTitle('MNRB')
        self.show()
