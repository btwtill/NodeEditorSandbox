import os
from idlelib.run import Executive

from calculatorConf import *
from calculatorNodeBase import *
from PyQt5.QtCore import *

from utils import dumpException


@registerNode(OP_NODE_ADD)
class CalcNode_Add(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/add.png")
    opCode = OP_NODE_ADD
    opTitle = "Add"
    contentLabel = "+"
    contentLabelObjectName = "calcNodeBG"

@registerNode(OP_NODE_SUBSTRACT)
class CalcNode_Subtract(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/sub.png")
    opCode = OP_NODE_SUBSTRACT
    opTitle = "Sub"
    contentLabel = "-"
    contentLabelObjectName = "calcNodeBG"

@registerNode(OP_NODE_MULTIPLY)
class CalcNode_Multiply(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/mul.png")
    opCode = OP_NODE_MULTIPLY
    opTitle = "mult"
    contentLabel = "*"
    contentLabelObjectName = "calcNodeMul"

@registerNode(OP_NODE_DIVIDE)
class CalcNode_Divide(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/divide.png")
    opCode = OP_NODE_DIVIDE
    opTitle = "divide"
    contentLabel = "/"
    contentLabelObjectName = "calcNodeDiv"

class CalcInputContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit = QLineEdit("1", self)
        self.edit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.edit.setObjectName(self.node.contentLabelObjectName)

    def serialize(self):
        result = super().serialize()
        result['value'] = self.edit.text()
        return result

    def deserialize(self, data, hashmap = {}):
        result = super().deserialize(data, hashmap)
        try:
            value = data['value']
            self.edit.setText(value)
            return True & result
        except Executive as e: dumpException(e)

        return result

@registerNode(OP_NODE_INPUT)
class CalcNode_Input(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/in.png")
    opCode = OP_NODE_INPUT
    opTitle = "Input"
    contentLabelObjectName = "calcNodeInput"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])

    def initInnerClasses(self):
        self.content = CalcInputContent(self)
        self.grNode = CalcGraphicsNode(self)

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

class CalcOutputContent(QDMNodeContentWidget):
    def initUI(self):
        self.label = QLineEdit("42", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.label.setObjectName(self.node.contentLabelObjectName)

