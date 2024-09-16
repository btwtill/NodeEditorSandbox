from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
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
        self.grScene = self.scene.grScene

        self.view = QDMGraphicsView(self.grScene, self)

        self.layout.addWidget(self.view)

        self.setWindowTitle('MNRB')
        self.show()

        self.addDebugContext()

    def addDebugContext(self):
        greenBrush = QBrush(Qt.green)
        outlinePen = QPen(Qt.black)
        outlinePen.setWidth(2)

        rect = self.grScene.addRect(-100, -100, 80, 100, outlinePen, greenBrush)
        rect.setFlag(QGraphicsItem.ItemIsMovable)

        text = self.grScene.addText("New Node editor Text")
        text.setFlag(QGraphicsItem.ItemIsMovable)
        text.setFlag(QGraphicsItem.ItemIsSelectable)
        text.setDefaultTextColor(QColor.fromRgbF(1.0, 1.0, 1.0))

        widget01 = QPushButton("Hello World")
        proxy1 = self.grScene.addWidget(widget01)
        proxy1.setFlag((QGraphicsItem.ItemIsMovable))
        proxy1.setPos(0, 30)

        widget02 = QTextEdit()
        proxy2 = self.grScene.addWidget(widget02)
        proxy2.setFlag(QGraphicsItem.ItemIsSelectable)
        proxy2.setPos(0, 50)

        line = self.grScene.addLine(-200, -100, 400, 200, outlinePen)
        line.setFlag(QGraphicsItem.ItemIsMovable)
        line.setFlag(QGraphicsItem.ItemIsSelectable)