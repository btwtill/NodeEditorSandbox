import os
from examples.calculatorExample.calculatorConf import *
from examples.calculatorExample.calculatorNodeBase import *
from PyQt5.QtCore import *
from utils import dumpException


class CalcOutputContent(QDMNodeContentWidget):
    def initUI(self):
        self.label = QLineEdit("42", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label.setObjectName(self.node.contentLabelObjectName)

@registerNode(OP_NODE_OUTPUT)
class CalcNode_Output(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/out.png")
    opCode = OP_NODE_OUTPUT
    opTitle = "Output"
    contentLabelObjectName = "calcNodeOutput"

    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])

    def initInnerClasses(self):
        self.content = CalcOutputContent(self)
        self.grNode = CalcGraphicsNode(self)

    def evaluationNodeImplementation(self):
        inputNode = self.getInput(0)
        if not inputNode:
            self.grNode.setToolTip("Input Not Connected")
            self.markInvalid()
            return

        value = inputNode.eval()

        if value is None:
            self.grNode.setToolTip("Input is NaN")
            self.markInvalid()
            return

        self.content.label.setText("%d" % value)

        self.markInvalid(False)
        self.markDirty(False)
        self.grNode.setToolTip("")

        return value
