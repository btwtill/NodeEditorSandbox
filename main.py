import os
import sys
import inspect
import faulthandler
from PyQt5.QtWidgets import *
from nodeEditorWindow import NodeEditorWindow
from utils import loadStyleSheet

if __name__ == "__main__":

    faulthandler.enable()

    app = QApplication(sys.argv)

    nodeEditorWindow = NodeEditorWindow()
    modulePath = os.path.dirname(inspect.getfile(nodeEditorWindow.__class__))

    print(modulePath)

    loadStyleSheet(os.path.join(modulePath, 'qss/nodestyle.qss'))

    sys.exit(app.exec_())