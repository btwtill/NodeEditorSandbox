import sys
from PyQt5.QtWidgets import *
from nodeEditorWidget import NodeEditorWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    nodeEditorWindow = NodeEditorWindow()

    sys.exit(app.exec_())