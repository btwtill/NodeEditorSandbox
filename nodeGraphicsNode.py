from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem
from PyQt5.QtCore import *

class QDMGraphicsNode(QGraphicsItem):
    def __init__(self, node, title = "nodeGraphicsItem",  parent = None):
        super().__init__(parent)

        self.titleColor = Qt.GlobalColor.white
        self.titleFont = QFont("Helvetica", 10)
        self.title = title


        self.initTitle()
        self.initUI()


    def initUI(self):
        pass

    def initTitle(self):
        self.titleItem = QGraphicsTextItem(self)
        self.titleItem.setDefaultTextColor(self.titleColor)
        self.titleItem.setFont(self.titleFont)
        self.titleItem.setPlainText(self.title)