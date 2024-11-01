from nodeEditorWidget import NodeEditorWidget
from PyQt5.QtCore import *

class CalculatorSubWindow(NodeEditorWidget):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.setTitle()

        self.scene.addHasBeenModifiedListener(self.setTitle)

        self._closeEventListeners = []

    def setTitle(self):
        self.setWindowTitle(self.getUserFriendlyFileName())

    def addCloseEventListener(self, callback):
        self._closeEventListeners.append(callback)

    def closeEvent(self, event):
        for callback in self._closeEventListeners: callback(self, event)