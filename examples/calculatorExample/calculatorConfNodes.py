import os
from calculatorConf import *
from calculatorNodeBase import *

@registerNode(OP_NODE_ADD)
class CalcNode_Add(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/add.png")
    opCode = OP_NODE_ADD
    opTitle = "Add"
    contentLabel = "+"

@registerNode(OP_NODE_SUBSTRACT)
class CalcNode_Subtract(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/sub.png")
    opCode = OP_NODE_SUBSTRACT
    opTitle = "Sub"
    contentLabel = "-"

@registerNode(OP_NODE_MULTIPLY)
class CalcNode_Multiply(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/mul.png")
    opCode = OP_NODE_MULTIPLY
    opTitle = "mult"
    contentLabel = "*"

@registerNode(OP_NODE_DIVIDE)
class CalcNode_Divide(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/divide.png")
    opCode = OP_NODE_DIVIDE
    opTitle = "divide"
    contentLabel = "/"

@registerNode(OP_NODE_INPUT)
class CalcNode_Input(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/in.png")
    opCode = OP_NODE_INPUT
    opTitle = "Input"
    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])

@registerNode(OP_NODE_OUTPUT)
class CalcNode_Output(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/out.png")
    opCode = OP_NODE_OUTPUT
    opTitle = "Output"
    def __init__(self, scene):
        super().__init__(scene, inputs=[1], outputs=[])