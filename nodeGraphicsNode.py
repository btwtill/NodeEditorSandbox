from PyQt5.QtGui import QColor, QFont, QPainterPath, QPen, QBrush
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsTextItem, QGraphicsProxyWidget
from PyQt5.QtCore import *

from nodeGraphicsView import DEBUG


class QDMGraphicsNode(QGraphicsItem):
    def __init__(self, node,  parent = None):
        super().__init__(parent)

        self.node = node
        self.content = self.node.content

        self.hovered = False
        self._wasMoved = False
        self._lastSelectedState = False

        self.initSizes()
        self.initGraphicElements()
        self.initUI()


    @property
    def title(self): return self._title
    @title.setter
    def title(self, value):
        self._title = value
        self.titleItem.setPlainText(self._title)

    def initUI(self):
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)

        self.setAcceptHoverEvents(True)

        self.initTitle()
        self.title = self.node.title

        self.initContent()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        for node in self.scene().scene.nodes:
            if node.grNode.isSelected():
                node.updateConnectedEdges()

        self._wasMoved = True

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        if self._wasMoved:
            self._wasMoved = False
            self.node.scene.sceneHistory.storeHistory("Moved Node", setModified = True)

            self.node.scene.resetLastSelectedStates()
            self.doSelect()

            self.node.scene._lastSelectedItems = self.node.scene.getSelectedItems()

            return

        if DEBUG :
            print("GRAPHICSNODE:: -MouseReleaseEvent:: Before:: _lastSelectedState = ", self._lastSelectedState)
            print("GRAPHICSNODE:: -MouseReleaseEvent:: Before:: _lastSelectedItems = ",
                  self.node.scene._lastSelectedItems)
            print("GRAPHICSNODE:: -MouseReleaseEvent:: Before:: last Selected State was not Selected",
                  self._lastSelectedState != self.isSelected())
            print("GRAPHICSNODE:: -MouseReleaseEvent:: Before:: last Selected Items not Equal current Selection",
                  self.node.scene._lastSelectedItems != self.node.scene.getSelectedItems())

        if (self._lastSelectedState != self.isSelected() or
                self.node.scene._lastSelectedItems != self.node.scene.getSelectedItems()):
            self.node.scene.resetLastSelectedStates()
            self._lastSelectedState = self.isSelected()
            self.onSelected()

        if DEBUG:
            print("GRAPHICSNODE:: -MouseReleaseEvent:: After:: _lastSelectedState = ", self._lastSelectedState)
            print("GRAPHICSNODE:: -MouseReleaseEvent:: After:: _lastSelectedItems = ",
                  self.node.scene._lastSelectedItems)

    def boundingRect(self):
        return QRectF(
            0, 0, self.width, self.height
        ).normalized()

    def paint(self, painter, QStyle, widget = None):

        pathTitle = QPainterPath()
        pathTitle.setFillRule(Qt.FillRule.WindingFill)
        pathTitle.addRoundedRect(0, 0, self.width, self.titleHeight, self.edgeRoundness, self.edgeRoundness)
        pathTitle.addRect(0, self.titleHeight - self.edgeRoundness, self.edgeRoundness, self.edgeRoundness)
        pathTitle.addRect(self.width - self.edgeRoundness, self.titleHeight - self.edgeRoundness, self.edgeRoundness, self.edgeRoundness)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.brushTitle)
        painter.drawPath(pathTitle.simplified())

        pathContent = QPainterPath()
        pathContent.setFillRule(Qt.FillRule.WindingFill)
        pathContent.addRoundedRect(0,
                                   self.titleHeight,
                                   self.width,
                                   self.height - self.titleHeight,
                                   self.edgeRoundness,
                                   self.edgeRoundness)

        pathContent.addRect(0, self.titleHeight, self.edgeRoundness, self.edgeRoundness)
        pathContent.addRect(self.width - self.edgeRoundness, self.titleHeight, self.edgeRoundness, self.edgeRoundness)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(self.brushBackground)
        painter.drawPath(pathContent)

        pathOutline = QPainterPath()
        pathOutline.addRoundedRect(-1, -1, self.width, self.height, self.edgeRoundness, self.edgeRoundness)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        if self.hovered:
            painter.setPen(self.hoveredPen)
            painter.drawPath(pathOutline.simplified())
            painter.setPen(self.defaultPen)
            painter.drawPath(pathOutline.simplified())
        else:
            painter.setPen(self.defaultPen if not self.isSelected() else self.selectedPen)
            painter.drawPath(pathOutline.simplified())

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()

    def mouseDoubleClickEvent(self, event):
        self.node.onDoubleClicked(event)

    def onSelected(self):
        self.node.scene.grScene.itemsSelected.emit()

    def doSelect(self, newState = True):
        self.setSelected(newState)
        self.lastSelectedState = newState
        if newState: self.onSelected()

    def initSizes(self):
        self.width = 180
        self.height = 220
        self.edgeRoundness = 10
        self.edgePadding = 10
        self.titleHeight = 24
        self.titleHorizontalPadding = 20.0
        self.titleVerticalPadding = 4.0

    def initGraphicElements(self):
        self.titleColor = Qt.GlobalColor.white
        self.titleFont = QFont("Helvetica", 10)

        self.color = QColor("#7F000000")
        self.colorSelected = QColor("#FFFFA637")
        self.colorHoverd = QColor("#FFFFAA39")

        self.defaultPen = QPen(self.color)
        self.defaultPen.setWidthF(2.0)
        self.selectedPen = QPen(self.colorSelected)
        self.selectedPen.setWidthF(2.0)
        self.hoveredPen = QPen(self.colorHoverd)
        self.hoveredPen.setWidthF(4.0)

        self.brushTitle = QBrush(QColor("#FF313131"))
        self.brushBackground = QBrush(QColor("#E3212121"))

    def initTitle(self):
        self.titleItem = QGraphicsTextItem(self)
        self.titleItem.node = self.node
        self.titleItem.setDefaultTextColor(self.titleColor)
        self.titleItem.setFont(self.titleFont)
        self.titleItem.setPos(self.titleHorizontalPadding, 0)

    def initContent(self):
        self.grContent = QGraphicsProxyWidget(self)

        self.content.setGeometry(self.edgePadding,
                                 self.titleHeight + self.edgePadding,
                                 self.width - 2 * self.edgePadding,
                                 self.height - 2 * self.edgePadding - self.titleHeight)

        self.grContent.setWidget(self.content)


