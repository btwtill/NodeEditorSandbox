from PyQt5.QtWidgets import *
from nodeNode import Node
from nodeContentWidget import QDMNodeContentWidget
from nodeGraphicsNode import QDMGraphicsNode

class CalcNodeContent(QDMNodeContentWidget):
    def initUI(self):
        label = QLabel(self.node.contentLabel, self)
        label.setObjectName(self.node.contentLabelObjectName)

class CalcGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()

        self.width = 160
        self.height = 74
        self.edgeSize = 5
        self.titleHeight = 24
        self.padding = 8.0

class CalcNode(Node):
    icon = ""
    opCode = 0
    opTitle = "Undifined"
    contentLabel = ""
    contentLabelObjectName = "CalcNodeBG"

    def __init__(self, scene, inputs=[2, 2], outputs=[1]):
        super().__init__(scene, self.__class__.opTitle, inputs, outputs)

    def initInnerClasses(self):
        self.content = CalcNodeContent(self)
        self.grNode = CalcGraphicsNode(self)