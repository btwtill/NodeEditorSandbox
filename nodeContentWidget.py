from PyQt5.QtWidgets import QVBoxLayout, QLabel, QTextEdit, QWidget
from collections import OrderedDict
from nodeSerializable import Serializable

class QDMNodeContentWidget(QWidget, Serializable):
    def __init__(self, node , parent = None):
        super().__init__(parent)
        self.node = node

        self.initUI()

    def initUI(self):

        self.contentLayout = QVBoxLayout()
        self.contentLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.contentLayout)

        self.contentLabel = QLabel("Title")
        self.contentLayout.addWidget(self.contentLabel)
        self.contentLayout.addWidget(QDMTextEdit("Content"))

    def setEditingFlag(self, value):
        self.node.scene.grScene.views()[0].editingFlag = value

    def serialize(self):
        return OrderedDict([

        ])
    def deserialize(self, data, hashmap = {}):
        return False

class QDMTextEdit(QTextEdit):

    def focusInEvent(self, event):
        self.parentWidget().setEditingFlag(True)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.parentWidget().setEditingFlag(False)
        super().focusOutEvent(event)