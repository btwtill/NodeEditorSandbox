import os

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from nodeNode import Node
from nodeContentWidget import QDMNodeContentWidget
from nodeGraphicsNode import QDMGraphicsNode
from nodeSocket import LEFT_CENTER, RIGHT_CENTER
from utils import dumpException

DEBUG = False

class CalcNodeContent(QDMNodeContentWidget):
    def initUI(self):
        label = QLabel(self.node.contentLabel, self)
        label.setObjectName(self.node.contentLabelObjectName)

class CalcGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()

        self.width = 160
        self.height = 74
        self.edgeRoundness = 5
        self.edgePadding = 0
        self.titleHeight = 24
        self.titleHorizontalPadding = 8.0
        self.titleVerticalPadding = 10.0

    def initGraphicElements(self):
        super().initGraphicElements()
        self.icons = QImage(os.path.join(os.path.dirname(__file__), "icons/status_icons.png"))

    def paint(self, painter, QStyle, widget=None):
        super().paint(painter, QStyle, widget)

        offset = 24.0
        if self.node.isDirty(): offset = 0.0
        if self.node.isInvalid(): offset = 48.0

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.),
            self.icons,
            QRectF(offset, 0, 24.0, 24.0)
        )

class CalcNode(Node):
    icon = ""
    opCode = 0
    opTitle = "Undifined"
    contentLabel = ""
    contentLabelObjectName = "CalcNodeBG"

    def __init__(self, scene, inputs=[2, 2], outputs=[1]):
        super().__init__(scene, self.__class__.opTitle, inputs, outputs)

        self.value = None

        self.markDirty()

    def initInnerClasses(self):
        self.content = CalcNodeContent(self)
        self.grNode = CalcGraphicsNode(self)

    def initSettings(self):
        super().initSettings()

        self.inputSocketPosition = LEFT_CENTER
        self.outputSocketPosition = RIGHT_CENTER

    def evalOperation(self, input1, input2):
        return 123

    def evaluationNodeImplementation(self):
        input1 = self.getInput(0)
        input2 = self.getInput(1)

        if  input1 is None or input2 is None:
            self.markDirty()
            self.markDescendeantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        else:
            value = self.evalOperation(input1.eval(), input2.eval())
            self.value = value
            self.markDirty(False)
            self.markInvalid(False)
            self.grNode.setToolTip("")

            self.markDescendeantsDirty()
            self.evalChildren()

            return value

    def eval(self):
        if not self.isDirty() and not self.isInvalid():
            if DEBUG : print(" _> returning cached %s value:" % self.__class__.__name__, self.value)
            return self.value

        try:
            value = self.evaluationNodeImplementation()

            return value

        except ValueError as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            self.markDescendeantsDirty()
        except Exception as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            dumpException(e)

    def onInputChanged(self, newEdge):
        if DEBUG : print("%s:: onInputChange:: _InputChanged" % __class__.__name__)
        self.markDirty()
        self.eval()

    def serialize(self):
        res = super().serialize()
        res['opCode'] = self.__class__.opCode
        return res
    
    def deserialize(self, data, hashmap = {}, restoreId = True):
        result = super().deserialize(data, hashmap, restoreId)
        if DEBUG : print("CALCULATORNODEBASE:: --deserialize:: CalcNode '%s' " % self.__class__.__name__, " Result: ", result)
        return result