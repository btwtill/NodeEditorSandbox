import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from utils import dumpException
from calculatorConf import *

DEBUG = False

class QDMDragListBox(QListWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):

        self.setIconSize(QSize(32, 32))
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setDragEnabled(True)

        self.addDragListItems()

    def addDragListItems(self):
        keys = list(CALC_NODES.keys())
        keys.sort()
        for key in keys:
            node = getClassFromOPCode(key)
            if DEBUG :
                print("DRAGLISTBOX:: -addDragListItems:: opTitle: ", node.opTitle)
                print("DRAGLISTBOX:: -addDragListItems:: opCode: ", node.opCode)
                print("DRAGLISTBOX:: -addDragListItems:: icon: ", node.icon)

            self.addDragListItem(node.opTitle, node.icon, node.opCode)

    def addDragListItem(self, name, icon=None, opCode=0):
        item = QListWidgetItem(name, self)

        if DEBUG : print("DRAGLISTBOX:: -addDragListItem:: icon = ", icon)
        pixmap = QPixmap(icon if icon is not None else ".")

        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)

        item.setData(Qt.ItemDataRole.UserRole, pixmap)
        item.setData(Qt.ItemDataRole.UserRole + 1, opCode)

    def startDrag(self, *args, **kwargs):
        try:
            item = self.currentItem()
            opCode = item.data(Qt.ItemDataRole.UserRole + 1)

            pixmap = QPixmap(item.data(Qt.ItemDataRole.UserRole))

            itemData = QByteArray()
            dataStream = QDataStream(itemData, QIODevice.OpenModeFlag.WriteOnly)
            dataStream << pixmap
            dataStream.writeInt(opCode)
            dataStream.writeQString(item.text())

            mimeData = QMimeData()
            mimeData.setData(LISTBOX_MIMETYPE, itemData)

            drag = QDrag(self)
            drag.setMimeData(mimeData)
            drag.setHotSpot(QPoint(pixmap.width() // 2, pixmap.height() // 2))
            drag.setPixmap(pixmap)

            drag.exec_(Qt.DropAction.MoveAction)

        except Exception as e:
            dumpException(e)
