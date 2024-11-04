import os
from examples.calculatorExample.calculatorConf import registerNode, OP_NODE_INPUT
from examples.calculatorExample.calculatorNodeBase import *
from PyQt5.QtCore import *
from utils import dumpException


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
        except Exception as e: dumpException(e)

        return result

@registerNode(OP_NODE_INPUT)
class CalcNode_Input(CalcNode):
    icon = os.path.join(os.path.dirname(__file__), "icons/in.png")
    opCode = OP_NODE_INPUT
    opTitle = "Input"
    contentLabelObjectName = "calcNodeInput"

    def __init__(self, scene):
        super().__init__(scene, inputs=[], outputs=[3])
        self.eval()

    def initInnerClasses(self):
        self.content = CalcInputContent(self)
        self.grNode = CalcGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)