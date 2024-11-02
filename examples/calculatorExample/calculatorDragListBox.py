from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

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
        self.addDragListItem("Input")
        self.addDragListItem("Output")
        self.addDragListItem("Add")
        self.addDragListItem("Substract")
        self.addDragListItem("Multiply")
        self.addDragListItem("Divide")

    def addDragListItem(self, name, icon=None, opCode=0):
        item = QListWidgetItem(name, self)
        pixmap = QPixmap(icon if icon is not None else ".")

        item.setIcon(QIcon(pixmap))
        item.setSizeHint(QSize(32, 32))

        item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsDragEnabled)

        item.setData(Qt.ItemDataRole.UserRole, pixmap)
        item.setData(Qt.ItemDataRole.UserRole + 1, opCode)