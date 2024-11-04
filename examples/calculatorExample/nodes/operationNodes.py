import os
from examples.calculatorExample.calculatorNodeBase import CalcNode
from examples.calculatorExample.calculatorConf import registerNode, OP_NODE_ADD, OP_NODE_SUBSTRACT, OP_NODE_MULTIPLY, OP_NODE_DIVIDE

@registerNode(OP_NODE_ADD)
class CalcNode_Add(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/add.png")
    opCode = OP_NODE_ADD
    opTitle = "Add"
    contentLabel = "+"
    contentLabelObjectName = "calcNodeBG"

    def evaluationNodeImplementation(self):
        self.markInvalid(False)
        self.markDirty(False)
        return 123

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

