import sys
from PyQt5.QtWidgets import *
from nodeEditorWindow import NodeEditorWindow
import faulthandler

if __name__ == "__main__":

    faulthandler.enable()

    app = QApplication(sys.argv)

    nodeEditorWindow = NodeEditorWindow()

    sys.exit(app.exec_())