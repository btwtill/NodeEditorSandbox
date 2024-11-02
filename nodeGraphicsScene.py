from PyQt5.QtCore import QLine, pyqtSignal
import math
from PyQt5.QtGui import QColor, QPen
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView


class QDMGraphicsScene(QGraphicsScene):
    itemsSelected = pyqtSignal()
    itemsDeselected = pyqtSignal()

    def __init__(self, scene, parent = None):
        super().__init__(parent)

        self.scene = scene

        #grid sizing
        self.gridSize = 20
        self.darkGridSquares = 5

        #scene Color and Canvas
        self.colorBackgroundcolor = QColor("#393939")
        self.lightBackgroundcolor = QColor("#2f2f2f")
        self.darkBackgroundcolor = QColor("#292929")

        self.penLight = QPen(self.lightBackgroundcolor)
        self.penLight.setWidth(1)

        self.penDark = QPen(self.darkBackgroundcolor)
        self.penDark.setWidth(2)

        self.setBackgroundBrush(self.colorBackgroundcolor)

    def dragMoveEvent(self, event):
        pass

    def setGrScene(self, width, height):
        self.setSceneRect(-width // 2, -height // 2, width, height)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)

        left = int(math.floor(rect.left()))
        right = int(math.ceil(rect.right()))
        top = int(math.floor(rect.top()))
        bottom = int(math.ceil(rect.bottom()))

        firstLeft = left - left % self.gridSize
        firstTop = top - top % self.gridSize

        lightLines, darkLines = [], []

        for x in range(firstLeft, right, self.gridSize):
           if x % (self.gridSize * self.darkGridSquares) !=0 :
               lightLines.append(QLine(x, top, x, bottom))
           else:
               darkLines.append(QLine(x, top, x, bottom))

        for y in range(firstTop, bottom, self.gridSize):
            if y % (self.gridSize * self.darkGridSquares) != 0 :
                lightLines.append(QLine(left, y, right, y))
            else:
                darkLines.append(QLine(left, y, right, y))

        painter.setPen(self.penLight)
        painter.drawLines(*lightLines)

        painter.setPen(self.penDark)
        painter.drawLines(*darkLines)