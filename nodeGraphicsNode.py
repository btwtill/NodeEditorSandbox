from PyQt5.QtGui import QColor, QFont, QPainterPath, QPen, QBrush
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsProxyWidget
from PyQt5.QtCore import *

class QDMGraphicsNode(QGraphicsItem):
    def __init__(self, node,  parent = None):
        super().__init__(parent)

        self.node = node
        self.content = self.node.content

        self.titleColor = Qt.GlobalColor.white
        self.titleFont = QFont("Helvetica", 10)


        self.width = 180
        self.height = 220
        self.edgeSize = 10
        self.titleHeight = 24
        self.padding = 20.0


        self.defaultPen = QPen(QColor("#7F000000"))
        self.selectedPen = QPen(QColor("#FFFFA637"))

        self.brushTitle = QBrush(QColor("#FF313131"))
        self.brushBackground = QBrush(QColor("#E3212121"))


        self.initTitle()
        self.title = self.node._title

        self.initSockets()

        self.initContent()

        self.initUI()

    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.titleItem.setPlainText(self._title)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        for node in self.scene().scene.nodes:
            if node.grNode.isSelected():
                node.updateConnectedEdges()

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def initTitle(self):
        self.titleItem = QGraphicsTextItem(self)
        self.titleItem.node = self.node
        self.titleItem.setDefaultTextColor(self.titleColor)
        self.titleItem.setFont(self.titleFont)
        self.titleItem.setPos(self.padding, 0)

    def initContent(self):
        self.grContent = QGraphicsProxyWidget(self)

        self.content.setGeometry(self.edgeSize,
                                 self.titleHeight + self.edgeSize,
                                 self.width - 2 * self.edgeSize,
                                 self.height - 2 * self.edgeSize - self.titleHeight)

        self.grContent.setWidget(self.content)

    def initSockets(self):
        pass

    def boundingRect(self):
        return QRectF(
            0, 0, self.width, self.height
        ).normalized()

    def paint(self, painter, QStyle, widget = None):

        pathTitle = QPainterPath()
        pathTitle.setFillRule(Qt.FillRule.WindingFill)
        pathTitle.addRoundedRect(0, 0, self.width, self.titleHeight, self.edgeSize, self.edgeSize)
        pathTitle.addRect(0, self.titleHeight - self.edgeSize, self.edgeSize, self.edgeSize)
        pathTitle.addRect(self.width - self.edgeSize, self.titleHeight - self.edgeSize, self.edgeSize, self.edgeSize)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.brushTitle)
        painter.drawPath(pathTitle.simplified())

        pathContent = QPainterPath()
        pathContent.setFillRule(Qt.FillRule.WindingFill)
        pathContent.addRoundedRect(0,
                                   self.titleHeight,
                                   self.width,
                                   self.height - self.titleHeight,
                                   self.edgeSize,
                                   self.edgeSize)

        pathContent.addRect(0, self.titleHeight, self.edgeSize, self.edgeSize)
        pathContent.addRect(self.width - self.edgeSize, self.titleHeight, self.edgeSize, self.edgeSize)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.brushBackground)
        painter.drawPath(pathContent)

        pathOutline = QPainterPath()
        pathOutline.addRoundedRect(0, 0, self.width, self.height, self.edgeSize, self.edgeSize)
        painter.setPen(self.defaultPen if not self.isSelected() else self.selectedPen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(pathOutline.simplified())


